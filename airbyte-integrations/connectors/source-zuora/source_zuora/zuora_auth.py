#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from typing import Any, Dict, Mapping, Union

from airbyte_cdk.sources.streams.http.requests_native_auth.oauth import Oauth2Authenticator
from airbyte_cdk.sources.streams.http.requests_native_auth.token import TokenAuthenticator

from .zuora_endpoint import get_url_base


class AuthNotImplemented(Exception):
    def __init__(self, auth_option: str):
        self.message = f"The {auth_option} authorization method is not implemented"
        super().__init__(self.message)


class ZuoraCredsAuthenticator(Oauth2Authenticator):
    """
    For regular authentication method with Client ID & Client Secret, we need to obtain the access_token.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_refresh_request_body(self) -> Mapping[str, Any]:
        payload = super().get_refresh_request_body()
        payload["grant_type"] = "client_credentials"
        payload.pop("refresh_token")  # Zuora doesn't have Refresh Token parameter
        return payload


class ZuoraAuthenticator:
    """
    Zuora Authenticator base class, contains methods to authenticate the user using:
     - `oauth2.0` option with `access_token` auto-generated using OAuth 2.0 Flow.
     - `auth_app_creds` option with {client_id, client_secret} from OAuth application. (default)
    """

    def __init__(self, config: Dict):
        self.config = config

    @property
    def url_base(self) -> str:
        return get_url_base(self.config["tenant_endpoint"])

    def get_auth(self) -> Union[ZuoraCredsAuthenticator, TokenAuthenticator]:
        auth_method = self.config["authorization"]
        auth_option = auth_method.get("authorization")

        if auth_option == "oauth2.0":
            return TokenAuthenticator(token=auth_method["access_token"])
        elif auth_option == "auth_app_creds":
            return ZuoraCredsAuthenticator(
                token_refresh_endpoint=f"{self.url_base}/oauth/token",
                client_id=auth_method["client_id"],
                client_secret=auth_method["client_secret"],
                refresh_token=None,  # Zuora doesn't have Refresh Token parameter
            )
        else:
            raise AuthNotImplemented(auth_option)
