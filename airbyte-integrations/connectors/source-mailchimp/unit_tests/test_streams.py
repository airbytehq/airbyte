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
from source_mailchimp.streams import (
    Automations,
    Campaigns,
    EmailActivity,
    InterestCategories,
    Interests,
    ListMembers,
    Lists,
    Reports,
    SegmentMembers,
    Segments,
    Tags,
    Unsubscribes,
)
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
    "stream, inputs, expected_params",
    [
        (
            Lists,
            {"stream_slice": None, "stream_state": None, "next_page_token": None},
            {"count": 1000, "sort_dir": "ASC", "sort_field": "date_created", "exclude_fields": "lists._links"},
        ),
        (
            Lists,
            {"stream_slice": None, "stream_state": None, "next_page_token": {"offset": 1000}},
            {"count": 1000, "sort_dir": "ASC", "sort_field": "date_created", "offset": 1000, "exclude_fields": "lists._links"},
        ),
        (
            InterestCategories,
            {"stream_slice": {"parent": {"id": "123"}}, "stream_state": None, "next_page_token": None},
            {"count": 1000, "exclude_fields": "categories._links"},
        ),
        (
            Interests,
            {"stream_slice": {"parent": {"id": "123"}}, "stream_state": None, "next_page_token": {"offset": 2000}},
            {"count": 1000, "exclude_fields": "interests._links", "offset": 2000},
        ),
    ],
    ids=[
        "Lists: no next_page_token or state to add to request params",
        "Lists: next_page_token added to request params",
        "InterestCategories: no next_page_token to add to request params",
        "Interests: next_page_token added to request params",
    ],
)
def test_request_params(auth, stream, inputs, expected_params):
    args = {"authenticator": auth}
    if stream == InterestCategories:
        args["parent"] = Lists(**args)
    elif stream == Interests:
        args["parent"] = InterestCategories(authenticator=auth, parent=Lists(authenticator=auth))
    stream = stream(**args)
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
            {"list_id": "123", "since_last_changed": "2023-10-15T00:00:00Z"},
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
        (
            SegmentMembers,
            {"segment_1": {"last_changed": "2023-10-15T00:00:00Z"}, "segment_2": {"last_changed": "2023-10-15T00:00:00Z"}},
            {"segment_id": "segment_1", "last_changed": "2023-10-16T00:00:00Z"},
            {"segment_1": {"last_changed": "2023-10-16T00:00:00Z"}, "segment_2": {"last_changed": "2023-10-15T00:00:00Z"}},
        ),
        (
            SegmentMembers,
            {"segment_1": {"last_changed": "2023-10-15T00:00:00Z"}},
            {"segment_id": "segment_2", "last_changed": "2023-10-16T00:00:00Z"},
            {"segment_1": {"last_changed": "2023-10-15T00:00:00Z"}, "segment_2": {"last_changed": "2023-10-16T00:00:00Z"}},
        )
    ],
    ids=[
        "Segments: no current_stream_state",
        "Segments: latest_record's cursor > than current_stream_state for list_1",
        "ListMembers: latest_record's cursor < current_stream_state for list_2",
        "SegmentMembers: latest_record's cursor > current_stream_state for segment_1",
        "SegmentMembers: no stream_state for current slice, new slice added to state"
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


@pytest.mark.parametrize(
    "stream_state, records, expected",
    [
        # Test case 1: No stream state, all records should be yielded
        (
          {},
          {"members": [
            {"id": 1, "segment_id": "segment_1", "last_changed": "2021-01-01T00:00:00Z"},
            {"id": 2, "segment_id": "segment_1", "last_changed": "2021-01-02T00:00:00Z"}
          ]},
          [
            {"id": 1, "segment_id": "segment_1", "last_changed": "2021-01-01T00:00:00Z"},
            {"id": 2, "segment_id": "segment_1", "last_changed": "2021-01-02T00:00:00Z"}
          ]
        ),
        
        # Test case 2: Records older than stream state should be filtered out
        (
          {"segment_1": {"last_changed": "2021-02-01T00:00:00Z"}},
          {"members": [
            {"id": 1, "segment_id": "segment_1", "last_changed": "2021-01-01T00:00:00Z"},
            {"id": 2, "segment_id": "segment_1", "last_changed": "2021-03-01T00:00:00Z"}
          ]},
          [{"id": 2, "segment_id": "segment_1", "last_changed": "2021-03-01T00:00:00Z"}]
        ),
        
        # Test case 3: Two lists in stream state, only state for segment_id_1 determines filtering
        (
          {"segment_1": {"last_changed": "2021-01-02T00:00:00Z"}, "segment_2": {"last_changed": "2022-01-01T00:00:00Z"}},
          {"members": [            
            {"id": 1, "segment_id": "segment_1", "last_changed": "2021-01-01T00:00:00Z"},
            {"id": 2, "segment_id": "segment_1", "last_changed": "2021-03-01T00:00:00Z"}
          ]}, 
          [{"id": 2, "segment_id": "segment_1", "last_changed": "2021-03-01T00:00:00Z"}]
        ),
    ],
    ids=[
        "No stream state, all records should be yielded",
        "Record < stream state, should be filtered out",
        "Record >= stream state, should be yielded",
    ]
)
def test_segment_members_parse_response(auth, stream_state, records, expected):
    segment_members_stream = SegmentMembers(authenticator=auth)
    response = MagicMock()
    response.json.return_value = records
    parsed_records = list(segment_members_stream.parse_response(response, stream_state, stream_slice={"segment_id": "segment_1"}))
    assert parsed_records == expected, f"Expected: {expected}, Actual: {parsed_records}"


@pytest.mark.parametrize(
    "stream, record, expected_record",
    [
        (
            SegmentMembers,
            {"id": 1, "email_address": "a@gmail.com", "email_type": "html", "opt_timestamp": ""},
            {"id": 1, "email_address": "a@gmail.com", "email_type": "html", "opt_timestamp": None}
        ),
        (
            SegmentMembers,
            {"id": 1, "email_address": "a@gmail.com", "email_type": "html", "opt_timestamp": "2022-01-01T00:00:00.000Z", "merge_fields": {"FNAME": "Bob", "LNAME": "", "ADDRESS": "", "PHONE": ""}},
            {"id": 1, "email_address": "a@gmail.com", "email_type": "html", "opt_timestamp": "2022-01-01T00:00:00.000Z", "merge_fields": {"FNAME": "Bob", "LNAME": None, "ADDRESS": None, "PHONE": None}}
        ),
        (
            Campaigns,            
            {"id": "1", "web_id": 2, "email_type": "html", "create_time": "2022-01-01T00:00:00.000Z", "send_time": ""},
            {"id": "1", "web_id": 2, "email_type": "html", "create_time": "2022-01-01T00:00:00.000Z", "send_time": None}
        ),
        (
            Reports,
            {"id": "1", "type": "rss", "clicks": {"clicks_total": 1, "last_click": "2022-01-01T00:00:00Z"}, "opens": {"opens_total": 0, "last_open": ""}},
            {"id": "1", "type": "rss", "clicks": {"clicks_total": 1, "last_click": "2022-01-01T00:00:00Z"}, "opens": {"opens_total": 0, "last_open": None}}
        ),
        (
            Lists,
            {"id": "1", "name": "Santa's List", "stats": {"last_sub_date": "2022-01-01T00:00:00Z", "last_unsub_date": ""}},
            {"id": "1", "name": "Santa's List", "stats": {"last_sub_date": "2022-01-01T00:00:00Z", "last_unsub_date": None}}            
        )
    ],
    ids=[
        "segment_members: opt_timestamp nullified",
        "segment_members: nested merge_fields nullified",
        "campaigns: send_time nullified",
        "reports: nested opens.last_open nullified",
        "lists: stats.last_unsub_date nullified"
    ]
)
def test_filter_empty_fields(auth, stream, record, expected_record):
    """
    Tests that empty string values are converted to None.
    """
    stream = stream(authenticator=auth)
    assert stream.filter_empty_fields(record) == expected_record


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
    stream_slice = {"campaign_id": "campaign_1"}
    records = list(unsubscribes_stream.parse_response(response=mock_response, stream_slice=stream_slice, stream_state=stream_state))
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
    "stream, stream_slice, expected_endpoint",
    [
        (Automations, {}, "automations"),
        (Lists, {}, "lists"),
        (Campaigns, {}, "campaigns"),
        (EmailActivity, {"campaign_id": "123"}, "reports/123/email-activity"),
        (InterestCategories, {"parent": {"id": "123"}}, "lists/123/interest-categories"),
        (Interests, {"parent": {"list_id": "123", "id": "456"}}, "lists/123/interest-categories/456/interests"),
        (ListMembers, {"list_id": "123"}, "lists/123/members"),
        (Reports, {}, "reports"),
        (SegmentMembers, {"list_id": "123", "segment_id": "456"}, "lists/123/segments/456/members"),
        (Segments, {"list_id": "123"}, "lists/123/segments"),
        (Tags, {"parent": {"id": "123"}}, "lists/123/tag-search"),
        (Unsubscribes, {"campaign_id": "123"}, "reports/123/unsubscribed"),
    ],
    ids=[
        "Automations",
        "Lists",
        "Campaigns",
        "EmailActivity",
        "InterestCategories",
        "Interests",
        "ListMembers",
        "Reports",
        "SegmentMembers",
        "Segments",
        "Tags",
        "Unsubscribes",
    ],
)
def test_path(auth, stream, stream_slice, expected_endpoint):
    """
    Test the path method for each stream.
    """

    # Add parent stream where necessary
    if stream is InterestCategories or stream is Tags:
        stream = stream(authenticator=auth, parent=Lists(authenticator=auth))
    elif stream is Interests:
        stream = stream(authenticator=auth, parent=InterestCategories(authenticator=auth, parent=Lists(authenticator=auth)))
    else:
        stream = stream(authenticator=auth)

    endpoint = stream.path(stream_slice=stream_slice)

    assert endpoint == expected_endpoint, f"Stream {stream}: expected path '{expected_endpoint}', got '{endpoint}'"


