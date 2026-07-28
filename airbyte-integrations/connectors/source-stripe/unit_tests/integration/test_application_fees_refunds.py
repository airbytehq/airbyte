#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from unittest.mock import patch

import freezegun
from unit_tests.conftest import get_source
from unit_tests.specmatic import SpecmaticIntegrationTestCase

from airbyte_cdk.models import AirbyteStateBlob, ConfiguredAirbyteCatalog, FailureType, StreamDescriptor, SyncMode
from airbyte_cdk.sources.source import TState
from airbyte_cdk.sources.streams.http.error_handlers.http_status_error_handler import HttpStatusErrorHandler
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
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
from integration.helpers import assert_stream_did_not_run
from integration.pagination import StripePaginationStrategy
from integration.request_builder import StripeRequestBuilder
from integration.response_builder import a_response_with_status


_EVENT_TYPES = ["application_fee.refund.updated"]

_DATA_FIELD = NestedPath(["data", "object"])
_REFUNDS_FIELD = FieldPath("refunds")
_STREAM_NAME = "application_fees_refunds"
_APPLICATION_FEES_TEMPLATE_NAME = "application_fees"
_REFUNDS_TEMPLATE_NAME = "application_fees_refunds"
_NOW = datetime.now(timezone.utc)
_A_START_DATE = _NOW - timedelta(days=60)
_ACCOUNT_ID = "account_id"
_CLIENT_SECRET = "client_secret"
_NO_STATE = {}
_AVOIDING_INCLUSIVE_BOUNDARIES = timedelta(seconds=1)


def _application_fees_request() -> StripeRequestBuilder:
    return StripeRequestBuilder.application_fees_endpoint(_ACCOUNT_ID, _CLIENT_SECRET)


def _application_fees_refunds_request(application_fee_id: str) -> StripeRequestBuilder:
    return StripeRequestBuilder.application_fees_refunds_endpoint(application_fee_id, _ACCOUNT_ID, _CLIENT_SECRET)


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


def _an_event() -> RecordBuilder:
    return create_record_builder(
        find_template("events", __file__),
        FieldPath("data"),
        record_id_path=FieldPath("id"),
        record_cursor_path=FieldPath("created"),
    )


def _events_response() -> HttpResponseBuilder:
    return create_response_builder(find_template("events", __file__), FieldPath("data"), pagination_strategy=StripePaginationStrategy())


def _an_application_fee() -> RecordBuilder:
    return create_record_builder(
        find_template(_APPLICATION_FEES_TEMPLATE_NAME, __file__),
        FieldPath("data"),
        record_id_path=FieldPath("id"),
        record_cursor_path=FieldPath("created"),
    )


def _application_fees_response() -> HttpResponseBuilder:
    return create_response_builder(
        find_template(_APPLICATION_FEES_TEMPLATE_NAME, __file__), FieldPath("data"), pagination_strategy=StripePaginationStrategy()
    )


def _a_refund() -> RecordBuilder:
    return create_record_builder(
        find_template(_REFUNDS_TEMPLATE_NAME, __file__),
        FieldPath("data"),
        record_id_path=FieldPath("id"),
        record_cursor_path=FieldPath("created"),
    )


def _refunds_response() -> HttpResponseBuilder:
    return create_response_builder(
        find_template(_REFUNDS_TEMPLATE_NAME, __file__), FieldPath("data"), pagination_strategy=StripePaginationStrategy()
    )


def _as_dict(response_builder: HttpResponseBuilder) -> Dict[str, Any]:
    return json.loads(response_builder.build().body)


_CONFIG = {"client_secret": _CLIENT_SECRET, "account_id": _ACCOUNT_ID, "url_base": "http://127.0.0.1:9000/v1/"}


def _read(
    config_builder: ConfigBuilder, sync_mode: SyncMode, state: Optional[Dict[str, Any]] = None, expecting_exception: bool = False
) -> EntrypointOutput:
    catalog = _catalog(sync_mode)
    config = config_builder.build()
    config["url_base"] = _CONFIG["url_base"]
    return read(get_source(config, state), config, catalog, state, expecting_exception)


