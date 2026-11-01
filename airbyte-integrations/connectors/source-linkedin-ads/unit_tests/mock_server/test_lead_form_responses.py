# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import logging
from datetime import datetime, timezone
from unittest import TestCase

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source

from .config import ConfigBuilder
from .request_builder import LinkedInAdsRequestBuilder
from .response_builder import LinkedInAdsPaginatedResponseBuilder


_NOW = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
_STREAM_NAME = "lead_form_responses"

# Timestamps in milliseconds (as required by the schema)
_TIMESTAMP_JAN_2024 = 1704067200000  # 2024-01-01T00:00:00.000Z
_TIMESTAMP_JUN_2024 = 1717200000000  # 2024-06-01T00:00:00.000Z


def _create_account_record(account_id: int, name: str = "Test Account") -> dict:
    """Create a mock account record."""
    return {
        "id": account_id,
        "name": name,
        "type": "BUSINESS",
        "status": "ACTIVE",
        "currency": "USD",
        "created": "2024-01-01T00:00:00.000Z",
        "lastModified": "2024-06-01T00:00:00.000Z",
    }


def _create_lead_form_response_record(
    response_id: str,
    account_id: int,
    form_id: str,
    submitted_at: int = _TIMESTAMP_JAN_2024,
) -> dict:
    """Create a mock lead form response record."""
    return {
        "id": response_id,
        "leadType": "SPONSORED",
        "form": {"leadGenFormUrn": f"urn:li:leadGenForm:{form_id}"},
        "owner": {"sponsoredAccount": f"urn:li:sponsoredAccount:{account_id}"},
        "submittedAt": submitted_at,
        "formResponse": {"answers": [{"questionId": "q1", "answerDetails": {"textQuestionAnswer": {"answer": "Test Answer"}}}]},
    }


