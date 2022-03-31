from http import HTTPStatus
from unittest.mock import MagicMock

import json
import pytest
import responses
from source_mailchimp.streams import (
    Lists,
    Campaigns,
    EmailActivity
)

from utils import read_full_refresh, read_incremental


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


def test_next_page_token(auth):
    args = {"authenticator": auth}
    stream = Lists(**args)
    inputs = {"response": MagicMock()}
    expected_token = None
    assert stream.next_page_token(**inputs) == expected_token

    resp = json.loads(json.dumps({"lists": [{"id": i} for i in range(101)]}))
    inputs = {"response": MagicMock(json=MagicMock(return_value=resp))}
    expected_token = {"offset": 100}
    assert stream.next_page_token(**inputs) == expected_token


def test_request_params(auth):
    args = {"authenticator": auth}
    stream = Lists(**args)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {"count": 100, "sort_dir": "ASC", "sort_field": "date_created"}
    assert stream.request_params(**inputs) == expected_params

    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": {"offset": 100}}
    expected_params = {"count": 100, "sort_dir": "ASC", "sort_field": "date_created", "offset": 100}
    assert stream.request_params(**inputs) == expected_params


def test_get_updated_state(auth):
    args = {"authenticator": auth}
    stream = Lists(**args)

    current_state_stream = {}
    latest_record = {"date_created": "2020-01-01"}
    new_stream_state = stream.get_updated_state(current_state_stream, latest_record)
    assert new_stream_state == {"date_created": "2020-01-01"}

    current_state_stream = {"date_created": "2020-01-01"}
    latest_record = {"date_created": "2021-01-01"}
    new_stream_state = stream.get_updated_state(current_state_stream, latest_record)
    assert new_stream_state == {"date_created": "2021-01-01"}

    current_state_stream = {"date_created": "2021-01-01"}
    latest_record = {"date_created": "2022-01-01"}
    new_stream_state = stream.get_updated_state(current_state_stream, latest_record)
    assert new_stream_state == {"date_created": "2022-01-01"}


@responses.activate
def test_stream_teams_read(auth):
    args = {"authenticator": auth}
    stream = EmailActivity(**args)
    stream_url = stream.url_base + "reports/123/email-activity"
    campaigns_stream_url = stream.url_base + "campaigns"
    responses.add("GET", campaigns_stream_url, json={"campaigns": [{"id": 123}]})

    response = {
        "emails": [
            {
                "campaign_id": 123,
                "activity": [
                    {"action": "q", "timestamp": "2021-08-24T14:15:22Z"}
                ]
            }
        ]
    }
    responses.add("GET", stream_url, json=response)
    records = read_incremental(stream, {})

    assert records
    assert records == [{"campaign_id": 123, "action": "q", "timestamp": "2021-08-24T14:15:22Z"}]
    assert len(responses.calls) == 2
