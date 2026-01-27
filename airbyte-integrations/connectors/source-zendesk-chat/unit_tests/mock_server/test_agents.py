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


_STREAM_NAME = "agents"
_SUBDOMAIN = "d3v-airbyte"


def _config():
    return ConfigBuilder().subdomain(_SUBDOMAIN).build()


def _agent_record(agent_id: int, name: str):
    return {
        "id": agent_id,
        "first_name": name,
        "last_name": "Test",
        "display_name": f"{name} Test",
        "email": f"{name.lower()}@example.com",
        "enabled": True,
        "create_date": "2020-01-15T10:00:00Z",
        "role_id": 1,
        "departments": [1, 2],
    }


class TestAgentsStream(TestCase):
    @HttpMocker()
    def test_full_refresh_returns_records(self, http_mocker: HttpMocker):
        """Test that agents stream returns array of agent records."""
        records = [_agent_record(1, "Alice"), _agent_record(2, "Bob")]
        http_mocker.get(
            HttpRequest(
                f"https://{_SUBDOMAIN}.zendesk.com/api/v2/chat/agents",
                query_params={"limit": "100", "since_id": "0"},
            ),
            HttpResponse(body=json.dumps(records), status_code=200),
        )

        config = _config()
        source = get_source(config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 2
        assert {r.record.data["id"] for r in output.records} == {1, 2}

    @HttpMocker()
    def test_pagination_fetches_multiple_pages(self, http_mocker: HttpMocker):
        """Test that agents stream paginates using since_id cursor.

        Pagination uses cursor_value: {{ last_record['id'] + 1 }} and stops when response is empty.

        NOTE: This test validates since_id cursor pagination which is also used by the 'bans' stream.
        Both streams use the same DefaultPaginator configuration with since_id cursor, so this test
        provides pagination coverage for both streams.
        """
        page1_records = [_agent_record(1, "Agent1"), _agent_record(2, "Agent2")]
        page2_records = [_agent_record(3, "Agent3")]

        http_mocker.get(
            HttpRequest(
                f"https://{_SUBDOMAIN}.zendesk.com/api/v2/chat/agents",
                query_params={"limit": "100", "since_id": "0"},
            ),
            HttpResponse(body=json.dumps(page1_records), status_code=200),
        )
        http_mocker.get(
            HttpRequest(
                f"https://{_SUBDOMAIN}.zendesk.com/api/v2/chat/agents",
                query_params={"limit": "100", "since_id": "3"},
            ),
            HttpResponse(body=json.dumps(page2_records), status_code=200),
        )
        http_mocker.get(
            HttpRequest(
                f"https://{_SUBDOMAIN}.zendesk.com/api/v2/chat/agents",
                query_params={"limit": "100", "since_id": "4"},
            ),
            HttpResponse(body=json.dumps([]), status_code=200),
        )

        config = _config()
        source = get_source(config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 3
        assert {r.record.data["id"] for r in output.records} == {1, 2, 3}

    @HttpMocker()
    def test_incremental_sync_first_sync_no_state(self, http_mocker: HttpMocker):
        """Test incremental sync without prior state (first sync).

        The paginator uses cursor_value: {{ last_record['id'] + 1 }} and stop_condition: {{ not last_record }}.
        So after reading records, it requests the next page with since_id = last_record_id + 1.
        When the response is empty, pagination stops.
        """
        records = [_agent_record(1, "Alice"), _agent_record(2, "Bob")]
        http_mocker.get(
            HttpRequest(
                f"https://{_SUBDOMAIN}.zendesk.com/api/v2/chat/agents",
                query_params={"limit": "100", "since_id": "0"},
            ),
            HttpResponse(body=json.dumps(records), status_code=200),
        )
        http_mocker.get(
            HttpRequest(
                f"https://{_SUBDOMAIN}.zendesk.com/api/v2/chat/agents",
                query_params={"limit": "100", "since_id": "3"},
            ),
            HttpResponse(body=json.dumps([]), status_code=200),
        )

        config = _config()
        source = get_source(config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 2
        assert len(output.state_messages) > 0
        latest_state = output.most_recent_state.stream_state
        assert latest_state.__dict__["id"] == 2

    @HttpMocker()
    def test_incremental_sync_with_prior_state(self, http_mocker: HttpMocker):
        """Test incremental sync with prior state (second sync).

        When state has id=2, the request uses since_id=2 (from start_value_option).
        After reading records, pagination continues with since_id = last_record_id + 1.
        """
        records = [_agent_record(3, "Charlie")]
        http_mocker.get(
            HttpRequest(
                f"https://{_SUBDOMAIN}.zendesk.com/api/v2/chat/agents",
                query_params={"limit": "100", "since_id": "2"},
            ),
            HttpResponse(body=json.dumps(records), status_code=200),
        )
        http_mocker.get(
            HttpRequest(
                f"https://{_SUBDOMAIN}.zendesk.com/api/v2/chat/agents",
                query_params={"limit": "100", "since_id": "4"},
            ),
            HttpResponse(body=json.dumps([]), status_code=200),
        )

        config = _config()
        state = StateBuilder().with_stream_state(_STREAM_NAME, {"id": 2}).build()
        source = get_source(config, state=state)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=config, catalog=catalog, state=state)

        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 3
        latest_state = output.most_recent_state.stream_state
        assert latest_state.__dict__["id"] == 3

    @HttpMocker()
    def test_404_error_is_ignored(self, http_mocker: HttpMocker):
        """Test that 404 errors are ignored per the manifest error handler configuration.

        The error handler in manifest.yaml uses only http_codes: [404] filter with IGNORE action.
        There is no error_message_contains filter, so error message assertion is not applicable.
        We verify: (1) zero records returned, and (2) no ERROR level logs emitted.

        NOTE: This error handler configuration is shared by all streams in this connector,
        so this test provides error handling coverage for all streams.
        """
        http_mocker.get(
            HttpRequest(
                f"https://{_SUBDOMAIN}.zendesk.com/api/v2/chat/agents",
                query_params={"limit": "100", "since_id": "0"},
            ),
            HttpResponse(
                body=json.dumps({"error": {"message": "Not Found"}}),
                status_code=404,
            ),
        )

        config = _config()
        source = get_source(config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
