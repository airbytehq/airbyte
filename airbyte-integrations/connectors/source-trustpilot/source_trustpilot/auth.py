#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping, Tuple

from airbyte_cdk.sources.streams.http.requests_native_auth import SingleUseRefreshTokenOauth2Authenticator, TokenAuthenticator


class TrustpilotApikeyAuthenticator(TokenAuthenticator):
    """
    Requesting data from the Public API requires only the API key.

    See also https://documentation-apidocumentation.trustpilot.com/#Auth
    """

    def __init__(self, token: str):
        super().__init__(token, auth_method=None, auth_header="apikey")

    @property
    def token(self) -> str:
        """
        Unfortunately, the TokenAuthenticator class does not support an empty
        'auth_method' so we have to hack this that only the API key is
        provided in the HTTP header.
        """
        return self._token


class TrustpilotOauth2Authenticator(SingleUseRefreshTokenOauth2Authenticator):
    """
    Requesting data from APIs which require OAuth2 with refresh.

    See also https://documentation-apidocumentation.trustpilot.com/#Auth
    """

    def get_auth_header(self) -> Mapping[str, Any]:
        headers = super().get_auth_header()
        headers.update(
            {
                "apikey": self.get_client_id(),  # The API key is required for OAuth2 requests as well ...
                "Content-Type": "application/x-www-form-urlencoded",
            }
        )
        return headers

    def refresh_access_token(self) -> Tuple[str, int, str]:
        """
        Required because Trustpilot passes the 'expires_in' parameter as string and not as integer.

        Would not be necessary when https://github.com/airbytehq/airbyte/pull/23921 gets merged.
        """
        response_json = self._get_refresh_access_token_response()
        return (
            response_json[self.get_access_token_name()],
            int(response_json[self.get_expires_in_name()]),
            response_json[self.get_refresh_token_name()],
        )


__all__ = ["TrustpilotApikeyAuthenticator", "TrustpilotOauth2Authenticator"]
