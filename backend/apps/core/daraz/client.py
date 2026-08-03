import time
import requests
import logging
from urllib.parse import urlencode
from django.conf import settings
from django.utils import timezone
from .signer import generate_signature

logger = logging.getLogger(__name__)

class DarazAuthError(Exception):
    def __init__(self, code, message):
        super().__init__(f"Auth Error [{code}]: {message}")
        self.code = code
        self.message = message

class DarazRateLimitError(Exception):
    def __init__(self, code, message):
        super().__init__(f"Rate Limit Error [{code}]: {message}")
        self.code = code
        self.message = message

class DarazApiError(Exception):
    def __init__(self, code, message):
        super().__init__(f"API Error [{code}]: {message}")
        self.code = code
        self.message = message


class DarazClient:
    API_URL = "https://api.daraz.pk/rest"

    def __init__(self, store=None):
        self.store = store
        self.app_key = settings.DARAZ_APP_KEY
        self.app_secret = settings.DARAZ_APP_SECRET
        self.mock_mode = settings.DARAZ_MOCK

    def call(self, api_path, params=None, method="GET", access_token=None):
        params = params or {}
        
        # Base params required by Daraz
        base_params = {
            "app_key": self.app_key,
            "timestamp": str(int(timezone.now().timestamp() * 1000)),
            "sign_method": "sha256",
        }
        if access_token:
            base_params["access_token"] = access_token
            
        full_params = {**base_params, **params}
        
        # Generate signature
        full_params["sign"] = generate_signature(api_path, full_params, self.app_secret)
        
        url = f"{self.API_URL}{api_path}"
        
        # Mock mode routing
        if self.mock_mode:
            return self._mock_call(api_path, full_params)
            
        # Exponential backoff retry logic (max 5 attempts)
        max_attempts = 5
        attempt = 0
        backoff = 1
        
        while attempt < max_attempts:
            attempt += 1
            start_time = time.time()
            
            try:
                if method == "GET":
                    response = requests.get(url, params=full_params, timeout=10)
                else:
                    # For POST, Daraz typically expects params in the URL as well, or body? 
                    # Documentation varies, usually they accept x-www-form-urlencoded body for POST.
                    # We'll use params in URL and empty body for standard POSTs unless specified.
                    response = requests.post(url, params=full_params, timeout=10)
                
                http_status = response.status_code
                duration_ms = int((time.time() - start_time) * 1000)
                
                # Log to DB
                self._log_call(api_path, full_params, response.text, http_status, duration_ms)
                
                if http_status in (429, 500, 502, 503, 504):
                    if attempt == max_attempts:
                        raise DarazRateLimitError(str(http_status), f"Max retries reached on {http_status}")
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                    
                data = response.json()
                
                # Check for Daraz application-level errors
                if "code" in data and str(data["code"]) != "0":
                    self._handle_api_error(data)
                    
                return data

            except requests.RequestException as e:
                duration_ms = int((time.time() - start_time) * 1000)
                self._log_call(api_path, full_params, str(e), None, duration_ms)
                
                if attempt == max_attempts:
                    raise DarazApiError("NETWORK_ERROR", str(e))
                time.sleep(backoff)
                backoff *= 2

    def _handle_api_error(self, data):
        code = str(data.get("code", ""))
        message = data.get("message", "Unknown error")
        if code in ["IllegalAccessToken", "InvalidAccessToken", "AccessTokenExpired"]:
            raise DarazAuthError(code, message)
        elif code in ["FlowLimitError", "SystemBusy"]:
            raise DarazRateLimitError(code, message)
        else:
            raise DarazApiError(code, message)

    def _log_call(self, api_path, params, response_text, http_status, duration_ms):
        from apps.stores.models import ApiCallLog
        
        # Redact secrets
        safe_params = params.copy()
        if "access_token" in safe_params:
            safe_params["access_token"] = "***"
        if "app_key" in safe_params:
            safe_params["app_key"] = "***"
        if "sign" in safe_params:
            safe_params["sign"] = "***"
            
        # Truncate response
        snippet = response_text[:1000] if response_text else ""
        
        # Parse error code if JSON
        error_code = ""
        try:
            import json
            j = json.loads(response_text)
            if "code" in j and str(j["code"]) != "0":
                error_code = str(j["code"])
        except:
            pass
            
        try:
            ApiCallLog.objects.create(
                store=self.store,
                api_path=api_path,
                http_status=http_status,
                duration_ms=duration_ms,
                request_params=safe_params,
                response_snippet=snippet,
                error_code=error_code
            )
        except Exception as e:
            logger.error(f"Failed to log API call: {e}")

    def _mock_call(self, api_path, params):
        from .mock.generator import route_mock_call
        data = route_mock_call(api_path, params)
        self._log_call(api_path, params, str(data), 200, 50)
        
        if "code" in data and str(data["code"]) != "0":
            self._handle_api_error(data)
            
        return data

    def create_token(self, code):
        return self.call("/auth/token/create", {"code": code}, method="POST")

    def refresh_token(self, refresh_token):
        return self.call("/auth/token/refresh", {"refresh_token": refresh_token}, method="POST")

    def get_seller(self, access_token):
        return self.call("/seller/get", method="GET", access_token=access_token)
