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
_STREAM_NAME = "bans"


def _config():
    return ConfigBuilder().subdomain(_SUBDOMAIN).build()


def _ban_record(ban_id: int, ban_type: str, reason: str, created_at: str):
    return {
        "id": ban_id,
        "type": ban_type,
        "reason": reason,
        "created_at": created_at,
    }


def _bans_response(ip_address_bans: list, visitor_bans: list):
    return {"ip_address": ip_address_bans, "visitor": visitor_bans}


class TestBansStream(TestCase):
    @HttpMocker()
    def test_full_refresh_returns_records(self, http_mocker: HttpMocker):
        """Test that bans stream returns records from both ip_address and visitor arrays."""
        ip_bans = [_ban_record(1, "ip_address", "spam", "2024-01-01T10:00:00Z")]
        visitor_bans = [_ban_record(2, "visitor", "abuse", "2024-01-02T10:00:00Z")]
        http_mocker.get(
            HttpRequest(
                f"https://{_SUBDOMAIN}.zendesk.com/api/v2/chat/bans",
                query_params={"limit": "100", "since_id": "0"},
            ),
            HttpResponse(body=json.dumps(_bans_response(ip_bans, visitor_bans)), status_code=200),
        )
        http_mocker.get(
            HttpRequest(
                f"https://{_SUBDOMAIN}.zendesk.com/api/v2/chat/bans",
                query_params={"limit": "100", "since_id": "3"},
            ),
            HttpResponse(body=json.dumps(_bans_response([], [])), status_code=200),
        )

        config = _config()
        source = get_source(config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 2
        record_ids = {r.record.data["id"] for r in output.records}
        assert record_ids == {1, 2}

    @HttpMocker()
    def test_records_sorted_by_created_at(self, http_mocker: HttpMocker):
        """Test that bans are sorted by created_at timestamp (extractor behavior)."""
        ip_bans = [_ban_record(2, "ip_address", "spam", "2024-01-02T10:00:00Z")]
        visitor_bans = [_ban_record(1, "visitor", "abuse", "2024-01-01T10:00:00Z")]
        http_mocker.get(
            HttpRequest(
                f"https://{_SUBDOMAIN}.zendesk.com/api/v2/chat/bans",
                query_params={"limit": "100", "since_id": "0"},
            ),
            HttpResponse(body=json.dumps(_bans_response(ip_bans, visitor_bans)), status_code=200),
        )
        http_mocker.get(
            HttpRequest(
                f"https://{_SUBDOMAIN}.zendesk.com/api/v2/chat/bans",
                query_params={"limit": "100", "since_id": "3"},
            ),
            HttpResponse(body=json.dumps(_bans_response([], [])), status_code=200),
        )

        config = _config()
        source = get_source(config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 2
        record_ids = [r.record.data["id"] for r in output.records]
        assert record_ids == [1, 2]

    @HttpMocker()
    def test_pagination_fetches_multiple_pages(self, http_mocker: HttpMocker):
        """Test that bans stream paginates using since_id cursor.

        Pagination uses cursor_value: {{ last_record['id'] + 1 }} and stops when response is empty.
        """
        page1_ip = [_ban_record(1, "ip_address", "spam", "2024-01-01T10:00:00Z")]
        page1_visitor = [_ban_record(2, "visitor", "abuse", "2024-01-02T10:00:00Z")]
        page2_ip = [_ban_record(3, "ip_address", "bot", "2024-01-03T10:00:00Z")]

        http_mocker.get(
            HttpRequest(
                f"https://{_SUBDOMAIN}.zendesk.com/api/v2/chat/bans",
                query_params={"limit": "100", "since_id": "0"},
            ),
            HttpResponse(body=json.dumps(_bans_response(page1_ip, page1_visitor)), status_code=200),
        )
        http_mocker.get(
            HttpRequest(
                f"https://{_SUBDOMAIN}.zendesk.com/api/v2/chat/bans",
                query_params={"limit": "100", "since_id": "3"},
            ),
            HttpResponse(body=json.dumps(_bans_response(page2_ip, [])), status_code=200),
        )
        http_mocker.get(
            HttpRequest(
                f"https://{_SUBDOMAIN}.zendesk.com/api/v2/chat/bans",
                query_params={"limit": "100", "since_id": "4"},
            ),
            HttpResponse(body=json.dumps(_bans_response([], [])), status_code=200),
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
        """
        ip_bans = [_ban_record(1, "ip_address", "spam", "2024-01-01T10:00:00Z")]
        visitor_bans = [_ban_record(2, "visitor", "abuse", "2024-01-02T10:00:00Z")]
        http_mocker.get(
            HttpRequest(
                f"https://{_SUBDOMAIN}.zendesk.com/api/v2/chat/bans",
                query_params={"limit": "100", "since_id": "0"},
            ),
            HttpResponse(body=json.dumps(_bans_response(ip_bans, visitor_bans)), status_code=200),
        )
        http_mocker.get(
            HttpRequest(
                f"https://{_SUBDOMAIN}.zendesk.com/api/v2/chat/bans",
                query_params={"limit": "100", "since_id": "3"},
            ),
            HttpResponse(body=json.dumps(_bans_response([], [])), status_code=200),
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
        """
        ip_bans = [_ban_record(3, "ip_address", "bot", "2024-01-03T10:00:00Z")]
        http_mocker.get(
            HttpRequest(
                f"https://{_SUBDOMAIN}.zendesk.com/api/v2/chat/bans",
                query_params={"limit": "100", "since_id": "2"},
            ),
            HttpResponse(body=json.dumps(_bans_response(ip_bans, [])), status_code=200),
        )
        http_mocker.get(
            HttpRequest(
                f"https://{_SUBDOMAIN}.zendesk.com/api/v2/chat/bans",
                query_params={"limit": "100", "since_id": "4"},
            ),
            HttpResponse(body=json.dumps(_bans_response([], [])), status_code=200),
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
        """Test that 404 errors are ignored per manifest error handler."""
        http_mocker.get(
            HttpRequest(
                f"https://{_SUBDOMAIN}.zendesk.com/api/v2/chat/bans",
                query_params={"limit": "100", "since_id": "0"},
            ),
            HttpResponse(body=json.dumps({"error": "Not Found"}), status_code=404),
        )

        config = _config()
        source = get_source(config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
