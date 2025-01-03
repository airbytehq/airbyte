# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from unittest import TestCase

import freezegun
from source_stripe import SourceStripe

from airbyte_cdk.models import AirbyteStateBlob, ConfiguredAirbyteCatalog, StreamDescriptor, SyncMode
from airbyte_cdk.sources.source import TState
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker
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


_EVENT_TYPES = [
    "setup_intent.canceled",
    "setup_intent.created",
    "setup_intent.requires_action",
    "setup_intent.setup_failed",
    "setup_intent.succeeded",
]

_DATA_FIELD = NestedPath(["data", "object"])
_STREAM_NAME = "setup_attempts"
_NOW = datetime.now(timezone.utc)
_A_START_DATE = _NOW - timedelta(days=60)
_ACCOUNT_ID = "account_id"
_CLIENT_SECRET = "client_secret"
_SETUP_INTENT_ID_1 = "setup_intent_id_1"
_SETUP_INTENT_ID_2 = "setup_intent_id_2"
_NO_STATE = StateBuilder().build()
_AVOIDING_INCLUSIVE_BOUNDARIES = timedelta(seconds=1)


def _setup_attempts_request(setup_intent: str) -> StripeRequestBuilder:
    return StripeRequestBuilder.setup_attempts_endpoint(_ACCOUNT_ID, _CLIENT_SECRET).with_setup_intent(setup_intent)


def _setup_intents_request() -> StripeRequestBuilder:
    return StripeRequestBuilder.setup_intents_endpoint(_ACCOUNT_ID, _CLIENT_SECRET)


def _events_request() -> StripeRequestBuilder:
    return StripeRequestBuilder.events_endpoint(_ACCOUNT_ID, _CLIENT_SECRET)


def _config() -> ConfigBuilder:
    return ConfigBuilder().with_start_date(_NOW - timedelta(days=75)).with_account_id(_ACCOUNT_ID).with_client_secret(_CLIENT_SECRET)


def _catalog(sync_mode: SyncMode) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(_STREAM_NAME, sync_mode).build()


def _source(catalog: ConfiguredAirbyteCatalog, config: Dict[str, Any], state: Optional[TState]) -> SourceStripe:
    return SourceStripe(catalog, config, state)


def _an_event() -> RecordBuilder:
    return create_record_builder(
        find_template("events", __file__),
        FieldPath("data"),
        record_id_path=FieldPath("id"),
        record_cursor_path=FieldPath("created"),
    )


def _events_response() -> HttpResponseBuilder:
    return create_response_builder(find_template("events", __file__), FieldPath("data"), pagination_strategy=StripePaginationStrategy())


def _a_setup_attempt() -> RecordBuilder:
    return create_record_builder(
        find_template(_STREAM_NAME, __file__),
        FieldPath("data"),
        record_id_path=FieldPath("id"),
        record_cursor_path=FieldPath("created"),
    )


def _setup_attempts_response() -> HttpResponseBuilder:
    return create_response_builder(find_template(_STREAM_NAME, __file__), FieldPath("data"), pagination_strategy=StripePaginationStrategy())


def _a_setup_intent() -> RecordBuilder:
    return create_record_builder(
        find_template("setup_intents", __file__),
        FieldPath("data"),
        record_id_path=FieldPath("id"),
        record_cursor_path=FieldPath("created"),
    )


def _setup_intents_response() -> HttpResponseBuilder:
    return create_response_builder(
        find_template("setup_intents", __file__), FieldPath("data"), pagination_strategy=StripePaginationStrategy()
    )


def _read(
    config_builder: ConfigBuilder, sync_mode: SyncMode, state: Optional[Dict[str, Any]] = None, expecting_exception: bool = False
) -> EntrypointOutput:
    catalog = _catalog(sync_mode)
    config = config_builder.build()
    return read(_source(catalog, config, state), config, catalog, state, expecting_exception)


