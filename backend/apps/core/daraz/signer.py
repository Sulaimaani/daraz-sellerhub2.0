import hmac
import hashlib

def generate_signature(api_path, params, secret):
    # Sort params by key
    sorted_params = sorted(params.items())
    
    # Concatenate api_path and sorted key-value pairs without spaces
    sign_string = api_path
    for key, value in sorted_params:
        if key != 'sign':  # Exclude 'sign' if it's already there
            sign_string += f"{key}{value}"
            
    # HMAC SHA256 using Daraz App Secret
    signature = hmac.new(
        secret.encode("utf-8"),
        sign_string.encode("utf-8"),
        hashlib.sha256
    ).hexdigest().upper()
    
    return signature
