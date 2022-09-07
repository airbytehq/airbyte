#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pendulum
import pytest
from source_marketo.source import Activities, MarketoAuthenticator


@pytest.fixture(autouse=True)
def mock_requests(requests_mock):
    requests_mock.register_uri(
        "GET", "https://602-euo-598.mktorest.com/identity/oauth/token", json={"access_token": "token", "expires_in": 3600}
    )
    requests_mock.register_uri(
        "POST",
        "https://602-euo-598.mktorest.com/bulk/v1/activities/export/create.json",
        [
            {"json": {"result": [{"exportId": "2c09ce6d", "format": "CSV", "status": "Created", "createdAt": "2022-06-20T08:44:08Z"}]}},
            {"json": {"result": [{"exportId": "cd465f55", "format": "CSV", "status": "Created", "createdAt": "2022-06-20T08:45:08Z"}]}},
            {"json": {"result": [{"exportId": "null", "format": "CSV", "status": "Failed", "createdAt": "2022-06-20T08:46:08Z"}]}},
            {"json": {"result": [{"exportId": "232aafb4", "format": "CSV", "status": "Created", "createdAt": "2022-06-20T08:47:08Z"}]}},
        ],
    )


@pytest.fixture
def config():
    start_date = pendulum.now().subtract(days=75).strftime("%Y-%m-%dT%H:%M:%SZ")
    config = {
        "client_id": "client-id",
        "client_secret": "********",
        "domain_url": "https://602-EUO-598.mktorest.com",
        "start_date": start_date,
        "window_in_days": 30,
    }
    config["authenticator"] = MarketoAuthenticator(config)
    return config


@pytest.fixture
def activity():
    return {
        "id": 6,
        "name": "send_email",
        "description": "Send Marketo Email to a person",
        "primaryAttribute": {"name": "Mailing ID", "dataType": "integer"},
        "attributes": [
            {"name": "Campaign Run ID", "dataType": "integer"},
            {"name": "Choice Number", "dataType": "integer"},
            {"name": "Has Predictive", "dataType": "boolean"},
            {"name": "Step ID", "dataType": "integer"},
            {"name": "Test Variant", "dataType": "integer"},
        ],
    }


@pytest.fixture
def send_email_stream(config, activity):
    stream_name = f"activities_{activity['name']}"
    cls = type(stream_name, (Activities,), {"activity": activity})
    return cls(config)
