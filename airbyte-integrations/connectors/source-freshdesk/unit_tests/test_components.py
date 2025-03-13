#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import random
from typing import Any, MutableMapping
from unittest.mock import MagicMock, patch

import pytest
import requests
from requests.auth import HTTPBasicAuth

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOptionType
from airbyte_cdk.sources.streams import Stream


@pytest.fixture(name="config")
def config_fixture():
    return {"domain": "test.freshdesk.com", "api_key": "secret_api_key", "requests_per_minute": 50, "start_date": "2002-02-10T22:21:44Z"}


@pytest.fixture(name="authenticator")
def authenticator_fixture(config):
    return HTTPBasicAuth(username=config["api_key"], password="unused_with_api_key")


def find_stream(components_module, stream_name, config):
    streams = components_module.SourceFreshdesk().streams(config=config)

    # cache should be disabled once this issue is fixed https://github.com/airbytehq/airbyte-internal-issues/issues/6513
    for stream in streams:
        stream.retriever.requester.use_cache = True

    # find by name
    for stream in streams:
        if stream.name == stream_name:
            return stream
    raise ValueError(f"Stream {stream_name} not found")


@pytest.fixture(name="responses")
def responses_fixtures():
    return [
        {
            "url": "https://test.freshdesk.com/api/v2/tickets?per_page=1&updated_since=2002-02-10T22%3A21%3A44Z",
            "json": [{"id": 1, "updated_at": "2018-01-02T00:00:00Z"}],
            "headers": {
                "Link": '<https://test.freshdesk.com/api/v2/tickets?per_page=1&page=2&updated_since=2002-02-10T22%3A21%3A44Z>; rel="next"'
            },
        },
        {
            "url": "https://test.freshdesk.com/api/v2/tickets?per_page=1&page=2&updated_since=2002-02-10T22%3A21%3A44Z",
            "json": [{"id": 2, "updated_at": "2018-02-02T00:00:00Z"}],
            "headers": {
                "Link": '<https://test.freshdesk.com/api/v2/tickets?per_page=1&page=3&updated_since=2002-02-10T22%3A21%3A44Z>; rel="next"'
            },
        },
        {
            "url": "https://test.freshdesk.com/api/v2/tickets?per_page=1&updated_since=2018-02-02T00%3A00%3A00Z",
            "json": [{"id": 2, "updated_at": "2018-02-02T00:00:00Z"}],
            "headers": {
                "Link": '<https://test.freshdesk.com/api/v2/tickets?per_page=1&page=2&updated_since=2018-02-02T00%3A00%3A00Z>; rel="next"'
            },
        },
        {
            "url": "https://test.freshdesk.com/api/v2/tickets?per_page=1&page=2&updated_since=2018-02-02T00%3A00%3A00Z",
            "json": [{"id": 3, "updated_at": "2018-03-02T00:00:00Z"}],
            "headers": {
                "Link": '<https://test.freshdesk.com/api/v2/tickets?per_page=1&page=3&updated_since=2018-02-02T00%3A00%3A00Z>; rel="next"'
            },
        },
        {
            "url": "https://test.freshdesk.com/api/v2/tickets?per_page=1&updated_since=2018-03-02T00%3A00%3A00Z",
            "json": [{"id": 3, "updated_at": "2018-03-02T00:00:00Z"}],
            "headers": {
                "Link": '<https://test.freshdesk.com/api/v2/tickets?per_page=1&page=2&updated_since=2018-03-02T00%3A00%3A00Z>; rel="next"'
            },
        },
        {
            "url": "https://test.freshdesk.com/api/v2/tickets?per_page=1&page=2&updated_since=2018-03-02T00%3A00%3A00Z",
            "json": [{"id": 4, "updated_at": "2019-01-03T00:00:00Z"}],
            "headers": {
                "Link": '<https://test.freshdesk.com/api/v2/tickets?per_page=1&page=3&updated_since=2018-03-02T00%3A00%3A00Z>; rel="next"'
            },
        },
        {
            "url": "https://test.freshdesk.com/api/v2/tickets?per_page=1&updated_since=2019-01-03T00%3A00%3A00Z",
            "json": [{"id": 4, "updated_at": "2019-01-03T00:00:00Z"}],
            "headers": {
                "Link": '<https://test.freshdesk.com/api/tickets?per_page=1&page=2&updated_since=2019-01-03T00%3A00%3A00Z>; rel="next"'
            },
        },
        {
            "url": "https://test.freshdesk.com/api/v2/tickets?per_page=1&page=2&updated_since=2019-01-03T00%3A00%3A00Z",
            "json": [{"id": 5, "updated_at": "2019-02-03T00:00:00Z"}],
            "headers": {
                "Link": '<https://test.freshdesk.com/api/tickets?per_page=1&page=3&updated_since=2019-01-03T00%3A00%3A00Z>; rel="next"'
            },
        },
        {
            "url": "https://test.freshdesk.com/api/v2/tickets?per_page=1&updated_since=2019-02-03T00%3A00%3A00Z",
            "json": [{"id": 5, "updated_at": "2019-02-03T00:00:00Z"}],
            "headers": {
                "Link": '<https://test.freshdesk.com/api/tickets?per_page=1&page=2&updated_since=2019-02-03T00%3A00%3A00Z>; rel="next"'
            },
        },
        {
            "url": "https://test.freshdesk.com/api/v2/tickets?per_page=1&page=2&updated_since=2019-02-03T00%3A00%3A00Z",
            "json": [{"id": 6, "updated_at": "2019-03-03T00:00:00Z"}],
        },
        {
            "url": "https://test.freshdesk.com/api/v2/tickets?per_page=1&updated_since=2019-03-03T00%3A00%3A00Z",
            "json": [],
        },
    ]


