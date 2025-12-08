from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from typing import Tuple
from base64 import b64encode

class Base64HttpAuthenticator(TokenAuthenticator):
    """
    :auth - tuple with (api_key as username, password string). Password should be empty.
    https://developer.close.com/#authentication
    """

    def __init__(self, auth: Tuple[str, str], auth_method: str = "Basic"):
        auth_string = f"{auth[0]}:{auth[1]}".encode("latin1")
        b64_encoded = b64encode(auth_string).decode("ascii")
        super().__init__(token=b64_encoded, auth_method=auth_method)