@freezegun.freeze_time(_NOW.isoformat())
class FullRefreshTest(TestCase):
    @HttpMocker()
    def test_given_one_page_when_read_then_return_records(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _setup_intents_request().with_created_gte(_A_START_DATE).with_created_lte(_NOW).with_limit(100).build(),
            _setup_intents_response()
            .with_record(_a_setup_intent().with_id(_SETUP_INTENT_ID_1))
            .with_record(_a_setup_intent().with_id(_SETUP_INTENT_ID_2))
            .build(),
        )
        http_mocker.get(
            _setup_attempts_request(_SETUP_INTENT_ID_1).with_created_gte(_A_START_DATE).with_created_lte(_NOW).with_limit(100).build(),
            _setup_attempts_response().with_record(_a_setup_attempt()).build(),
        )
        http_mocker.get(
            _setup_attempts_request(_SETUP_INTENT_ID_2).with_created_gte(_A_START_DATE).with_created_lte(_NOW).with_limit(100).build(),
            _setup_attempts_response().with_record(_a_setup_attempt()).with_record(_a_setup_attempt()).build(),
        )

        output = self._read(_config().with_start_date(_A_START_DATE))

        assert len(output.records) == 3

    def _read(self, config: ConfigBuilder, expecting_exception: bool = False) -> EntrypointOutput:
        return _read(config, SyncMode.full_refresh, expecting_exception=expecting_exception)


@freezegun.freeze_time(_NOW.isoformat())
class IncrementalTest(TestCase):
    @HttpMocker()
    def test_given_no_state_when_read_then_use_cards_endpoint(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _setup_intents_request().with_created_gte(_A_START_DATE).with_created_lte(_NOW).with_limit(100).build(),
            _setup_intents_response()
            .with_record(_a_setup_intent().with_id(_SETUP_INTENT_ID_1))
            .with_record(_a_setup_intent().with_id(_SETUP_INTENT_ID_2))
            .build(),
        )
        http_mocker.get(
            _setup_attempts_request(_SETUP_INTENT_ID_1).with_created_gte(_A_START_DATE).with_created_lte(_NOW).with_limit(100).build(),
            _setup_attempts_response().with_record(_a_setup_attempt()).build(),
        )
        http_mocker.get(
            _setup_attempts_request(_SETUP_INTENT_ID_2).with_created_gte(_A_START_DATE).with_created_lte(_NOW).with_limit(100).build(),
            _setup_attempts_response().with_record(_a_setup_attempt()).with_record(_a_setup_attempt()).build(),
        )

        output = self._read(_config().with_start_date(_A_START_DATE), _NO_STATE)

        assert len(output.records) == 3

    @HttpMocker()
    def test_given_state_when_read_then_query_events_using_types_and_state_value_plus_1(self, http_mocker: HttpMocker) -> None:
        start_date = _NOW - timedelta(days=40)
        state_datetime = _NOW - timedelta(days=5)
        cursor_value = int(state_datetime.timestamp()) + 10
        creation_datetime_of_setup_attempt = int(state_datetime.timestamp()) + 5

        http_mocker.get(
            _events_request()
            .with_created_gte(state_datetime + _AVOIDING_INCLUSIVE_BOUNDARIES)
            .with_created_lte(_NOW)
            .with_limit(100)
            .with_types(_EVENT_TYPES)
            .build(),
            _events_response().with_record(self._a_setup_intent_event(cursor_value, _SETUP_INTENT_ID_1)).build(),
        )
        http_mocker.get(
            _setup_attempts_request(_SETUP_INTENT_ID_1)
            .with_created_gte(state_datetime + _AVOIDING_INCLUSIVE_BOUNDARIES)
            .with_created_lte(_NOW)
            .with_limit(100)
            .build(),
            _setup_attempts_response().with_record(_a_setup_attempt().with_cursor(creation_datetime_of_setup_attempt)).build(),
        )

        output = self._read(
            _config().with_start_date(start_date),
            StateBuilder().with_stream_state(_STREAM_NAME, {"created": int(state_datetime.timestamp())}).build(),
        )

        assert len(output.records) == 1
        most_recent_state = output.most_recent_state
        assert most_recent_state.stream_descriptor == StreamDescriptor(name=_STREAM_NAME)
        assert most_recent_state.stream_state == AirbyteStateBlob(created=creation_datetime_of_setup_attempt)

    def _a_setup_intent_event(self, cursor_value: int, setup_intent_id: str) -> RecordBuilder:
        return _an_event().with_cursor(cursor_value).with_field(_DATA_FIELD, _a_setup_intent().with_id(setup_intent_id).build())

    def _read(self, config: ConfigBuilder, state: Optional[Dict[str, Any]], expecting_exception: bool = False) -> EntrypointOutput:
        return _read(config, SyncMode.incremental, state, expecting_exception)