@pytest.mark.skip
class Test300PageLimit:
    def test_not_all_records(self, components_module, requests_mock, authenticator, config, responses):
        """
        TEST 1 - not all records are retrieved

        During test1 the tickets_stream changes the state of parameters on page: 2,
        by updating the params:
        `params["order_by"] = "updated_at"`
        `params["updated_since"] = last_record`
        continues to fetch records from the source, using new cycle, and so on.

        NOTE:
        After switch of the state on ticket_paginate_limit = 2, is this example, we will experience the
        records duplication, because of the last_record state, starting at the point
        where we stoped causes the duplication of the output. The solution for this is to add at least 1 second to the
        last_record state. The DBT normalization should handle this for the end user, so the duplication issue is not a
        blocker in such cases.
        Main pricipal here is: airbyte is at-least-once delivery, but skipping records is data loss.
        """

        expected_output = [
            {"id": 1, "updated_at": "2018-01-02T00:00:00Z"},
            {"id": 2, "updated_at": "2018-02-02T00:00:00Z"},
            {"id": 2, "updated_at": "2018-02-02T00:00:00Z"},  # duplicate
            {"id": 3, "updated_at": "2018-03-02T00:00:00Z"},
            {"id": 3, "updated_at": "2018-03-02T00:00:00Z"},  # duplicate
            {"id": 4, "updated_at": "2019-01-03T00:00:00Z"},
            {"id": 4, "updated_at": "2019-01-03T00:00:00Z"},  # duplicate
            {"id": 5, "updated_at": "2019-02-03T00:00:00Z"},
            {"id": 5, "updated_at": "2019-02-03T00:00:00Z"},  # duplicate
            {"id": 6, "updated_at": "2019-03-03T00:00:00Z"},
        ]

        # Create test_stream instance.
        test_stream = find_stream(components_module, "tickets", config)

        # INT value of page number where the switch state should be triggered.
        # in this test case values from: 1 - 4, assuming we want to switch state on this page.
        test_stream.retriever.paginator.pagination_strategy.PAGE_LIMIT = 2
        # This parameter mocks the "per_page" parameter in the API Call
        test_stream.retriever.paginator.pagination_strategy._page_size = 1

        # Mocking Request
        for response in responses:
            requests_mock.register_uri(
                "GET",
                response["url"],
                json=response["json"],
                headers=response.get("headers", {}),
            )

        records = []
        for slice in test_stream.stream_slices(sync_mode=SyncMode.full_refresh):
            records_generator = test_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=slice)
            records.extend([dict(record) for record in records_generator])

        # We're expecting 6 records to return from the tickets_stream
        assert records == expected_output


