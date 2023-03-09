#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
import responses
from source_mailchimp.streams import Campaigns, EmailActivity, Lists
from utils import read_full_refresh, read_incremental


@pytest.mark.parametrize(
    "stream, endpoint",
    [
        (Lists, "lists"),
        (Campaigns, "campaigns"),
    ],
)
def test_stream_read(requests_mock, auth, stream, endpoint):
    args = {"authenticator": auth}
    stream = stream(**args)
    stream_responses = [
        {
            "json": {
                stream.data_field: [{"id": "test_id"}],
            }
        }
    ]
    stream_url = stream.url_base + endpoint
    requests_mock.register_uri("GET", stream_url, stream_responses)
    records = read_full_refresh(stream)

    assert records


def test_next_page_token(auth):
    args = {"authenticator": auth}
    stream = Lists(**args)
    inputs = {"response": MagicMock()}
    expected_token = None
    assert stream.next_page_token(**inputs) == expected_token

    resp = {"lists": [{"id": i} for i in range(1001)]}
    inputs = {"response": MagicMock(json=MagicMock(return_value=resp))}
    expected_token = {"offset": 1000}
    assert stream.next_page_token(**inputs) == expected_token


@pytest.mark.parametrize(
    "inputs, expected_params",
    [
        (
            {"stream_slice": None, "stream_state": None, "next_page_token": None},
            {"count": 1000, "sort_dir": "ASC", "sort_field": "date_created"},
        ),
        (
            {"stream_slice": None, "stream_state": None, "next_page_token": {"offset": 1000}},
            {"count": 1000, "sort_dir": "ASC", "sort_field": "date_created", "offset": 1000},
        ),
    ],
)
def test_request_params(auth, inputs, expected_params):
    args = {"authenticator": auth}
    stream = Lists(**args)
    assert stream.request_params(**inputs) == expected_params


@pytest.mark.parametrize(
    "current_state_stream, latest_record, expected_state",
    [
        ({}, {"date_created": "2020-01-01"}, {"date_created": "2020-01-01"}),
        ({"date_created": "2020-01-01"}, {"date_created": "2021-01-01"}, {"date_created": "2021-01-01"}),
        ({"date_created": "2021-01-01"}, {"date_created": "2022-01-01"}, {"date_created": "2022-01-01"}),
    ],
)
def test_get_updated_state(auth, current_state_stream, latest_record, expected_state):
    args = {"authenticator": auth}
    stream = Lists(**args)

    new_stream_state = stream.get_updated_state(current_state_stream, latest_record)
    assert new_stream_state == expected_state


@responses.activate
def test_stream_teams_read(auth):
    args = {"authenticator": auth}
    stream = EmailActivity(**args)
    stream_url = stream.url_base + "reports/123/email-activity"
    campaigns_stream_url = stream.url_base + "campaigns"
    responses.add("GET", campaigns_stream_url, json={"campaigns": [{"id": 123}]})

    response = {"emails": [{"campaign_id": 123, "activity": [{"action": "q", "timestamp": "2021-08-24T14:15:22Z"}]}]}
    responses.add("GET", stream_url, json=response)
    records = read_incremental(stream, {})

    assert records
    assert records == [{"campaign_id": 123, "action": "q", "timestamp": "2021-08-24T14:15:22Z"}]
    assert len(responses.calls) == 2
