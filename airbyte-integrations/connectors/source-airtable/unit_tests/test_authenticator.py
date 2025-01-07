#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pytest
from source_airtable.auth import AirtableAuth, AirtableOAuth

from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from airbyte_cdk.utils import AirbyteTracedException


CONFIG_OAUTH = {"credentials": {"auth_method": "oauth2.0", "client_id": "sample_client_id", "client_secret": "sample_client_secret"}}


@pytest.mark.parametrize(
    "config, expected_auth_class",
    [
        ({"api_key": "sample_api_key"}, TokenAuthenticator),
        (CONFIG_OAUTH, AirtableOAuth),
        ({"credentials": {"auth_method": "api_key", "api_key": "sample_api_key"}}, TokenAuthenticator),
    ],
    ids=["old_config_api_key", "oauth2.0", "api_key"],
)
def test_airtable_auth(config, expected_auth_class):
    auth_instance = AirtableAuth(config)
    assert isinstance(auth_instance, expected_auth_class)


def test_airtable_oauth():
    auth_instance = AirtableAuth(CONFIG_OAUTH)
    assert isinstance(auth_instance, AirtableOAuth)
    assert auth_instance.build_refresh_request_headers() == {
        "Authorization": "Basic c2FtcGxlX2NsaWVudF9pZDpzYW1wbGVfY2xpZW50X3NlY3JldA==",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    assert auth_instance.build_refresh_request_body() == {"grant_type": "refresh_token", "refresh_token": ""}


def test_airtable_oauth_token_refresh_exception(requests_mock):
    auth_instance = AirtableAuth(CONFIG_OAUTH)
    requests_mock.post(
        "https://airtable.com/oauth2/v1/token", status_code=400, json={"error": "invalid_grant", "error_description": "grant invalid"}
    )
    with pytest.raises(AirbyteTracedException) as e:
        auth_instance._get_refresh_access_token_response()
    assert e.value.message == "Refresh token is invalid or expired. Please re-authenticate to restore access to Airtable."