class TestFreshdeskTicketsIncrementalSync:
    @pytest.mark.parametrize(
        "stream_state, stream_slice, next_page_token, expected_params",
        [
            ({}, {"partition_field_start": "2022-01-01"}, {"next_page_token": 1}, {"partition_field_start": "2022-01-01"}),
            ({}, {"partition_field_start": "2021-01-01"}, {"next_page_token": "2022-01-01"}, {"partition_field_start": "2022-01-01"}),
        ],
    )
    def test_initialization_and_inheritance(self, components_module, stream_state, stream_slice, next_page_token, expected_params):
        sync = components_module.FreshdeskTicketsIncrementalSync("2022-01-01", "updated_at", "%Y-%m-%d", {}, {})

        # Setup mock for start_time_option.field_name.eval
        with (
            patch.object(sync, "start_time_option") as mock_start_time_option,
            patch.object(sync, "_partition_field_start") as mock_partition_field_start,
        ):
            mock_field_name = MagicMock()
            mock_field_name.eval.return_value = "partition_field_start"

            mock_start_time_option.field_name = mock_field_name
            mock_start_time_option.inject_into = RequestOptionType("request_parameter")

            mock_partition_field_start.eval.return_value = "partition_field_start"

            params = sync.get_request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
            assert params == expected_params


class TestFreshdeskTicketsPaginationStrategy:
    #  returns None when there are fewer records than the page size
    @pytest.mark.parametrize(
        "response, current_page, last_page_size, last_record, expected",
        [
            (requests.Response(), 1, 0, {}, None),  # No records
            (requests.Response(), 1, 3, {"updated_at": "2022-01-05"}, None),  # Fewer records than page size
            (requests.Response(), 3, 4, {"updated_at": "2022-01-05"}, 4),  # Page size records
            (
                requests.Response(),
                6,
                5,
                {"updated_at": "2022-01-05"},
                "2022-01-05",
            ),  # Page limit is hit
        ],
    )
    def test_returns_none_when_fewer_records_than_page_size(
        self, components_module, response, current_page, last_page_size, last_record, expected, config
    ):
        pagination_strategy = components_module.FreshdeskTicketsPaginationStrategy(config=config, page_size=4, parameters={})
        pagination_strategy.PAGE_LIMIT = 5
        pagination_strategy._page = current_page
        assert pagination_strategy.next_page_token(response, last_page_size, last_record, current_page) == expected


@pytest.mark.parametrize(
    "request_params, expected_modified_params, expected_call_credit_cost, requests_per_minute, consume_expected",
    [
        ({"page": "1991-08-24"}, {}, 3, 60, True),  # Rate limiting applied, expect _call_credit.consume to be called
        ({"page": 1}, {"page": 1}, 3, 60, True),  # Rate limiting applied, expect _call_credit.consume to be called
        ({"page": "1991-08-24"}, {}, 3, None, False),  # No rate limiting, do not expect _call_credit.consume to be called
        ({"page": 1}, {"page": 1}, 3, None, False),  # No rate limiting, do not expect _call_credit.consume to be called
    ],
)
def test_freshdesk_tickets_incremental_requester_send_request(
    components_module, request_params, expected_modified_params, expected_call_credit_cost, requests_per_minute, consume_expected
):
    config = {"requests_per_minute": requests_per_minute} if requests_per_minute is not None else {}

    # Initialize the requester with mock config
    requester = components_module.FreshdeskTicketsIncrementalRequester(
        name="tickets", url_base="https://example.com", path="/api/v2/tickets", parameters={}, config=config
    )

    # Patch the HttpRequester.send_request to prevent actual HTTP requests
    with patch.object(components_module.HttpRequester, "send_request", return_value=MagicMock()) as mock_super_send_request:
        # Call send_request with test parameters
        requester.send_request(request_params=request_params)

        # Check if HttpRequester.send_request was called with the modified request_params
        mock_super_send_request.assert_called_once_with(request_params=expected_modified_params)


