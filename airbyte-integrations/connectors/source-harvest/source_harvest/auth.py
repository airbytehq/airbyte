#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping

from airbyte_cdk.sources.streams.http.requests_native_auth import SingleUseRefreshTokenOauth2Authenticator, TokenAuthenticator


class HarvestMixin:
    """
    Mixin class for providing additional HTTP header for specifying account ID
    https://help.getharvest.com/api-v2/authentication-api/authentication/authentication/
    """

    def __init__(self, *, account_id: str, account_id_header: str = "Harvest-Account-ID", **kwargs):
        super().__init__(**kwargs)
        self.account_id = account_id
        self.account_id_header = account_id_header

    def get_auth_header(self) -> Mapping[str, Any]:
        return {**super().get_auth_header(), self.account_id_header: self.account_id}


class HarvestTokenAuthenticator(HarvestMixin, TokenAuthenticator):
    """
    Auth class for Personal Access Token
    https://help.getharvest.com/api-v2/authentication-api/authentication/authentication/#personal-access-tokens
    """


class HarvestOauth2Authenticator(SingleUseRefreshTokenOauth2Authenticator):
    """
    Auth class for OAuth2
    https://help.getharvest.com/api-v2/authentication-api/authentication/authentication/#for-server-side-applications
    """

    def get_auth_header(self) -> Mapping[str, Any]:
        return {**super().get_auth_header(), "Harvest-Account-ID": self._connector_config["account_id"]}
