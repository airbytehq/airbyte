# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from source_typeform.components import TypeformAuthenticator

from airbyte_cdk.sources.declarative.auth.oauth import DeclarativeSingleUseRefreshTokenOauth2Authenticator
from airbyte_cdk.sources.declarative.auth.token import BearerAuthenticator


def test_typeform_authenticator():
    config = {"credentials": {"auth_type": "access_token", "access_token": "access_token"}}
    oauth_config = {
        "credentials": {"auth_type": "oauth2.0", "access_token": None, "client_id": "client_id", "client_secret": "client_secret"}
    }

    class TokenProvider:
        def get_token(self) -> str:
            return "test token"

    auth = TypeformAuthenticator(
        token_auth=BearerAuthenticator(config=config, token_provider=TokenProvider(), parameters={}),
        config=config,
        oauth2=DeclarativeSingleUseRefreshTokenOauth2Authenticator(connector_config=oauth_config, token_refresh_endpoint="/new_token"),
    )
    assert isinstance(auth, BearerAuthenticator)

    oauth = TypeformAuthenticator(
        token_auth=BearerAuthenticator(config=config, token_provider=TokenProvider(), parameters={}),
        config=oauth_config,
        oauth2=DeclarativeSingleUseRefreshTokenOauth2Authenticator(connector_config=oauth_config, token_refresh_endpoint="/new_token"),
    )
    assert isinstance(oauth, DeclarativeSingleUseRefreshTokenOauth2Authenticator)
