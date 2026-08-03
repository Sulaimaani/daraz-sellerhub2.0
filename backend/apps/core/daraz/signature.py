import hashlib
import hmac


def sign_request(secret: str, api_path: str, parameters: dict) -> str:
    """
    Signs a Daraz API request.
    1. Sort all parameters (including app_key, timestamp, sign_method, access_token) alphabetically by key.
    2. Concatenate the sorted parameters into a string: k1v1k2v2...
    3. Prepend the api_path to the concatenated string.
    4. Calculate the HMAC-SHA256 signature using the app secret.
    5. Convert the signature to uppercase hex string.
    """
    sorted_keys = sorted(parameters.keys())
    concatenated = api_path
    for key in sorted_keys:
        concatenated += f"{key}{parameters[key]}"

    signature = (
        hmac.new(secret.encode("utf-8"), concatenated.encode("utf-8"), hashlib.sha256)
        .hexdigest()
        .upper()
    )

    return signature