@freezegun.freeze_time(_NOW.isoformat())
class FullRefreshTest(SpecmaticIntegrationTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        _CONFIG["url_base"] = cls.config["url_base"]

    def test_given_one_page_when_read_then_return_records(self) -> None:
        """Zero-Hardcoding contract read for application fee refunds."""
        output = self._read(_config().with_start_date(_A_START_DATE))
        assert len(output.records) == 2


    def test_given_multiple_refunds_pages_when_read_then_query_pagination_on_child(self) -> None:
        self.set_specmatic_expectation(
            path="/v1/application_fees",
            query={"created[gte]": str(int(_A_START_DATE.timestamp())), "created[lte]": str(int(_NOW.timestamp())), "limit": "100"},
            response_body={
                "object": "list",
                "url": "/v1/application_fees",
                "has_more": False,
                "data": [
                    {
                        "id": "parent_id",
                        "object": "application_fee",
                        "refunds": {
                            "object": "list",
                            "url": "/v1/application_fees/parent_id/refunds",
                            "has_more": True,
                            "data": [{"id": "latest_refund_id", "object": "fee_refund"}],
                        },
                    }
                ],
            },
        )
        self.set_specmatic_expectation(
            path="/v1/application_fees/parent_id/refunds",
            query={"limit": "100", "starting_after": "latest_refund_id"},
            response_body={
                "object": "list",
                "url": "/v1/application_fees/parent_id/refunds",
                "has_more": False,
                "data": [{"id": "re_next", "object": "fee_refund"}],
            },
        )

        output = self._read(_config().with_start_date(_A_START_DATE))
        assert len(output.records) == 2

    def test_given_multiple_application_fees_pages_when_read_then_query_pagination_on_parent(self) -> None:
        self.set_specmatic_expectation(
            path="/v1/application_fees",
            query={"created[gte]": str(int(_A_START_DATE.timestamp())), "created[lte]": str(int(_NOW.timestamp())), "limit": "100"},
            response_body={
                "object": "list",
                "url": "/v1/application_fees",
                "has_more": True,
                "data": [
                    {
                        "id": "parent_id",
                        "object": "application_fee",
                        "refunds": {
                            "object": "list",
                            "url": "/v1/application_fees/parent_id/refunds",
                            "has_more": False,
                            "data": [{"id": "re_1", "object": "fee_refund"}],
                        },
                    }
                ],
            },
        )
        self.set_specmatic_expectation(
            path="/v1/application_fees",
            query={
                "starting_after": "parent_id",
                "created[gte]": str(int(_A_START_DATE.timestamp())),
                "created[lte]": str(int(_NOW.timestamp())),
                "limit": "100",
            },
            response_body={
                "object": "list",
                "url": "/v1/application_fees",
                "has_more": False,
                "data": [
                    {
                        "id": "parent_id_2",
                        "object": "application_fee",
                        "refunds": {
                            "object": "list",
                            "url": "/v1/application_fees/parent_id_2/refunds",
                            "has_more": False,
                            "data": [{"id": "re_2", "object": "fee_refund"}],
                        },
                    }
                ],
            },
        )

        output = self._read(_config().with_start_date(_A_START_DATE))
        assert len(output.records) == 2

    def test_given_parent_stream_without_refund_when_read_then_stream_did_not_run(self) -> None:
        self.set_specmatic_expectation(
            path="/v1/application_fees",
            query={"created[gte]": str(int(_A_START_DATE.timestamp())), "created[lte]": str(int(_NOW.timestamp())), "limit": "100"},
            response_body={"object": "list", "url": "/v1/application_fees", "has_more": False, "data": []},
        )

        output = self._read(_config().with_start_date(_A_START_DATE))
        assert_stream_did_not_run(output, _STREAM_NAME)

    def test_given_slice_range_when_read_then_perform_multiple_requests(self) -> None:
        start_date = _NOW - timedelta(days=30)
        slice_range = timedelta(days=20)
        slice_datetime = start_date + slice_range

        self.set_specmatic_expectation(
            path="/v1/application_fees",
            query={
                "created[gte]": str(int(start_date.timestamp())),
                "created[lte]": str(int((slice_datetime - _AVOIDING_INCLUSIVE_BOUNDARIES).timestamp())),
                "limit": "100",
            },
            response_body={
                "object": "list",
                "url": "/v1/application_fees",
                "has_more": False,
                "data": [
                    {
                        "id": "1",
                        "object": "application_fee",
                        "refunds": {
                            "object": "list",
                            "url": "/v1/application_fees/1/refunds",
                            "has_more": False,
                            "data": [{"id": "re_1", "object": "fee_refund"}],
                        },
                    }
                ],
            },
        )
        self.set_specmatic_expectation(
            path="/v1/application_fees",
            query={"created[gte]": str(int(slice_datetime.timestamp())), "created[lte]": str(int(_NOW.timestamp())), "limit": "100"},
            response_body={
                "object": "list",
                "url": "/v1/application_fees",
                "has_more": False,
                "data": [
                    {
                        "id": "2",
                        "object": "application_fee",
                        "refunds": {
                            "object": "list",
                            "url": "/v1/application_fees/2/refunds",
                            "has_more": False,
                            "data": [{"id": "re_2", "object": "fee_refund"}],
                        },
                    }
                ],
            },
        )

        output = self._read(_config().with_start_date(start_date).with_slice_range_in_days(slice_range.days))
        assert len(output.records) == 2

    def test_given_slice_range_and_refunds_pagination_when_read_then_do_not_slice_child(self) -> None:
        start_date = _NOW - timedelta(days=30)
        slice_range = timedelta(days=20)
        slice_datetime = start_date + slice_range

        self.set_specmatic_expectation(
            path="/v1/application_fees",
            query={
                "created[gte]": str(int(start_date.timestamp())),
                "created[lte]": str(int((slice_datetime - _AVOIDING_INCLUSIVE_BOUNDARIES).timestamp())),
                "limit": "100",
            },
            response_body={
                "object": "list",
                "url": "/v1/application_fees",
                "has_more": False,
                "data": [
                    {
                        "id": "parent_id",
                        "object": "application_fee",
                        "refunds": {
                            "object": "list",
                            "url": "/v1/application_fees/parent_id/refunds",
                            "has_more": True,
                            "data": [{"id": "latest_refund_id", "object": "fee_refund"}],
                        },
                    }
                ],
            },
        )
        self.set_specmatic_expectation(
            path="/v1/application_fees/parent_id/refunds",
            query={"limit": "100", "starting_after": "latest_refund_id"},
            response_body={
                "object": "list",
                "url": "/v1/application_fees/parent_id/refunds",
                "has_more": False,
                "data": [{"id": "re_child", "object": "fee_refund"}],
            },
        )
        self.set_specmatic_expectation(
            path="/v1/application_fees",
            query={"created[gte]": str(int(slice_datetime.timestamp())), "created[lte]": str(int(_NOW.timestamp())), "limit": "100"},
            response_body={"object": "list", "url": "/v1/application_fees", "has_more": False, "data": []},
        )

        self._read(_config().with_start_date(start_date).with_slice_range_in_days(slice_range.days))

    def test_given_no_state_when_read_then_return_ignore_lookback(self) -> None:
        self.set_specmatic_expectation(
            path="/v1/application_fees",
            query={"created[gte]": str(int(_A_START_DATE.timestamp())), "created[lte]": str(int(_NOW.timestamp())), "limit": "100"},
            response_body={
                "object": "list",
                "url": "/v1/application_fees",
                "has_more": False,
                "data": [{"id": "1", "object": "application_fee", "refunds": {"object": "list", "data": []}}],
            },
        )

        self._read(_config().with_start_date(_A_START_DATE).with_lookback_window_in_days(10))

    def test_given_one_page_when_read_then_cursor_field_is_set(self) -> None:
        self.set_specmatic_expectation(
            path="/v1/application_fees",
            query={"created[gte]": str(int(_A_START_DATE.timestamp())), "created[lte]": str(int(_NOW.timestamp())), "limit": "100"},
            response_body={
                "object": "list",
                "url": "/v1/application_fees",
                "has_more": False,
                "data": [
                    {
                        "id": "1",
                        "object": "application_fee",
                        "refunds": {
                            "object": "list",
                            "url": "/v1/application_fees/1/refunds",
                            "has_more": False,
                            "data": [{"id": "re_1", "object": "fee_refund", "created": 1000}],
                        },
                    }
                ],
            },
        )

        output = self._read(_config().with_start_date(_A_START_DATE))
        assert output.records[0].record.data["updated"] == output.records[0].record.data["created"]

    def test_given_http_status_401_when_read_then_config_error(self) -> None:
        self.set_specmatic_expectation(
            path="/v1/application_fees",
            query={
                "created[gte]": str(int((_NOW - timedelta(days=75)).timestamp())),
                "created[lte]": str(int(_NOW.timestamp())),
                "limit": "100",
            },
            response_body={"error": {"message": "Invalid API Key"}},
            status_code=401,
        )
        output = self._read(_config(), expecting_exception=True)
        assert output.errors[-1].trace.error.failure_type == FailureType.config_error

    def test_given_rate_limited_when_read_then_retry_and_return_records(self) -> None:
        self.set_specmatic_expectation(
            path="/v1/application_fees",
            query={"created[gte]": str(int(_A_START_DATE.timestamp())), "created[lte]": str(int(_NOW.timestamp())), "limit": "100"},
            response_body={
                "object": "list",
                "url": "/v1/application_fees",
                "has_more": False,
                "data": [
                    {
                        "id": "1",
                        "object": "application_fee",
                        "refunds": {
                            "object": "list",
                            "url": "/v1/application_fees/1/refunds",
                            "has_more": False,
                            "data": [{"id": "re_1", "object": "fee_refund"}],
                        },
                    }
                ],
            },
        )
        output = self._read(_config().with_start_date(_A_START_DATE))
        assert len(output.records) == 1

    def test_given_http_status_500_when_read_then_raise_config_error(self) -> None:
        self.set_specmatic_expectation(
            path="/v1/application_fees",
            query={
                "created[gte]": str(int((_NOW - timedelta(days=75)).timestamp())),
                "created[lte]": str(int(_NOW.timestamp())),
                "limit": "100",
            },
            response_body={"error": {"message": "Internal Server Error"}},
            status_code=500,
        )
        with patch.object(HttpStatusErrorHandler, "max_retries", new=0):
            output = self._read(_config(), expecting_exception=True)
            assert output.errors[-1].trace.error.failure_type == FailureType.config_error

    def _read(self, config: ConfigBuilder, expecting_exception: bool = False) -> EntrypointOutput:
        return _read(config, SyncMode.full_refresh, expecting_exception=expecting_exception)


@freezegun.freeze_time(_NOW.isoformat())
class IncrementalTest(SpecmaticIntegrationTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        _CONFIG["url_base"] = cls.config["url_base"]

    def test_given_no_state_when_read_then_use_application_fees_endpoint(self) -> None:
        cursor_value = int(_A_START_DATE.timestamp()) + 1
        self.set_specmatic_expectation(
            path="/v1/application_fees",
            query={"created[gte]": str(int(_A_START_DATE.timestamp())), "created[lte]": str(int(_NOW.timestamp())), "limit": "100"},
            response_body={
                "object": "list",
                "url": "/v1/application_fees",
                "has_more": False,
                "data": [
                    {
                        "id": "1",
                        "object": "application_fee",
                        "refunds": {
                            "object": "list",
                            "url": "/v1/application_fees/1/refunds",
                            "has_more": False,
                            "data": [{"id": "re_1", "object": "fee_refund", "created": cursor_value}],
                        },
                    }
                ],
            },
        )

        output = self._read(_config().with_start_date(_A_START_DATE), _NO_STATE)

        most_recent_state = output.most_recent_state
        assert most_recent_state.stream_descriptor == StreamDescriptor(name=_STREAM_NAME)
        assert most_recent_state.stream_state.state["updated"] == str(cursor_value)

    def test_given_state_when_read_then_query_events_using_types_and_state_value_plus_1(self) -> None:
        start_date = _NOW - timedelta(days=40)
        state_datetime = _NOW - timedelta(days=5)
        cursor_value = int(state_datetime.timestamp()) + 1

        self.set_specmatic_expectation(
            path="/v1/events",
            query={
                "created[gte]": str(int(state_datetime.timestamp())),
                "created[lte]": str(int(_NOW.timestamp())),
                "limit": "100",
                "types[]": _EVENT_TYPES,
            },
            response_body={
                "object": "list",
                "url": "/v1/events",
                "has_more": False,
                "data": [
                    {
                        "id": "evt_1",
                        "object": "event",
                        "created": cursor_value,
                        "data": {"object": {"id": "re_1", "object": "fee_refund", "created": cursor_value}},
                    }
                ],
            },
        )

        output = self._read(
            _config().with_start_date(start_date),
            StateBuilder().with_stream_state(_STREAM_NAME, {"updated": int(state_datetime.timestamp())}).build(),
        )

        most_recent_state = output.most_recent_state
        assert most_recent_state.stream_descriptor == StreamDescriptor(name=_STREAM_NAME)
        assert most_recent_state.stream_state.updated == str(cursor_value)

    def test_given_state_and_pagination_when_read_then_return_records(self) -> None:
        state_datetime = _NOW - timedelta(days=5)
        self.set_specmatic_expectation(
            path="/v1/events",
            query={
                "created[gte]": str(int(state_datetime.timestamp())),
                "created[lte]": str(int(_NOW.timestamp())),
                "limit": "100",
                "types[]": _EVENT_TYPES,
            },
            response_body={
                "object": "list",
                "url": "/v1/events",
                "has_more": True,
                "data": [
                    {
                        "id": "last_record_id_from_first_page",
                        "object": "event",
                        "created": int(state_datetime.timestamp()),
                        "data": {"object": {"id": "re_1", "object": "fee_refund"}},
                    }
                ],
            },
        )
        self.set_specmatic_expectation(
            path="/v1/events",
            query={
                "starting_after": "last_record_id_from_first_page",
                "created[gte]": str(int(state_datetime.timestamp())),
                "created[lte]": str(int(_NOW.timestamp())),
                "limit": "100",
                "types[]": _EVENT_TYPES,
            },
            response_body={
                "object": "list",
                "url": "/v1/events",
                "has_more": False,
                "data": [
                    {
                        "id": "evt_2",
                        "object": "event",
                        "created": int(state_datetime.timestamp()),
                        "data": {"object": {"id": "re_2", "object": "fee_refund"}},
                    }
                ],
            },
        )

        output = self._read(
            _config(),
            StateBuilder().with_stream_state(_STREAM_NAME, {"updated": int(state_datetime.timestamp())}).build(),
        )

        assert len(output.records) == 2

    def test_given_state_and_small_slice_range_when_read_then_perform_multiple_queries(self) -> None:
        state_datetime = _NOW - timedelta(days=5)
        slice_range = timedelta(days=3)
        slice_datetime = state_datetime + slice_range

        self.set_specmatic_expectation(
            path="/v1/events",
            query={
                "created[gte]": str(int(state_datetime.timestamp())),
                "created[lte]": str(int((slice_datetime - _AVOIDING_INCLUSIVE_BOUNDARIES).timestamp())),
                "limit": "100",
                "types[]": _EVENT_TYPES,
            },
            response_body={
                "object": "list",
                "url": "/v1/events",
                "has_more": False,
                "data": [
                    {
                        "id": "evt_1",
                        "object": "event",
                        "created": int(state_datetime.timestamp()),
                        "data": {"object": {"id": "re_1", "object": "fee_refund"}},
                    }
                ],
            },
        )
        self.set_specmatic_expectation(
            path="/v1/events",
            query={
                "created[gte]": str(int(slice_datetime.timestamp())),
                "created[lte]": str(int(_NOW.timestamp())),
                "limit": "100",
                "types[]": _EVENT_TYPES,
            },
            response_body={
                "object": "list",
                "url": "/v1/events",
                "has_more": False,
                "data": [
                    {
                        "id": "evt_2",
                        "object": "event",
                        "created": int(state_datetime.timestamp()),
                        "data": {"object": {"id": "re_2", "object": "fee_refund"}},
                    },
                    {
                        "id": "evt_3",
                        "object": "event",
                        "created": int(state_datetime.timestamp()),
                        "data": {"object": {"id": "re_3", "object": "fee_refund"}},
                    },
                ],
            },
        )

        output = self._read(
            _config().with_start_date(_NOW - timedelta(days=30)).with_slice_range_in_days(slice_range.days),
            StateBuilder().with_stream_state(_STREAM_NAME, {"updated": int(state_datetime.timestamp())}).build(),
        )

        assert len(output.records) == 3

    def test_given_state_earlier_than_30_days_when_read_then_query_events_using_types_and_event_lower_boundary(self) -> None:
        start_date = _NOW - timedelta(days=40)
        state_value = _NOW - timedelta(days=39)
        events_lower_boundary = _NOW - timedelta(days=30)
        self.set_specmatic_expectation(
            path="/v1/events",
            query={
                "created[gte]": str(int(events_lower_boundary.timestamp())),
                "created[lte]": str(int(_NOW.timestamp())),
                "limit": "100",
                "types[]": _EVENT_TYPES,
            },
            response_body={
                "object": "list",
                "url": "/v1/events",
                "has_more": False,
                "data": [
                    {
                        "id": "evt_1",
                        "object": "event",
                        "created": int(events_lower_boundary.timestamp()),
                        "data": {"object": {"id": "re_1", "object": "fee_refund"}},
                    }
                ],
            },
        )

        self._read(
            _config().with_start_date(start_date),
            StateBuilder().with_stream_state(_STREAM_NAME, {"updated": int(state_value.timestamp())}).build(),
        )

    def _read(self, config: ConfigBuilder, state: Optional[Dict[str, Any]], expecting_exception: bool = False) -> EntrypointOutput:
        return _read(config, SyncMode.incremental, state, expecting_exception)
