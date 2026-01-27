# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

from config_builder import ConfigBuilder
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_SUBDOMAIN = "d3v-airbyte"
_STREAM_NAME = "agent_timeline"
_START_TIME_MICROSECONDS = "1443657600000000"


def _config():
    return ConfigBuilder().subdomain(_SUBDOMAIN).build()


def _timeline_record(agent_id: int, start_time: str, status: str = "online", duration: int = 3600):
    """Create a timeline record with start_time as ISO format string.

    The API returns start_time as ISO format (e.g., '2021-01-01T00:00:00Z').
    The manifest transforms it and uses it for the cursor.
    """
    return {
        "agent_id": agent_id,
        "start_time": start_time,
        "status": status,
        "duration": duration,
    }


def _timeline_response(records: list, count: int = None, next_page: str = None):
    response = {
        "agent_timeline": records,
        "count": count if count is not None else len(records),
    }
    if next_page:
        response["next_page"] = next_page
    return response


class TestAgentTimelineStream(TestCase):
    @HttpMocker()
    def test_404_error_is_ignored(self, http_mocker: HttpMocker):
        """Test that 404 errors are ignored per manifest error handler."""
        http_mocker.get(
            HttpRequest(
                f"https://{_SUBDOMAIN}.zendesk.com/api/v2/chat/incremental/agent_timeline",
                query_params={
                    "fields": "agent_timeline(*)",
                    "limit": "1000",
                    "start_time": _START_TIME_MICROSECONDS,
                },
            ),
            HttpResponse(body=json.dumps({"error": "Not Found"}), status_code=404),
        )

        config = _config()
        source = get_source(config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)

    @HttpMocker()
    def test_full_refresh_returns_records(self, http_mocker: HttpMocker):
        """Test that agent_timeline stream returns records with AddFields transformation.

        The manifest applies AddFields transformation to create an 'id' field from agent_id|start_time.
        The start_time is transformed to ISO format before being used in the id.
        """
        start_time_1 = "2021-01-01T00:00:00Z"
        start_time_2 = "2021-01-01T01:00:00Z"
        records = [
            _timeline_record(1001, start_time_1),
            _timeline_record(1002, start_time_2),
        ]
        http_mocker.get(
            HttpRequest(
                f"https://{_SUBDOMAIN}.zendesk.com/api/v2/chat/incremental/agent_timeline",
                query_params={
                    "fields": "agent_timeline(*)",
                    "limit": "1000",
                    "start_time": _START_TIME_MICROSECONDS,
                },
            ),
            HttpResponse(body=json.dumps(_timeline_response(records, count=2)), status_code=200),
        )

        config = _config()
        source = get_source(config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 2
        record_ids = {r.record.data["id"] for r in output.records}
        assert f"1001|{start_time_1}" in record_ids
        assert f"1002|{start_time_2}" in record_ids

    @HttpMocker()
    def test_incremental_sync_first_sync_no_state(self, http_mocker: HttpMocker):
        """Test incremental sync without prior state (first sync).

        Uses DatetimeBasedCursor with cursor_field: start_time and datetime_format: %epoch_microseconds.
        The start_time request parameter uses the config's start_date converted to epoch microseconds.
        The state stores the cursor value as epoch microseconds string.
        """
        start_time_1 = "2021-01-01T00:00:00Z"
        start_time_2 = "2021-01-01T01:00:00Z"
        start_time_2_microseconds = "1609462800000000"
        records = [
            _timeline_record(1001, start_time_1),
            _timeline_record(1002, start_time_2),
        ]
        http_mocker.get(
            HttpRequest(
                f"https://{_SUBDOMAIN}.zendesk.com/api/v2/chat/incremental/agent_timeline",
                query_params={
                    "fields": "agent_timeline(*)",
                    "limit": "1000",
                    "start_time": _START_TIME_MICROSECONDS,
                },
            ),
            HttpResponse(body=json.dumps(_timeline_response(records, count=2)), status_code=200),
        )

        config = _config()
        source = get_source(config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 2
        assert len(output.state_messages) > 0
        latest_state = output.most_recent_state.stream_state
        assert latest_state.__dict__["start_time"] == start_time_2_microseconds

    @HttpMocker()
    def test_incremental_sync_with_prior_state(self, http_mocker: HttpMocker):
        """Test incremental sync with prior state (second sync).

        When state has start_time cursor, the request uses that value for the start_time parameter.
        Both state and request parameter use epoch microseconds format.
        """
        prior_cursor_microseconds = "1609459200000000"
        new_start_time = "2021-01-01T02:00:00Z"
        new_start_time_microseconds = "1609466400000000"
        records = [_timeline_record(1003, new_start_time)]
        http_mocker.get(
            HttpRequest(
                f"https://{_SUBDOMAIN}.zendesk.com/api/v2/chat/incremental/agent_timeline",
                query_params={
                    "fields": "agent_timeline(*)",
                    "limit": "1000",
                    "start_time": prior_cursor_microseconds,
                },
            ),
            HttpResponse(body=json.dumps(_timeline_response(records, count=1)), status_code=200),
        )

        config = _config()
        state = StateBuilder().with_stream_state(_STREAM_NAME, {"start_time": prior_cursor_microseconds}).build()
        source = get_source(config, state=state)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=config, catalog=catalog, state=state)

        assert len(output.records) == 1
        assert output.records[0].record.data["agent_id"] == 1003
        latest_state = output.most_recent_state.stream_state
        assert latest_state.__dict__["start_time"] == new_start_time_microseconds

    @HttpMocker()
    def test_pagination_with_next_page(self, http_mocker: HttpMocker):
        """Test pagination using next_page URL (RequestPath pagination).

        Pagination uses CursorPagination with cursor_value from response.next_page
        and stops when count < 1000. The next_page URL includes all query params.

        NOTE: This test validates next_page URL pagination which is also used by the 'chats' stream.
        Both streams use the same DefaultPaginator configuration with RequestPath page_token_option,
        so this test provides pagination coverage for both streams.
        """
        next_page_url = (
            f"https://{_SUBDOMAIN}.zendesk.com/api/v2/chat/incremental/agent_timeline"
            "?cursor=abc123&fields=agent_timeline%28%2A%29&limit=1000"
        )
        page1_records = [_timeline_record(1001, "2021-01-01T00:00:00Z")]
        page2_records = [_timeline_record(1002, "2021-01-01T01:00:00Z")]

        http_mocker.get(
            HttpRequest(
                f"https://{_SUBDOMAIN}.zendesk.com/api/v2/chat/incremental/agent_timeline",
                query_params={
                    "fields": "agent_timeline(*)",
                    "limit": "1000",
                    "start_time": _START_TIME_MICROSECONDS,
                },
            ),
            HttpResponse(
                body=json.dumps(_timeline_response(page1_records, count=1000, next_page=next_page_url)),
                status_code=200,
            ),
        )
        http_mocker.get(
            HttpRequest(next_page_url),
            HttpResponse(body=json.dumps(_timeline_response(page2_records, count=1)), status_code=200),
        )

        config = _config()
        source = get_source(config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 2
        agent_ids = {r.record.data["agent_id"] for r in output.records}
        assert agent_ids == {1001, 1002}
