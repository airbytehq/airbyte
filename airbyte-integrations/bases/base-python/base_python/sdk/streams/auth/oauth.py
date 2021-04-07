from typing import Mapping, Any

from base_python.sdk.streams.auth.core import HttpAuthenticator


class Oauth2Authenticator(HttpAuthenticator):
    def get_auth_header(self) -> Mapping[str, Any]:
        # TODO
        raise NotImplementedError
