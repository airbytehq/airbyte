#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import json
from pathlib import Path

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source

from .config import ConfigBuilder
from .response_builder import EmptyResponseBuilder


_STREAM_NAME = "bounces"
_BASE_URL = "https://api.sendgrid.com"


def _get_response(filename: str) -> str:
    response_path = Path(__file__).parent.parent / "resource" / "http" / "response" / filename
    return response_path.read_text()


def _create_catalog(sync_mode: SyncMode = SyncMode.full_refresh):
    return CatalogBuilder().with_stream(name=_STREAM_NAME, sync_mode=sync_mode).build()


@freezegun.freeze_time("2024-01-15T00:00:00Z")
class TestBouncesStream:
    """
    Tests for the bounces stream with offset pagination and incremental sync.
    This stream uses the same paginator as blocks, spam_reports, global_suppressions, and invalid_emails.
    Pagination tests here also validate the same behavior for those streams.
    """

    def test_read_full_refresh_single_page(self):
        """Test basic full refresh sync with a single page of results."""
        config = ConfigBuilder().build()

        with HttpMocker() as http_mocker:
            http_mocker.get(
                HttpRequest(
                    url=f"{_BASE_URL}/v3/suppression/bounces",
                    query_params={
                        "limit": "500",
                        "offset": "0",
                        "start_time": "1704067200",
                        "end_time": "1705276800",
                    },
                ),
                HttpResponse(body=_get_response("bounces.json"), status_code=200),
            )

            source = get_source(config)
            actual_messages = read(source, config=config, catalog=_create_catalog())

            assert len(actual_messages.records) == 1
            assert actual_messages.records[0].record.data["email"] == "bounce@example.com"
            assert actual_messages.records[0].record.data["created"] == 1704067200
            assert actual_messages.records[0].record.data["status"] == "5.1.1"

    def test_read_full_refresh_with_pagination(self):
        """Test full refresh sync with multiple pages using offset pagination."""
        config = ConfigBuilder().build()

        with HttpMocker() as http_mocker:
            # First page - return 500 records to trigger pagination
            first_page_records = json.loads(_get_response("bounces.json")) * 500
            http_mocker.get(
                HttpRequest(
                    url=f"{_BASE_URL}/v3/suppression/bounces",
                    query_params={
                        "limit": "500",
                        "offset": "0",
                        "start_time": "1704067200",
                        "end_time": "1705276800",
                    },
                ),
                HttpResponse(body=json.dumps(first_page_records), status_code=200),
            )

            # Second page - return fewer records to stop pagination
            http_mocker.get(
                HttpRequest(
                    url=f"{_BASE_URL}/v3/suppression/bounces",
                    query_params={
                        "limit": "500",
                        "offset": "500",
                        "start_time": "1704067200",
                        "end_time": "1705276800",
                    },
                ),
                HttpResponse(body=_get_response("bounces.json"), status_code=200),
            )

            source = get_source(config)
            actual_messages = read(source, config=config, catalog=_create_catalog())

            assert len(actual_messages.records) == 501

    def test_read_incremental_first_sync_emits_state(self):
        """Test incremental sync on first sync (no prior state) emits state message."""
        config = ConfigBuilder().build()

        with HttpMocker() as http_mocker:
            http_mocker.get(
                HttpRequest(
                    url=f"{_BASE_URL}/v3/suppression/bounces",
                    query_params={
                        "limit": "500",
                        "offset": "0",
                        "start_time": "1704067200",
                        "end_time": "1705276800",
                    },
                ),
                HttpResponse(body=_get_response("bounces.json"), status_code=200),
            )

            source = get_source(config)
            actual_messages = read(
                source,
                config=config,
                catalog=_create_catalog(sync_mode=SyncMode.incremental),
            )

            assert len(actual_messages.records) == 1
            assert len(actual_messages.state_messages) > 0
            state_data = actual_messages.state_messages[-1].state.stream.stream_state
            assert hasattr(state_data, "created") or "created" in state_data.__dict__

    def test_read_incremental_with_prior_state(self):
        """Test incremental sync with existing state uses state for start_time."""
        config = ConfigBuilder().build()
        state = StateBuilder().with_stream_state(_STREAM_NAME, {"created": 1704844800}).build()

        with HttpMocker() as http_mocker:
            http_mocker.get(
                HttpRequest(
                    url=f"{_BASE_URL}/v3/suppression/bounces",
                    query_params={
                        "limit": "500",
                        "offset": "0",
                        "start_time": "1704844800",
                        "end_time": "1705276800",
                    },
                ),
                HttpResponse(body=_get_response("bounces.json"), status_code=200),
            )

            source = get_source(config, state=state)
            actual_messages = read(
                source,
                config=config,
                catalog=_create_catalog(sync_mode=SyncMode.incremental),
                state=state,
            )

            assert len(actual_messages.records) == 1

    def test_read_empty_results_no_errors(self):
        """Test that empty results don't produce errors in logs."""
        config = ConfigBuilder().build()

        with HttpMocker() as http_mocker:
            http_mocker.get(
                HttpRequest(
                    url=f"{_BASE_URL}/v3/suppression/bounces",
                    query_params={
                        "limit": "500",
                        "offset": "0",
                        "start_time": "1704067200",
                        "end_time": "1705276800",
                    },
                ),
                EmptyResponseBuilder(is_array=True).build(),
            )

            source = get_source(config)
            actual_messages = read(source, config=config, catalog=_create_catalog())

            assert len(actual_messages.records) == 0
            assert len(actual_messages.errors) == 0
            for log in actual_messages.logs:
                assert "error" not in log.log.message.lower()
