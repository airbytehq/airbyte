#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import json
from datetime import datetime, timedelta, timezone
from unittest import TestCase

import freezegun
from unit_tests.conftest import get_source

from airbyte_cdk.models import ConfiguredAirbyteCatalog, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import (
    FieldPath,
    HttpResponseBuilder,
    NestedPath,
    RecordBuilder,
    create_record_builder,
    create_response_builder,
    find_template,
)
from airbyte_cdk.test.state_builder import StateBuilder
from integration.config import ConfigBuilder
from integration.pagination import StripePaginationStrategy
from integration.request_builder import StripeRequestBuilder


_STREAM_NAME = "charges"
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
_DATA_FIELD = NestedPath(["data", "object"])
_ACCOUNT_ID = "account_id"
_CLIENT_SECRET = "client_secret"
_NOW = datetime.now(timezone.utc)
_A_CHARGE = {"id": "ch_hydrated", "object": "charge", "amount": 100, "currency": "usd", "created": int(_NOW.timestamp())}


def _config() -> ConfigBuilder:
    return (
        ConfigBuilder()
        .with_start_date(_NOW - timedelta(days=75))
        .with_account_id(_ACCOUNT_ID)
        .with_client_secret(_CLIENT_SECRET)
        .with_slice_range_in_days(365)
    )


def _catalog() -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()


def _events_request() -> StripeRequestBuilder:
    return StripeRequestBuilder.events_endpoint(_ACCOUNT_ID, _CLIENT_SECRET)


def _charge_request(charge_id: str) -> StripeRequestBuilder:
    return StripeRequestBuilder._for_endpoint(f"charges/{charge_id}", _ACCOUNT_ID, _CLIENT_SECRET)


def _an_event() -> RecordBuilder:
    return create_record_builder(
        find_template("events", __file__),
        FieldPath("data"),
        record_id_path=FieldPath("id"),
        record_cursor_path=FieldPath("created"),
    )


def _events_response() -> HttpResponseBuilder:
    return create_response_builder(find_template("events", __file__), FieldPath("data"), pagination_strategy=StripePaginationStrategy())


@freezegun.freeze_time(_NOW.isoformat())
class ChargesHydratedTest(TestCase):
    @HttpMocker()
    def test_given_hydrated_mode_when_read_then_expand_refunds_without_list_prefix(self, http_mocker: HttpMocker) -> None:
        state_datetime = _NOW - timedelta(days=5)
        cursor_value = int(state_datetime.timestamp()) + 1
        hydrated_charge = {**_A_CHARGE, "description": "fresh-from-endpoint"}

        http_mocker.get(
            _events_request().with_created_gte(state_datetime).with_created_lte(_NOW).with_limit(100).with_types(_EVENT_TYPES).build(),
            _events_response()
            .with_record(
                _an_event().with_cursor(cursor_value).with_field(FieldPath("type"), "charge.updated").with_field(_DATA_FIELD, _A_CHARGE)
            )
            .build(),
        )
        # `refunds`, not `data.refunds`: the `data.` prefix is only valid on list requests.
        http_mocker.get(
            _charge_request("ch_hydrated").with_expands(["refunds"]).build(),
            HttpResponse(json.dumps(hydrated_charge), 200),
        )

        config = _config().with_event_based_incremental_sync_mode("hydrated_events").build()
        state = StateBuilder().with_stream_state(_STREAM_NAME, {"updated": int(state_datetime.timestamp())}).build()
        output = read(get_source(config=config, state=state), config=config, catalog=_catalog(), state=state)

        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "ch_hydrated"
        assert output.records[0].record.data["description"] == "fresh-from-endpoint"
