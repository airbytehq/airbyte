#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import pytest
from source_zendesk_talk.client import Client


@pytest.fixture(name="zendesk_credentials")
def zendesk_credentials_fixture():
    return {
        "email": "fake-email@email.cm",
        "access_token": "fake_access_token",
        "subdomain": "wrong_subdomain",
        "start_date": "2021-02-12T00:00:00Z",
    }


def test_client_with_wrong_credentials(zendesk_credentials):
    """Test check with wrong credentials"""
    client = Client(**zendesk_credentials)

    alive, error = client.health_check()

    assert not alive
    assert error


def test_client_backoff_on_limit_reached(requests_mock, zendesk_credentials):
    """Error twice, check that we retry and not fail"""
    responses = [
        {"json": {"error": "limit reached"}, "status_code": 429},
        {"json": {"error": "limit reached"}, "status_code": 429},
        {"json": {"phone_numbers": [], "count": 0}, "status_code": 200},
    ]

    requests_mock.get(f"https://{zendesk_credentials['subdomain']}.zendesk.com/api/v2/channels/voice/phone_numbers", responses)
    client = Client(**zendesk_credentials)

    alive, error = client.health_check()

    assert alive
    assert not error
