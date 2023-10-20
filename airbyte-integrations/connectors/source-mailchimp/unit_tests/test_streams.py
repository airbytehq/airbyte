#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
import requests
import responses
from airbyte_cdk.models import SyncMode
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


@responses.activate
def test_stream_parse_json_error(auth, caplog):
    args = {"authenticator": auth}
    stream = EmailActivity(**args)
    stream_url = stream.url_base + "reports/123/email-activity"
    campaigns_stream_url = stream.url_base + "campaigns"
    responses.add("GET", campaigns_stream_url, json={"campaigns": [{"id": 123}]})
    responses.add("GET", stream_url, body="not_valid_json")
    read_incremental(stream, {})
    assert "response.content=b'not_valid_json'" in caplog.text


def test_unsubscribes_stream_slices(requests_mock, unsubscribes_stream, campaigns_stream, mock_campaigns_response):
    campaigns_url = campaigns_stream.url_base + campaigns_stream.path()
    requests_mock.register_uri("GET", campaigns_url, json={"campaigns": mock_campaigns_response})

    expected_slices = [{"campaign_id": "campaign_1"}, {"campaign_id": "campaign_2"}, {"campaign_id": "campaign_3"}]
    slices = list(unsubscribes_stream.stream_slices(sync_mode=SyncMode.incremental))
    assert slices == expected_slices


@pytest.mark.parametrize(
    "stream_state, expected_records",
    [
        (  # Test case 1: all records >= state
            {"campaign_1": {"timestamp": "2022-01-01T00:00:00Z"}},
            [
                {"campaign_id": "campaign_1", "email_id": "email_1", "timestamp": "2022-01-02T00:00:00Z"},
                {"campaign_id": "campaign_1", "email_id": "email_2", "timestamp": "2022-01-02T00:00:00Z"},
                {"campaign_id": "campaign_1", "email_id": "email_3", "timestamp": "2022-01-01T00:00:00Z"},
                {"campaign_id": "campaign_1", "email_id": "email_4", "timestamp": "2022-01-03T00:00:00Z"},
            ],
        ),
        (  # Test case 2: one record < state
            {"campaign_1": {"timestamp": "2022-01-02T00:00:00Z"}},
            [
                {"campaign_id": "campaign_1", "email_id": "email_1", "timestamp": "2022-01-02T00:00:00Z"},
                {"campaign_id": "campaign_1", "email_id": "email_2", "timestamp": "2022-01-02T00:00:00Z"},
                {"campaign_id": "campaign_1", "email_id": "email_4", "timestamp": "2022-01-03T00:00:00Z"},
            ],
        ),
        (  # Test case 3: one record >= state
            {"campaign_1": {"timestamp": "2022-01-03T00:00:00Z"}},
            [
                {"campaign_id": "campaign_1", "email_id": "email_4", "timestamp": "2022-01-03T00:00:00Z"},
            ],
        ),
        (  # Test case 4: no state, all records returned
            {},
            [
                {"campaign_id": "campaign_1", "email_id": "email_1", "timestamp": "2022-01-02T00:00:00Z"},
                {"campaign_id": "campaign_1", "email_id": "email_2", "timestamp": "2022-01-02T00:00:00Z"},
                {"campaign_id": "campaign_1", "email_id": "email_3", "timestamp": "2022-01-01T00:00:00Z"},
                {"campaign_id": "campaign_1", "email_id": "email_4", "timestamp": "2022-01-03T00:00:00Z"},
            ],
        ),
    ],
)
def test_parse_response(stream_state, expected_records, unsubscribes_stream):
    mock_response = MagicMock(spec=requests.Response)
    mock_response.json.return_value = {
        "unsubscribes": [
            {"campaign_id": "campaign_1", "email_id": "email_1", "timestamp": "2022-01-02T00:00:00Z"},
            {"campaign_id": "campaign_1", "email_id": "email_2", "timestamp": "2022-01-02T00:00:00Z"},
            {"campaign_id": "campaign_1", "email_id": "email_3", "timestamp": "2022-01-01T00:00:00Z"},
            {"campaign_id": "campaign_1", "email_id": "email_4", "timestamp": "2022-01-03T00:00:00Z"},
        ]
    }
    records = list(unsubscribes_stream.parse_response(response=mock_response, stream_state=stream_state))
    assert records == expected_records


@pytest.mark.parametrize(
    "latest_record, expected_updated_state",
    [
        # Test case 1: latest_record > and updates the state of campaign_1
        (
            {
                "email_id": "email_1",
                "email_address": "address1@email.io",
                "reason": "None given",
                "timestamp": "2022-01-05T00:00:00Z",
                "campaign_id": "campaign_1",
            },
            {
                "campaign_1": {"timestamp": "2022-01-05T00:00:00Z"},
                "campaign_2": {"timestamp": "2022-01-02T00:00:00Z"},
                "campaign_3": {"timestamp": "2022-01-03T00:00:00Z"},
            },
        ),
        # Test case 2: latest_record > and updates the state of campaign_2
        (
            {
                "email_id": "email_2",
                "email_address": "address2@email.io",
                "reason": "Inappropriate content",
                "timestamp": "2022-01-05T00:00:00Z",
                "campaign_id": "campaign_2",
            },
            {
                "campaign_1": {"timestamp": "2022-01-01T00:00:00Z"},
                "campaign_2": {"timestamp": "2022-01-05T00:00:00Z"},
                "campaign_3": {"timestamp": "2022-01-03T00:00:00Z"},
            },
        ),
        # Test case 3: latest_record < and does not update the state of campaign_3
        (
            {
                "email_id": "email_3",
                "email_address": "address3@email.io",
                "reason": "No longer interested",
                "timestamp": "2021-01-01T00:00:00Z",
                "campaign_id": "campaign_3",
            },
            {
                "campaign_1": {"timestamp": "2022-01-01T00:00:00Z"},
                "campaign_2": {"timestamp": "2022-01-02T00:00:00Z"},
                "campaign_3": {"timestamp": "2022-01-03T00:00:00Z"},
            },
        ),
        # Test case 4: latest_record sets state campaign_4
        (
            {
                "email_id": "email_4",
                "email_address": "address4@email.io",
                "reason": "No longer interested",
                "timestamp": "2022-01-04T00:00:00Z",
                "campaign_id": "campaign_4",
            },
            {
                "campaign_1": {"timestamp": "2022-01-01T00:00:00Z"},
                "campaign_2": {"timestamp": "2022-01-02T00:00:00Z"},
                "campaign_3": {"timestamp": "2022-01-03T00:00:00Z"},
                "campaign_4": {"timestamp": "2022-01-04T00:00:00Z"},
            },
        ),
    ],
)
def test_unsubscribes_get_updated_state(unsubscribes_stream, mock_unsubscribes_state, latest_record, expected_updated_state):
    updated_state = unsubscribes_stream.get_updated_state(mock_unsubscribes_state, latest_record)
    assert updated_state == expected_updated_state
