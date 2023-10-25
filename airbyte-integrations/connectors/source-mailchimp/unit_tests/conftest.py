#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pytest import fixture
from source_mailchimp.source import MailChimpAuthenticator
from source_mailchimp.streams import Campaigns, Unsubscribes


@fixture(name="data_center")
def data_center_fixture():
    return "some_dc"


@fixture(name="config")
def config_fixture(data_center):
    return {"apikey": f"API_KEY-{data_center}"}


@fixture(name="access_token")
def access_token_fixture():
    return "some_access_token"


@fixture(name="oauth_config")
def oauth_config_fixture(access_token):
    return {
        "credentials": {
            "auth_type": "oauth2.0",
            "client_id": "111111111",
            "client_secret": "secret_1111111111",
            "access_token": access_token,
        }
    }


@fixture(name="apikey_config")
def apikey_config_fixture(data_center):
    return {"credentials": {"auth_type": "apikey", "apikey": f"some_api_key-{data_center}"}}


@fixture(name="wrong_config")
def wrong_config_fixture():
    return {"credentials": {"auth_type": "not auth_type"}}


@fixture(name="auth")
def authenticator_fixture(apikey_config):
    return MailChimpAuthenticator().get_auth(apikey_config)


@fixture(name="campaigns_stream")
def campaigns_stream_fixture(auth):
    return Campaigns(authenticator=auth)


@fixture(name="unsubscribes_stream")
def unsubscribes_stream_fixture(auth):
    return Unsubscribes(authenticator=auth)


@fixture(name="mock_campaigns_response")
def mock_campaigns_response_fixture():
    return [
        {"id": "campaign_1", "web_id": 1, "type": "regular", "create_time": "2022-01-01T00:00:00Z"},
        {"id": "campaign_2", "web_id": 2, "type": "plaintext", "create_time": "2022-01-02T00:00:00Z"},
        {"id": "campaign_3", "web_id": 3, "type": "variate", "create_time": "2022-01-03T00:00:00Z"},
    ]


@fixture(name="mock_unsubscribes_state")
def mock_unsubscribes_state_fixture():
    return {
        "campaign_1": {"timestamp": "2022-01-01T00:00:00Z"},
        "campaign_2": {"timestamp": "2022-01-02T00:00:00Z"},
        "campaign_3": {"timestamp": "2022-01-03T00:00:00Z"},
    }
