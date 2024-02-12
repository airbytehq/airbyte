# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from unittest import TestCase

import freezegun
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import (
    FieldPath,
    NestedPath,
    HttpResponseBuilder,
    RecordBuilder,
    create_record_builder,
    create_response_builder,
    find_template,
)
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_protocol.models import ConfiguredAirbyteCatalog, FailureType, SyncMode
from integration.config import ConfigBuilder
from integration.pagination import ChargebeePaginationStrategy
from integration.request_builder import ChargebeeRequestBuilder
from integration.response_builder import a_response_with_status
from source_chargebee import SourceChargebee

_STREAM_NAME = "event"
_NOW = datetime.now(timezone.utc)
_A_START_DATE = _NOW - timedelta(days=60)
_SITE = "test-site"
_SITE_API_KEY = "test-api-key"
_PRODUCT_CATALOG = "2.0"
_NO_STATE = {}
_AVOIDING_INCLUSIVE_BOUNDARIES = timedelta(seconds=1)
_SECOND_REQUEST = timedelta(seconds=1)
_THIRD_REQUEST = timedelta(seconds=2)

'''
  Add tests for the following:
    - Ensure HTTP integration and record extraction
        * Mock a response with one record for the HTTP request and ensure that there is a record returned
        * There can be multiple requests to mock depending on the authentication method or the presence of a parent stream for example
    - Ensure error handling
        * Mock a response causing an issue and check if there is a trace message
        * I`m not sure if we should test backoff as it will make tests slow. Maybe we can configure a very low backoff and just check for the log message?
    - Ensure pagination
        * Create a mocked response that triggers pagination and ensure the right number of records is returned
    - Ensure transformation
        * Given transformation adds a field, check if this field is available in the record
        * Given the transformation removes a field, check if this field is not in the record
        * Given the transformation modifies a field, check that the original value is different than the new one
    - Ensure incremental sync
        * At least ensure that the cursor value match the one from the most recent record
    - Ensure list partition routing
        * Check if multiple requests are performed
    - Ensure record filtering
        * Set up a response with a record that should be filtered and assert the records count
'''

def _a_request() -> ChargebeeRequestBuilder:
    return ChargebeeRequestBuilder.event_endpoint(_SITE, _SITE_API_KEY)

def _config() -> ConfigBuilder:
    return ConfigBuilder().with_site(_SITE).with_site_api_key(_SITE_API_KEY).with_start_date(_A_START_DATE).with_product_catalog(_PRODUCT_CATALOG)

def _catalog(sync_mode: SyncMode) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(_STREAM_NAME, sync_mode).build()

def _source() -> SourceChargebee:
    return SourceChargebee()

def _a_record() -> RecordBuilder:
    return create_record_builder(
        find_template(_STREAM_NAME, __file__),
        FieldPath("list"),
        record_id_path=NestedPath(["event", "id"]),
        record_cursor_path=NestedPath(["event", "occurred_at"])
    )

def _a_response() -> HttpResponseBuilder:
    return create_response_builder(find_template(_STREAM_NAME, __file__), FieldPath("list"), pagination_strategy=ChargebeePaginationStrategy())

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

    @HttpMocker()
    def test_given_one_page_when_read_then_return_records(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _a_request().with_occurred_at_btw([{int(_A_START_DATE.timestamp())},{int(_NOW.timestamp())}]).with_sort_by_asc('occurred_at').with_limit(100).build(),
            _a_response().with_record(_a_record()).with_record(_a_record()).build(),
        )
        config = _config().with_start_date(_A_START_DATE).with_site('test-site').with_site_api_key('test-site-api-key')
        output = self._read(config)
        assert len(output.records) == 2


    @HttpMocker()
    def test_given_many_pages_when_read_then_return_records(self, http_mocker: HttpMocker) -> None:
        print("todo")

    @HttpMocker()
    def test_given_http_status_401_when_the_stream_is_incomplete(self, http_mocker: HttpMocker) -> None:
        print("todo")

    @HttpMocker()
    def test_given_rate_limited_when_read_then_retry_and_return_records(self, http_mocker: HttpMocker) -> None:
        print("todo")

    @HttpMocker()
    def test_given_http_status_500_once_before_200_when_read_then_retry_and_return_records(self, http_mocker: HttpMocker) -> None:
        print("todo")

    @HttpMocker()
    def test_given_http_status_500_once_before_200_when_read_then_retry_and_fail(self, http_mocker: HttpMocker) -> None:
        print("todo")

    @HttpMocker()
    def test_given_http_status_500_on_availability_when_read_then_raise_system_error(self, http_mocker: HttpMocker) -> None:
        print("todo")

    @HttpMocker()
    def test_given_pagination_when_read_then_return_records(self, http_mocker: HttpMocker) -> None:
        print("todo")

    @HttpMocker()
    def test_given_transformation_when_read_then_return_transformed_records(self, http_mocker: HttpMocker) -> None:
        print("todo")

    @HttpMocker()
    def test_when_read_then_validate_availability_for_full_refresh_and_incremental(self, http_mocker: HttpMocker) -> None:
        print("todo")

    def _read(self, config: ConfigBuilder, expecting_exception: bool = False) -> EntrypointOutput:
        return _read(config, SyncMode.full_refresh, expecting_exception=expecting_exception)


@freezegun.freeze_time(_NOW.isoformat())
class IncrementalTest(TestCase):

    @HttpMocker()
    def test_given_no_state_when_read_then_return_state_based_on_cursor_field(self, http_mocker: HttpMocker) -> None:
        print("todo")

    @HttpMocker()
    def test_given_state_when_read_then_use_state_for_query_params(self, http_mocker: HttpMocker) -> None:
        assert True

    @HttpMocker()
    def test_given_state_more_recent_than_cursor_when_read_then_return_state_based_on_cursor_field(self, http_mocker: HttpMocker) -> None:
        print("todo")
        assert True

    def _read(self, config: ConfigBuilder, state: Dict[str, Any], expecting_exception: bool = False) -> EntrypointOutput:
        return _read(config, SyncMode.incremental, state, expecting_exception)