@pytest.mark.parametrize(
    "start_date, state_date, expected_return_value",
    [
        (
            "2021-01-01T00:00:00.000Z",
            "2020-01-01T00:00:00+00:00",
            "2021-01-01T00:00:00Z"
        ),
        (
            "2021-01-01T00:00:00.000Z",
            "2023-10-05T00:00:00+00:00",
            "2023-10-05T00:00:00+00:00"
        ),
        (
            None,
            "2022-01-01T00:00:00+00:00",
            "2022-01-01T00:00:00+00:00"
        ),
        (
            "2020-01-01T00:00:00.000Z",
            None,
            "2020-01-01T00:00:00Z"
        ),
        (
            None,
            None,
            None
        )
    ]
)
def test_get_filter_date(auth, start_date, state_date, expected_return_value):
    """
    Tests that the get_filter_date method returns the correct date string
    """
    stream = Campaigns(authenticator=auth, start_date=start_date)
    result = stream.get_filter_date(start_date, state_date)
    assert result == expected_return_value, f"Expected: {expected_return_value}, Actual: {result}"


@pytest.mark.parametrize(
    "stream_class, records, filter_date, expected_return_value",
    [
        (
            Unsubscribes,
            [
                {"campaign_id": "campaign_1", "email_id": "email_1", "timestamp": "2022-01-02T00:00:00Z"},
                {"campaign_id": "campaign_1", "email_id": "email_2", "timestamp": "2022-01-04T00:00:00Z"},
                {"campaign_id": "campaign_1", "email_id": "email_3", "timestamp": "2022-01-03T00:00:00Z"},
                {"campaign_id": "campaign_1", "email_id": "email_4", "timestamp": "2022-01-01T00:00:00Z"},
            ],
            "2022-01-02T12:00:00+00:00",
            [
                {"campaign_id": "campaign_1", "email_id": "email_2", "timestamp": "2022-01-04T00:00:00Z"},
                {"campaign_id": "campaign_1", "email_id": "email_3", "timestamp": "2022-01-03T00:00:00Z"},
            ],
        ),
        (
            SegmentMembers,
            [
                {"id": 1, "segment_id": "segment_1", "last_changed": "2021-01-04T00:00:00Z"},
                {"id": 2, "segment_id": "segment_1", "last_changed": "2021-01-01T00:00:00Z"},
                {"id": 3, "segment_id": "segment_1", "last_changed": "2021-01-03T00:00:00Z"},
                {"id": 4, "segment_id": "segment_1", "last_changed": "2021-01-02T00:00:00Z"},
            ],
            None,
            [
                {"id": 1, "segment_id": "segment_1", "last_changed": "2021-01-04T00:00:00Z"},
                {"id": 2, "segment_id": "segment_1", "last_changed": "2021-01-01T00:00:00Z"},
                {"id": 3, "segment_id": "segment_1", "last_changed": "2021-01-03T00:00:00Z"},
                {"id": 4, "segment_id": "segment_1", "last_changed": "2021-01-02T00:00:00Z"},
            ],
        )
    ],
    ids=[
        "Unsubscribes: filter_date is set, records filtered",
        "SegmentMembers: filter_date is None, all records returned"
    ]
)
def test_filter_old_records(auth, stream_class, records, filter_date, expected_return_value):
    """
    Tests the logic for filtering old records in streams that do not support query_param filtering.
    """
    stream = stream_class(authenticator=auth)
    filtered_records = list(stream.filter_old_records(records, filter_date))
    assert filtered_records == expected_return_value