def _read_full_refresh(stream_instance: Stream):
    records = []
    slices = stream_instance.stream_slices(sync_mode=SyncMode.full_refresh)
    for slice in slices:
        records.extend(list(stream_instance.read_records(stream_slice=slice, sync_mode=SyncMode.full_refresh)))
    return records


def _read_incremental(stream_instance: Stream, stream_state: MutableMapping[str, Any]):
    res = []
    slices = stream_instance.stream_slices(sync_mode=SyncMode.incremental, stream_state=stream_state)
    for slice in slices:
        records = stream_instance.read_records(sync_mode=SyncMode.incremental, stream_slice=slice, stream_state=stream_state)
        for record in records:
            res.append(record)
    return res, stream_instance.state


@pytest.mark.skip
@pytest.mark.parametrize(
    "stream_name, resource",
    [
        ("agents", "agents"),
        ("companies", "companies"),
        ("contacts", "contacts"),
        ("groups", "groups"),
        ("roles", "roles"),
        ("skills", "skills"),
        ("time_entries", "time_entries"),
        ("satisfaction_ratings", "surveys/satisfaction_ratings"),
        ("business_hours", "business_hours"),
        ("canned_response_folders", "canned_response_folders"),
        ("discussion_categories", "discussions/categories"),
        ("email_configs", "email_configs"),
        ("email_mailboxes", "email/mailboxes"),
        ("products", "products"),
        ("scenario_automations", "scenario_automations"),
        ("sla_policies", "sla_policies"),
        ("solution_categories", "solutions/categories"),
        ("ticket_fields", "ticket_fields"),
        ("surveys", "surveys"),
    ],
)
def test_full_refresh(components_module, stream_name, resource, config, requests_mock):
    stream = find_stream(components_module, stream_name, config)
    requests_mock.register_uri("GET", f"/api/v2/{resource}", json=[{"id": x, "updated_at": "2022-05-05T00:00:00Z"} for x in range(25)])

    records = _read_full_refresh(stream)

    assert len(records) == 25


# skipped due to https://github.com/airbytehq/airbyte-internal-issues/issues/6314
@pytest.mark.skip
def test_full_refresh_conversations(components_module, authenticator, config, requests_mock):
    requests_mock.register_uri("GET", "/api/v2/tickets", json=[{"id": x, "updated_at": "2022-05-05T00:00:00Z"} for x in range(5)])
    for i in range(5):
        requests_mock.register_uri("GET", f"/api/v2/tickets/{i}/conversations", json=[{"id": x} for x in range(10)])

    stream = find_stream(components_module, "conversations", config)
    records = _read_full_refresh(stream)

    assert len(records) == 50


@pytest.mark.skip
def test_full_refresh_settings(components_module, config, requests_mock):
    json_resp = {"primary_language": "en", "supported_languages": [], "portal_languages": []}
    requests_mock.register_uri("GET", "/api/v2/settings/helpdesk", json=json_resp)

    stream = find_stream(components_module, "settings", config)
    records = _read_full_refresh(stream)

    assert len(records) == 1
    assert dict(records[0]) == json_resp


