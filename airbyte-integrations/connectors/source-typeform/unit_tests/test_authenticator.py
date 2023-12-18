# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from airbyte_cdk.sources.declarative.auth.oauth import DeclarativeSingleUseRefreshTokenOauth2Authenticator
from airbyte_cdk.sources.declarative.auth.token import BearerAuthenticator
from source_typeform.components import TypeformAuthenticator


def test_typeform_authenticator():
    config = {"credentials": {"access_token": "access_token", "client_id": None, "client_secret": None}}
    oauth_config = {"credentials": {"access_token": None, "client_id": "client_id", "client_secret": "client_secret"}}

    class TokenProvider:
        def get_token(self) -> str:
            return "test token"

    auth = TypeformAuthenticator(
        token_auth=BearerAuthenticator(config=config, token_provider=TokenProvider(), parameters={}),
        config=config,
        oauth2=DeclarativeSingleUseRefreshTokenOauth2Authenticator(connector_config=config, token_refresh_endpoint="/new_token")
    )
    assert isinstance(auth, BearerAuthenticator)

    oauth = TypeformAuthenticator(
        token_auth=BearerAuthenticator(config=oauth_config, token_provider=TokenProvider(), parameters={}),
        config=oauth_config,
        oauth2=DeclarativeSingleUseRefreshTokenOauth2Authenticator(connector_config=oauth_config, token_refresh_endpoint="/new_token")
    )
    assert isinstance(oauth, DeclarativeSingleUseRefreshTokenOauth2Authenticator)
