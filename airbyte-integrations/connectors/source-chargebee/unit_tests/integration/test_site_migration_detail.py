# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from unittest import TestCase

import freezegun
from airbyte_cdk.models import AirbyteStateBlob, ConfiguredAirbyteCatalog, FailureType, StreamDescriptor, SyncMode
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
from source_chargebee import SourceChargebee

from .config import ConfigBuilder
from .pagination import ChargebeePaginationStrategy
from .request_builder import ChargebeeRequestBuilder
from .response_builder import a_response_with_status, a_response_with_status_and_header

_STREAM_NAME = "site_migration_detail"
_SITE = "test-site"
_SITE_API_KEY = "test-api-key"
_PRODUCT_CATALOG = "2.0"
_PRIMARY_KEY = "entity_id"
_CURSOR_FIELD = "migrated_at"
_NO_STATE = {}
_NOW = datetime.now(timezone.utc)

'''
Note that this is a semi-incremental stream and tests will need to be adapated accordingly
'''


def _a_request() -> ChargebeeRequestBuilder:
    return ChargebeeRequestBuilder.site_migration_detail_endpoint(_SITE, _SITE_API_KEY)

def _config() -> ConfigBuilder:
    return ConfigBuilder().with_site(_SITE).with_site_api_key(_SITE_API_KEY).with_product_catalog(_PRODUCT_CATALOG)

def _catalog(sync_mode: SyncMode) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(_STREAM_NAME, sync_mode).build()

def _source() -> SourceChargebee:
    return SourceChargebee()

def _a_record() -> RecordBuilder:
    return create_record_builder(
        find_template(_STREAM_NAME, __file__),
        FieldPath("list"),
        record_id_path=NestedPath([_STREAM_NAME, _PRIMARY_KEY]),
        record_cursor_path=NestedPath([_STREAM_NAME, _CURSOR_FIELD])
    )

def _a_response() -> HttpResponseBuilder:
    return create_response_builder(
        find_template(_STREAM_NAME, __file__),
        FieldPath("list"),
        pagination_strategy=ChargebeePaginationStrategy()
    )

def _read(
    config_builder: ConfigBuilder,
    sync_mode: SyncMode,
    state: Optional[Dict[str, Any]] = None,
    expecting_exception: bool = False
) -> EntrypointOutput:
    catalog = _catalog(sync_mode)
    config = config_builder.build()
    return read(_source(), config, catalog, state, expecting_exception)

@freezegun.freeze_time(_NOW.isoformat())
class FullRefreshTest(TestCase):

    def setUp(self) -> None:
        self._now = _NOW
        self._now_in_seconds = int(self._now.timestamp())
        self._start_date = _NOW - timedelta(days=28)
        self._start_date_in_seconds = int(self._start_date.timestamp())

    @staticmethod
    def _read(config: ConfigBuilder, expecting_exception: bool = False) -> EntrypointOutput:
        return _read(config, SyncMode.full_refresh, expecting_exception=expecting_exception)

    @HttpMocker()
    def test_given_valid_response_records_are_extracted_and_returned(self, http_mocker: HttpMocker) -> None:
        # Tests simple read and record extraction
        http_mocker.get(
            _a_request().with_any_query_params().build(),
            _a_response().with_record(_a_record()).with_record(_a_record()).build()
        )
        output = self._read(_config().with_start_date(self._start_date))
        assert len(output.records) == 2

    @HttpMocker()
    def test_given_multiple_pages_of_records_read_and_returned(self, http_mocker: HttpMocker) -> None:
        # Tests pagination
        http_mocker.get(
            _a_request().build(),
            _a_response().with_record(_a_record()).with_pagination().build()
        )
        http_mocker.get(
            _a_request().with_offset("[1707076198000,57873868]").build(),
            _a_response().with_record(_a_record()).build()
        )

        self._read(_config().with_start_date(self._start_date))
        # HTTPMocker ensures call are performed


    @HttpMocker()
    def test_given_http_status_400_when_read_then_stream_is_ignored(self, http_mocker: HttpMocker) -> None:
        # Tests 400 status error handling
        http_mocker.get(
            _a_request().with_any_query_params().build(),
            a_response_with_status(400)
        )
        output = self._read(_config().with_start_date(self._start_date), expecting_exception=True)
        assert len(output.get_stream_statuses(f"{_STREAM_NAME}s")) == 0

    @HttpMocker()
    def test_given_http_status_401_when_the_stream_is_incomplete(self, http_mocker: HttpMocker) -> None:
        # Test 401 status error handling
        http_mocker.get(
            _a_request().with_any_query_params().build(),
            a_response_with_status(401),
        )
        output = self._read(_config().with_start_date(self._start_date), expecting_exception=True)
        assert output.errors[-1].trace.error.failure_type == FailureType.config_error

    @HttpMocker()
    def test_given_rate_limited_when_read_then_retry_and_return_records(self, http_mocker: HttpMocker) -> None:
        # Tests backoff/retry with rate limiting
        http_mocker.get(
            _a_request().with_any_query_params().build(),
            [
                a_response_with_status_and_header(429, {"Retry-After": "0.01"}),
                _a_response().with_record(_a_record()).build(),
            ],
        )
        output = self._read(_config().with_start_date(self._start_date))
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_http_status_500_then_retry_returns_200_and_extracted_records(self, http_mocker: HttpMocker) -> None:
        # Tests retry with 500 status
        http_mocker.get(
            _a_request().with_any_query_params().build(),
            [a_response_with_status_and_header(500, {"Retry-After": "0.01"}), _a_response().with_record(_a_record()).build()],
        )
        output = self._read(_config().with_start_date(self._start_date))
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_http_status_500_after_max_retries_raises_config_error(self, http_mocker: HttpMocker) -> None:
        # Tests 500 status error handling
        http_mocker.get(
            _a_request().with_any_query_params().build(),
            a_response_with_status_and_header(500, {"Retry-After": "0.01"}),
        )
        output = self._read(_config(), expecting_exception=True)
        assert output.errors[-1].trace.error.failure_type == FailureType.config_error


