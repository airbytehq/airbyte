# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


from azure.core.credentials import AccessToken
from source_azure_blob_storage.stream_reader import AzureOauth2Authenticator


def test_custom_authenticator(requests_mock):

    authenticator = AzureOauth2Authenticator(
                    token_refresh_endpoint="https://login.microsoftonline.com/tenant_id/oauth2/v2.0/token",
                    client_id="client_id",
                    client_secret="client_secret",
                    refresh_token="refresh_token",
                )
    token_refresh_response = {
        "token_type": "Bearer",
        "scope": "https://storage.azure.com/user_impersonation https://storage.azure.com/.default",
        "expires_in": 5144,
        "ext_expires_in": 5144,
        "access_token": "access_token",
        "refresh_token": "refresh_token"
    }
    requests_mock.post("https://login.microsoftonline.com/tenant_id/oauth2/v2.0/token", json=token_refresh_response)
    new_token = authenticator.get_token()
    assert isinstance(new_token, AccessToken)
    assert new_token.token == "access_token"