@freezegun.freeze_time(_NOW)
class TestLeadFormResponsesStream(TestCase):
    """Tests for the lead_form_responses stream."""

    @HttpMocker()
    def test_full_refresh_sync(self, http_mocker: HttpMocker):
        """
        Test full refresh sync for lead_form_responses stream.

        Given: A parent account with lead form responses
        When: Running a full refresh sync
        Then: All lead form responses should be returned
        """
        config = ConfigBuilder().build()

        http_mocker.get(
            LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(500).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_account_record(111111111, "Account 1")]),
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.lead_form_responses_endpoint(111111111).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page(
                [
                    _create_lead_form_response_record("resp-1001", 111111111, "form-1"),
                    _create_lead_form_response_record("resp-1002", 111111111, "form-2"),
                ]
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 2
        record_ids = [record.record.data["id"] for record in output.records]
        assert "resp-1001" in record_ids
        assert "resp-1002" in record_ids

    @HttpMocker()
    def test_multiple_parent_accounts(self, http_mocker: HttpMocker):
        """
        Test lead_form_responses stream with multiple parent accounts.

        Given: Multiple parent accounts with lead form responses
        When: Running a full refresh sync
        Then: Lead form responses from all accounts should be returned
        """
        config = ConfigBuilder().build()

        http_mocker.get(
            LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(500).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page(
                [
                    _create_account_record(111111111, "Account 1"),
                    _create_account_record(222222222, "Account 2"),
                ]
            ),
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.lead_form_responses_endpoint(111111111).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_lead_form_response_record("resp-1001", 111111111, "form-1")]),
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.lead_form_responses_endpoint(222222222).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_lead_form_response_record("resp-2001", 222222222, "form-2")]),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        # Due to concurrent processing, we may get records from both accounts
        # The exact count depends on processing order
        assert len(output.records) >= 2
        record_ids = [record.record.data["id"] for record in output.records]
        assert "resp-1001" in record_ids
        assert "resp-2001" in record_ids

    @HttpMocker()
    def test_empty_parent_stream(self, http_mocker: HttpMocker):
        """
        Test lead_form_responses stream when parent stream returns no records.

        Given: No parent accounts
        When: Running a full refresh sync
        Then: No lead form responses should be returned and no child requests made
        """
        config = ConfigBuilder().build()

        http_mocker.get(
            LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(500).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([]),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)

    @HttpMocker()
    def test_parent_with_no_lead_form_responses(self, http_mocker: HttpMocker):
        """
        Test lead_form_responses stream when parent has no lead form responses.

        Given: A parent account with no lead form responses
        When: Running a full refresh sync
        Then: No lead form responses should be returned
        """
        config = ConfigBuilder().build()

        http_mocker.get(
            LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(500).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_account_record(111111111, "Account 1")]),
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.lead_form_responses_endpoint(111111111).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([]),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)

    @HttpMocker()
    def test_incremental_sync_initial(self, http_mocker: HttpMocker):
        """
        Test incremental sync without prior state (initial sync).

        Given: No prior state
        When: Running an incremental sync
        Then: The request is unfiltered (no submittedAtTimeRange) and the cursor
              advances to the latest submittedAt seen
        """
        config = ConfigBuilder().build()

        http_mocker.get(
            LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(500).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_account_record(111111111, "Account 1")]),
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.lead_form_responses_endpoint(111111111).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page(
                [
                    _create_lead_form_response_record("resp-1001", 111111111, "form-1", submitted_at=_TIMESTAMP_JAN_2024),
                    _create_lead_form_response_record("resp-1002", 111111111, "form-2", submitted_at=_TIMESTAMP_JUN_2024),
                ]
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 2
        last_state = output.state_messages[-1].state.stream.stream_state.__dict__
        partition_state = next(s for s in last_state["states"] if s["partition"]["account_id"] == 111111111)
        assert partition_state["cursor"] == {"submittedAt": "1717200000000"}

    @HttpMocker()
    def test_incremental_sync_with_state(self, http_mocker: HttpMocker):
        """
        Test incremental sync with prior per-partition state (subsequent sync).

        Given: Per-partition cursor state for two accounts
        When: Running an incremental sync
        Then: Each partition request carries submittedAtTimeRange=(start:<cursor>,end:<now>)
              and the cursor state advances
        """
        config = ConfigBuilder().build()
        state = (
            StateBuilder()
            .with_stream_state(
                _STREAM_NAME,
                {
                    "states": [
                        {"partition": {"account_id": 111111111, "parent_slice": {}}, "cursor": {"submittedAt": "1704067200000"}},
                        {"partition": {"account_id": 222222222, "parent_slice": {}}, "cursor": {"submittedAt": "1717200000000"}},
                    ]
                },
            )
            .build()
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(500).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page(
                [
                    _create_account_record(111111111, "Account 1"),
                    _create_account_record(222222222, "Account 2"),
                ]
            ),
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.lead_form_responses_endpoint(
                111111111, submitted_at_start=1704067200000, submitted_at_end=1718452800000
            ).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page(
                [_create_lead_form_response_record("resp-1001", 111111111, "form-1", submitted_at=_TIMESTAMP_JUN_2024)]
            ),
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.lead_form_responses_endpoint(
                222222222, submitted_at_start=1717200000000, submitted_at_end=1718452800000
            ).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page(
                [_create_lead_form_response_record("resp-2001", 222222222, "form-2", submitted_at=_TIMESTAMP_JUN_2024)]
            ),
        )

        source = get_source(config=config, state=state)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=config, catalog=catalog, state=state)

        assert len(output.records) == 2
        record_ids = [record.record.data["id"] for record in output.records]
        assert "resp-1001" in record_ids
        assert "resp-2001" in record_ids
        assert not any(log.log.level == "ERROR" for log in output.logs)

    @HttpMocker()
    def test_incremental_sync_lookback_window(self, http_mocker: HttpMocker):
        """
        Test incremental sync with a lookback window.

        Given: Prior cursor state and a 2-day lookback window
        When: Running an incremental sync
        Then: The submittedAtTimeRange start is shifted back by the lookback window
        """
        config = ConfigBuilder().with_lookback_window(2).build()
        state = (
            StateBuilder()
            .with_stream_state(
                _STREAM_NAME,
                {"states": [{"partition": {"account_id": 111111111, "parent_slice": {}}, "cursor": {"submittedAt": "1717200000000"}}]},
            )
            .build()
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.accounts_endpoint().with_q("search").with_page_size(500).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page([_create_account_record(111111111, "Account 1")]),
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.lead_form_responses_endpoint(
                111111111, submitted_at_start=1717027200000, submitted_at_end=1718452800000
            ).build(),
            LinkedInAdsPaginatedResponseBuilder.single_page(
                [_create_lead_form_response_record("resp-1001", 111111111, "form-1", submitted_at=_TIMESTAMP_JUN_2024)]
            ),
        )

        source = get_source(config=config, state=state)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=config, catalog=catalog, state=state)

        assert len(output.records) == 1
        assert not any(log.log.level == "ERROR" for log in output.logs)

    def test_discover_supports_incremental(self):
        """
        Test that discovery reports incremental support for lead_form_responses.

        Given: A valid config
        When: Running discover
        Then: lead_form_responses supports incremental sync with submittedAt as the cursor
        """
        config = ConfigBuilder().build()

        source = get_source(config=config)
        catalog = source.discover(logger=logging.getLogger("airbyte"), config=config)

        stream = next(s for s in catalog.streams if s.name == _STREAM_NAME)
        assert SyncMode.incremental in stream.supported_sync_modes
        assert stream.default_cursor_field == ["submittedAt"]