@freezegun.freeze_time(_NOW.isoformat())
class IncrementalTest(TestCase):

    # Site Migration Detail stream is a semi-incremental stream and therefore state acts differently than typical declarative incremental implementation -- state is updated to most recent cursor value read

    def setUp(self) -> None:
        self._now = _NOW
        self._now_in_seconds = int(self._now.timestamp())
        self._start_date = _NOW - timedelta(days=60)
        self._start_date_in_seconds = int(self._start_date.timestamp())

    @staticmethod
    def _read(config: ConfigBuilder, state: Dict[str, Any], expecting_exception: bool = False) -> EntrypointOutput:
        return _read(config, SyncMode.incremental, state, expecting_exception)

    @HttpMocker()
    def test_given_no_initial_state_when_read_then_return_state_based_on_cursor_field(self, http_mocker: HttpMocker) -> None:
        # Tests setting state when no initial state is provided
        cursor_value = self._start_date_in_seconds + 1
        http_mocker.get(
            _a_request().with_any_query_params().build(),
            _a_response().with_record(_a_record().with_cursor(cursor_value)).build()
        )
        output = self._read(_config().with_start_date(self._start_date), _NO_STATE)
        most_recent_state = output.most_recent_state
        assert most_recent_state.stream_descriptor == StreamDescriptor(name=_STREAM_NAME)
        assert most_recent_state.stream_state == AirbyteStateBlob(migrated_at=cursor_value)

    @HttpMocker()
    def test_given_initial_state_value_when_read_then_state_is_updated_to_most_recent_cursor_value(self, http_mocker: HttpMocker) -> None:
        state_cursor_value = self._start_date_in_seconds + 1
        record_cursor_value = state_cursor_value + 1
        state =  StateBuilder().with_stream_state(_STREAM_NAME, {_CURSOR_FIELD: state_cursor_value}).build()

        http_mocker.get(
            _a_request().with_any_query_params().build(),
            _a_response().with_record(_a_record().with_cursor(record_cursor_value)).build(),
        )

        output = self._read(_config().with_start_date(self._start_date), state)
        most_recent_state = output.most_recent_state
        assert most_recent_state.stream_descriptor == StreamDescriptor(name=_STREAM_NAME)
        assert most_recent_state.stream_state == AirbyteStateBlob(migrated_at=record_cursor_value, prior_state={_CURSOR_FIELD: state_cursor_value})

    @HttpMocker()
    def test_given_record_returned_with_cursor_value_before_state_record_is_not_read_and_state_not_updated(self, http_mocker: HttpMocker) -> None:
        state_cursor_value = self._start_date_in_seconds
        record_cursor_value = self._start_date_in_seconds - 1
        state =  StateBuilder().with_stream_state(_STREAM_NAME, {_CURSOR_FIELD: state_cursor_value}).build()

        http_mocker.get(
            _a_request().with_any_query_params().build(),
            _a_response().with_record(_a_record().with_cursor(record_cursor_value)).build(),
        )

        output = self._read(_config().with_start_date(self._start_date), state)
        most_recent_state = output.most_recent_state
        assert most_recent_state.stream_descriptor == StreamDescriptor(name=_STREAM_NAME)
        assert most_recent_state.stream_state == AirbyteStateBlob(migrated_at=state_cursor_value, prior_state={_CURSOR_FIELD: state_cursor_value})
        assert len(output.records) == 0
