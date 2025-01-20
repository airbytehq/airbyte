import base64

def generate_access_token(service_secret: str, licence_key: str) -> str:
    input_bytes = f"{service_secret}:{licence_key}".encode("utf-8")
    base64_bytes = base64.b64encode(input_bytes)
    base64_string = base64_bytes.decode('utf-8')
    return f"ESA {base64_string}" # For RakutenAPI, return in the format 'ESA {base64_string}'
