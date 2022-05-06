#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from pathlib import Path

from pytest import fixture
from source_freshdesk.client import Client

HERE = Path(__file__).parent.absolute()


@fixture(autouse=True)
def time_sleep_mock(mocker):
    time_mock = mocker.patch("time.sleep", lambda x: None)
    yield time_mock


def test_client_backoff_on_limit_reached(requests_mock):
    """Error once, check that we retry and not fail"""
    responses = [
        {"json": {"error": "limit reached"}, "status_code": 429, "headers": {"Retry-After": "0"}},
        {"json": {"status": "ok"}, "status_code": 200},
    ]
    requests_mock.register_uri("GET", "/api/v2/settings/helpdesk", responses)
    client = Client(domain="someaccount.freshdesk.com", api_key="somekey")

    result = client.settings()

    assert result == {"status": "ok"}


def test_client_backoff_on_server_error(requests_mock):
    """Error once, check that we retry and not fail"""
    responses = [
        {"json": {"error": "something bad"}, "status_code": 500},
        {"json": {"status": "ok"}, "status_code": 200},
    ]
    requests_mock.register_uri("GET", "/api/v2/settings/helpdesk", responses)
    client = Client(domain="someaccount.freshdesk.com", api_key="somekey")

    result = client.settings()

    assert result == {"status": "ok"}
