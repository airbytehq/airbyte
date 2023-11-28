#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from unittest.mock import MagicMock

import pytest
import requests
import responses
from airbyte_cdk.models import SyncMode
from requests.exceptions import HTTPError
from source_mailchimp.streams import Campaigns, EmailActivity, ListMembers, Lists, Reports, Segments
from utils import read_full_refresh, read_incremental


@pytest.mark.parametrize(
    "stream, endpoint",
    [
        (Lists, "lists"),
        (Campaigns, "campaigns"),
        (Segments, "lists/123/segments"),
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

    # Mock the 'lists' endpoint as Segments stream_slice
    lists_url = stream.url_base + "lists"
    lists_response = {"json": {"lists": [{"id": "123"}]}}
    requests_mock.register_uri("GET", lists_url, [lists_response])
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


@pytest.mark.parametrize(
    "stream_class, stream_slice, stream_state, next_page_token, expected_params",
    [
        # Test case 1: no state, no next_page_token
        (
            Segments,
            {"list_id": "123"},
            {},
            None,
            {"count": 1000, "sort_dir": "ASC", "sort_field": "updated_at", "list_id": "123", "exclude_fields": "segments._links"},
        ),
        # Test case 2: state and next_page_token
        (
            ListMembers,
            {"list_id": "123"},
            {"123": {"last_changed": "2023-10-15T00:00:00Z"}},
            {"offset": 1000},
            {
                "count": 1000,
                "sort_dir": "ASC",
                "sort_field": "last_changed",
                "list_id": "123",
                "offset": 1000,
                "exclude_fields": "members._links",
                "since_last_changed": "2023-10-15T00:00:00Z",
            },
        ),
    ],
    ids=[
        "Segments: no next_page_token or state to add to request params",
        "ListMembers: next_page_token and state filter added to request params",
    ],
)
def test_list_child_request_params(auth, stream_class, stream_slice, stream_state, next_page_token, expected_params):
    """
    Tests the request_params method for the shared MailChimpListSubStream class.
    """
    stream = stream_class(authenticator=auth)
    params = stream.request_params(stream_slice=stream_slice, stream_state=stream_state, next_page_token=next_page_token)
    assert params == expected_params


@pytest.mark.parametrize(
    "stream_class, current_stream_state,latest_record,expected_state",
    [
        # Test case 1: current_stream_state is empty
        (Segments, {}, {"list_id": "list_1", "updated_at": "2023-10-15T00:00:00Z"}, {"list_1": {"updated_at": "2023-10-15T00:00:00Z"}}),
        # Test case 2: latest_record's cursor is higher than current_stream_state for list_1 and updates it
        (
            Segments,
            {"list_1": {"updated_at": "2023-10-14T00:00:00Z"}, "list_2": {"updated_at": "2023-10-15T00:00:00Z"}},
            {"list_id": "list_1", "updated_at": "2023-10-15T00:00:00Z"},
            {"list_1": {"updated_at": "2023-10-15T00:00:00Z"}, "list_2": {"updated_at": "2023-10-15T00:00:00Z"}},
        ),
        # Test case 3: latest_record's cursor is lower than current_stream_state for list_2, no state update
        (
            ListMembers,
            {"list_1": {"last_changed": "2023-10-15T00:00:00Z"}, "list_2": {"last_changed": "2023-10-15T00:00:00Z"}},
            {"list_id": "list_2", "last_changed": "2023-10-14T00:00:00Z"},
            {"list_1": {"last_changed": "2023-10-15T00:00:00Z"}, "list_2": {"last_changed": "2023-10-15T00:00:00Z"}},
        ),
    ],
    ids=[
        "Segments: no current_stream_state",
        "Segments: latest_record's cursor > than current_stream_state for list_1",
        "ListMembers: latest_record's cursor < current_stream_state for list_2",
    ],
)
def test_list_child_get_updated_state(auth, stream_class, current_stream_state, latest_record, expected_state):
    """
    Tests that the get_updated_state method for the shared MailChimpListSubStream class
    correctly updates state only for its slice.
    """
    segments_stream = stream_class(authenticator=auth)
    updated_state = segments_stream.get_updated_state(current_stream_state, latest_record)
    assert updated_state == expected_state


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
    ids=[
        "all records >= state",
        "one record < state",
        "one record >= state",
        "no state, all records returned",
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
    ids=[
        "latest_record > and updates the state of campaign_1",
        "latest_record > and updates the state of campaign_2",
        "latest_record < and does not update the state of campaign_3",
        "latest_record sets state of campaign_4",
    ],
)
def test_unsubscribes_get_updated_state(unsubscribes_stream, mock_unsubscribes_state, latest_record, expected_updated_state):
    updated_state = unsubscribes_stream.get_updated_state(mock_unsubscribes_state, latest_record)
    assert updated_state == expected_updated_state


@pytest.mark.parametrize(
    "stream,url,status_code,response_content,expected_availability,expected_reason_substring",
    [
        (
            Campaigns,
            "https://some_dc.api.mailchimp.com/3.0/campaigns",
            403,
            b'{"object": "error", "status": 403, "code": "restricted_resource"}',
            False,
            "Unable to read campaigns stream",
        ),
        (
            EmailActivity,
            "https://some_dc.api.mailchimp.com/3.0/reports/123/email-activity",
            403,
            b'{"object": "error", "status": 403, "code": "restricted_resource"}',
            False,
            "Unable to read email_activity stream",
        ),
        (
            Lists,
            "https://some_dc.api.mailchimp.com/3.0/lists",
            200,
            b'{ "lists": [{"id": "123", "date_created": "2022-01-01T00:00:00+000"}]}',
            True,
            None,
        ),
        (
            Lists,
            "https://some_dc.api.mailchimp.com/3.0/lists",
            400,
            b'{ "object": "error", "status": 404, "code": "invalid_action"}',
            False,
            None,
        ),
    ],
    ids=[
        "Campaigns 403 error",
        "EmailActivity 403 error",
        "Lists 200 success",
        "Lists 400 error",
    ],
)
def test_403_error_handling(
    auth, requests_mock, stream, url, status_code, response_content, expected_availability, expected_reason_substring
):
    """
    Test that availability strategy flags streams with 403 error as unavailable
    and returns appropriate message.
    """

    requests_mock.get(url=url, status_code=status_code, content=response_content)

    stream = stream(authenticator=auth)

    if stream.__class__.__name__ == "EmailActivity":
        stream.stream_slices = MagicMock(return_value=[{"campaign_id": "123"}])

    try:
        is_available, reason = stream.check_availability(logger=logging.Logger, source=MagicMock())

        assert is_available is expected_availability

        if expected_reason_substring:
            assert expected_reason_substring in reason
        else:
            assert reason is None

    # Handle non-403 error
    except HTTPError as e:
        assert e.response.status_code == status_code

@pytest.mark.parametrize(
    "record, expected_return",
    [
        (
            {"clicks": {"last_click": ""}, "opens": {"last_open": ""}},
            {"clicks": {}, "opens": {}},
        ),
        (
            {"clicks": {"last_click": "2023-01-01T00:00:00.000Z"}, "opens": {"last_open": ""}},
            {"clicks": {"last_click": "2023-01-01T00:00:00.000Z"}, "opens": {}},
        ),
        (         
            {"clicks": {"last_click": ""}, "opens": {"last_open": "2023-01-01T00:00:00.000Z"}},
            {"clicks": {}, "opens": {"last_open": "2023-01-01T00:00:00.000Z"}},

        ),
        (
            {"clicks": {"last_click": "2023-01-01T00:00:00.000Z"}, "opens": {"last_open": "2023-01-01T00:00:00.000Z"}},
            {"clicks": {"last_click": "2023-01-01T00:00:00.000Z"}, "opens": {"last_open": "2023-01-01T00:00:00.000Z"}},
        ),
    ],
    ids=[
        "last_click and last_open empty",
        "last_click empty",
        "last_open empty",
        "last_click and last_open not empty"
    ]
)
def test_reports_remove_empty_datetime_fields(auth, record, expected_return):
    """
    Tests that the Reports stream removes the 'clicks' and 'opens' fields from the response
    when they are empty strings
    """
    stream = Reports(authenticator=auth)
    assert stream.remove_empty_datetime_fields(record) == expected_return, f"Expected: {expected_return}, Actual: {stream.remove_empty_datetime_fields(record)}"
