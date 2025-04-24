#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass

from airbyte_cdk.sources.declarative.auth.oauth import DeclarativeSingleUseRefreshTokenOauth2Authenticator
from airbyte_cdk.sources.declarative.types import Config


@dataclass
class SingleUseOauth2Authenticator(DeclarativeSingleUseRefreshTokenOauth2Authenticator):
    config: Config

    def __post_init__(self):
        self._connector_config = self.config
        self._token_expiry_date_config_path = "credentials/token_expiry_date"
        self.token_refresh_endpoint = "https://accounts.salesloft.com/oauth/token"
        self._access_token_config_path = "credentials/access_token"

    @property
    def auth_header(self) -> str:
        return "Authorization"

    @property
    def token(self) -> str:
        return f"Bearer {self.get_access_token()}"
