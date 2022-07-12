import requests


class HTTPApiKeyHeaderAuth(requests.auth.AuthBase):
    """Attaches Access API Key as a HTTP header to the given Request object."""

    def __init__(self, api_key_header: str, access_key: str):
        self.access_key = access_key
        self.api_key_header = api_key_header

    def __call__(self, r: requests.Request):
        r.headers[self.api_key_header] = self.access_key
        return r
