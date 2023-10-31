from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator as _TokenAuthenticator


class TokenAuthenticator(_TokenAuthenticator):
    def __init__(self, token: str):
        super().__init__(token, auth_method=None, auth_header="Api-Token")

    @property
    def token(self) -> str:
        return self._token