# skipped due to https://github.com/airbytehq/airbyte-internal-issues/issues/6314
@pytest.mark.skip
@pytest.mark.parametrize(
    "stream_name, resource",
    [
        ("contacts", "contacts"),
        ("tickets", "tickets"),
        ("satisfaction_ratings", "surveys/satisfaction_ratings"),
    ],
)
def test_incremental(components_module, stream_name, resource, config, requests_mock):
    highest_updated_at = "2022-04-25T22:00:00Z"
    other_updated_at = "2022-04-01T00:00:00Z"
    highest_index = random.randint(0, 24)

    requests_mock.register_uri(
        "GET",
        f"/api/v2/{resource}",
        json=[{"id": x, "updated_at": highest_updated_at if x == highest_index else other_updated_at} for x in range(25)],
    )

    stream = find_stream(components_module, stream_name, config=config)
    records, state = _read_incremental(stream, {})

    assert len(records) == 25
    assert "updated_at" in state
    assert state["updated_at"] == highest_updated_at


@pytest.mark.skip
@pytest.mark.parametrize(
    "stream_name, parent_path, sub_paths",
    [
        ("canned_responses", "canned_response_folders", [f"canned_response_folders/{x}/responses" for x in range(5)]),
        # ("conversations", "tickets", [f"tickets/{x}/conversations" for x in range(5)]), Disabled due to issue with caching
        ("discussion_forums", "discussions/categories", [f"discussions/categories/{x}/forums" for x in range(5)]),
        ("solution_folders", "solutions/categories", [f"solutions/categories/{x}/folders" for x in range(5)]),
    ],
)
def test_substream_full_refresh(components_module, requests_mock, stream_name, parent_path, sub_paths, authenticator, config):
    requests_mock.register_uri("GET", "/api/v2/" + parent_path, json=[{"id": x, "updated_at": "2022-05-05T00:00:00Z"} for x in range(5)])
    for sub_path in sub_paths:
        requests_mock.register_uri("GET", "/api/v2/" + sub_path, json=[{"id": x, "updated_at": "2022-05-05T00:00:00Z"} for x in range(10)])

    stream = find_stream(components_module, stream_name=stream_name, config=config)
    records = _read_full_refresh(stream)

    assert len(records) == 50


@pytest.mark.skip  # Disabled due to issue with caching
@pytest.mark.parametrize(
    "stream_name, parent_path, sub_paths, sub_sub_paths",
    [
        (
            "discussion_topics",
            "discussions/categories",
            [f"discussions/categories/{x}/forums" for x in range(5)],
            [f"discussions/forums/{x}/topics" for x in range(5)],
        ),
        (
            "solution_articles",
            "solutions/categories",
            [f"solutions/categories/{x}/folders" for x in range(5)],
            [f"solutions/folders/{x}/articles" for x in range(5)],
        ),
    ],
)
def test_full_refresh_with_two_sub_levels(components_module, requests_mock, stream_name, parent_path, sub_paths, sub_sub_paths, config):
    requests_mock.register_uri("GET", f"/api/v2/{parent_path}", json=[{"id": x} for x in range(5)])
    for sub_path in sub_paths:
        requests_mock.register_uri("GET", f"/api/v2/{sub_path}", json=[{"id": x} for x in range(5)])
        for sub_sub_path in sub_sub_paths:
            requests_mock.register_uri("GET", f"/api/v2/{sub_sub_path}", json=[{"id": x} for x in range(10)])

    stream = find_stream(components_module, stream_name=stream_name, config=config)
    records = _read_full_refresh(stream)

    assert len(records) == 250


@pytest.mark.skip  # Disabled due to issue with caching
def test_full_refresh_discussion_comments(requests_mock, authenticator, config):
    requests_mock.register_uri("GET", "/api/v2/discussions/categories", json=[{"id": x} for x in range(2)])
    for i in range(2):
        requests_mock.register_uri("GET", f"/api/v2/discussions/categories/{i}/forums", json=[{"id": x} for x in range(3)])
        for j in range(3):
            requests_mock.register_uri("GET", f"/api/v2/discussions/forums/{j}/topics", json=[{"id": x} for x in range(4)])
            for k in range(4):
                requests_mock.register_uri("GET", f"/api/v2/discussions/topics/{k}/comments", json=[{"id": x} for x in range(5)])

    stream = find_stream(stream_name="discussion_comments", config=config)
    records = _read_full_refresh(stream)

    assert len(records) == 120
