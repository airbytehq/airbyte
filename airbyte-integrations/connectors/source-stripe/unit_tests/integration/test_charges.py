#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from unittest import TestCase

import freezegun
from unit_tests.conftest import get_source

from airbyte_cdk.models import ConfiguredAirbyteCatalog, StreamDescriptor, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from integration.config import ConfigBuilder
from integration.request_builder import StripeRequestBuilder


_EVENT_TYPES = [
    "charge.captured",
    "charge.expired",
    "charge.failed",
    "charge.pending",
    "charge.refunded",
    "charge.refund.updated",
    "charge.succeeded",
    "charge.updated",
]
_EXPANDS = ["refunds"]
_STREAM_NAME = "charges"
_NOW = datetime.now(timezone.utc)
_ACCOUNT_ID = "account_id"
_CLIENT_SECRET = "client_secret"


def _charge_request(charge_id: str) -> StripeRequestBuilder:
    return StripeRequestBuilder.charge_endpoint(charge_id, _ACCOUNT_ID, _CLIENT_SECRET)


def _events_request() -> StripeRequestBuilder:
    return StripeRequestBuilder.events_endpoint(_ACCOUNT_ID, _CLIENT_SECRET)


def _config() -> ConfigBuilder:
    return (
        ConfigBuilder()
        .with_start_date(_NOW - timedelta(days=75))
        .with_account_id(_ACCOUNT_ID)
        .with_client_secret(_CLIENT_SECRET)
        .with_slice_range_in_days(365)
    )


def _catalog(sync_mode: SyncMode) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(_STREAM_NAME, sync_mode).build()


def _read(config_builder: ConfigBuilder, state: Optional[Dict[str, Any]] = None) -> EntrypointOutput:
    catalog = _catalog(SyncMode.incremental)
    config = config_builder.build()
    return read(get_source(config, state), config, catalog, state)


@freezegun.freeze_time(_NOW.isoformat())
class IncrementalTest(TestCase):
    @HttpMocker()
    def test_given_incremental_event_when_read_then_refresh_charge_from_detail_endpoint(self, http_mocker: HttpMocker) -> None:
        state_datetime = _NOW - timedelta(days=5)
        cursor_value = int(state_datetime.timestamp()) + 1
        charge_id = "ch_123"

        event_response = {
            "object": "list",
            "has_more": False,
            "data": [
                {
                    "id": "evt_123",
                    "object": "event",
                    "created": cursor_value,
                    "type": "charge.updated",
                    "data": {
                        "object": {
                            "id": charge_id,
                            "object": "charge",
                            "created": 1,
                            "refunds": "re_should_be_replaced",
                        }
                    },
                }
            ],
        }
        refreshed_charge = {
            "id": charge_id,
            "object": "charge",
            "created": 1,
            "refunds": {
                "object": "list",
                "data": [{"id": "re_123", "object": "refund"}],
                "has_more": False,
                "url": f"/v1/charges/{charge_id}/refunds",
            },
        }

        http_mocker.get(
            _events_request().with_created_gte(state_datetime).with_created_lte(_NOW).with_limit(100).with_types(_EVENT_TYPES).build(),
            HttpResponse(json.dumps(event_response), 200),
        )
        http_mocker.get(
            _charge_request(charge_id).with_expands(_EXPANDS).build(),
            HttpResponse(json.dumps(refreshed_charge), 200),
        )

        output = _read(
            _config(),
            StateBuilder().with_stream_state(_STREAM_NAME, {"updated": int(state_datetime.timestamp())}).build(),
        )

        record = output.records[0].record.data
        most_recent_state = output.most_recent_state

        assert record["refunds"]["object"] == "list"
        assert record["updated"] == cursor_value
        assert most_recent_state.stream_descriptor == StreamDescriptor(name=_STREAM_NAME)
        assert most_recent_state.stream_state.updated == str(cursor_value)
