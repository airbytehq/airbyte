# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from airbyte_cdk import SingleUseRefreshTokenOauth2Authenticator


class ExactOauth2Authenticator(SingleUseRefreshTokenOauth2Authenticator):
    def __init__(self, connector_config, token_refresh_endpoint, **kwargs):
        super().__init__(connector_config, token_refresh_endpoint, **kwargs)
