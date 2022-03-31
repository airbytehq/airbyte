from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from source_mailchimp.streams import (
    Lists,
    Campaigns,
)

from utils import read_full_refresh


@pytest.mark.parametrize(
    ("http_status", "response_text", "expected_backoff_time"),
    [
        (HTTPStatus.BAD_GATEWAY, "", None),
    ],
)
def test_backoff_time(auth, http_status, response_text, expected_backoff_time):
    response_mock = MagicMock()
    response_mock.status_code = http_status
    response_mock.text = response_text
    args = {"authenticator": auth}
    stream = Lists(**args)
    assert stream.backoff_time(response_mock) == expected_backoff_time


@pytest.mark.parametrize(
    "stream, endpoint",
    [
        (Lists, "lists"),
        (Campaigns, "campaigns"),
    ]
)
def test_stream_read(requests_mock, auth, stream, endpoint):
    args = {"authenticator": auth}
    stream = stream(**args)
    responses = [
        {
            "json": {
                stream.data_field: [
                    {
                        "id": "test_id"
                    }
                ],
            }
        }
    ]
    stream_url = stream.url_base + endpoint
    requests_mock.register_uri("GET", stream_url, responses)
    records = read_full_refresh(stream)

    assert records
