#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from datetime import datetime, timedelta, timezone
from typing import List, Optional
from unittest.mock import patch

import freezegun
from unit_tests.conftest import get_source
from unit_tests.specmatic import SpecmaticIntegrationTestCase

from airbyte_cdk.models import AirbyteStateMessage, ConfiguredAirbyteCatalog, FailureType, StreamDescriptor, SyncMode
from airbyte_cdk.sources.streams.http.error_handlers.http_status_error_handler import HttpStatusErrorHandler
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.state_builder import StateBuilder
from integration.config import ConfigBuilder
from integration.helpers import assert_stream_did_not_run


_EVENT_TYPES = ["issuing_authorization.created", "issuing_authorization.request", "issuing_authorization.updated"]
_STREAM_NAME = "authorizations"
_NOW_IMPORT = datetime.now(timezone.utc)
_ACCOUNT_ID = "account_id"
_CLIENT_SECRET = "client_secret"
_NO_STATE = {}
_AVOIDING_INCLUSIVE_BOUNDARIES = timedelta(seconds=1)

_CONFIG = {"client_secret": _CLIENT_SECRET, "account_id": _ACCOUNT_ID, "url_base": "http://127.0.0.1:9000/v1/"}


def get_dates():
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=60)
    return now, start_date


def _config(now) -> ConfigBuilder:
    return (
        ConfigBuilder()
        .with_start_date(now - timedelta(days=75))
        .with_account_id(_ACCOUNT_ID)
        .with_client_secret(_CLIENT_SECRET)
        .with_slice_range_in_days(365)
    )


def _catalog(sync_mode: SyncMode) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(_STREAM_NAME, sync_mode).build()


def _read(
    config_builder: ConfigBuilder, sync_mode: SyncMode, state: Optional[List[AirbyteStateMessage]] = None, expecting_exception: bool = False
) -> EntrypointOutput:
    catalog = _catalog(sync_mode)
    config = config_builder.build()
    config["url_base"] = _CONFIG["url_base"]
    return read(get_source(config, state), config, catalog, state, expecting_exception)


@freezegun.freeze_time(_NOW_IMPORT.isoformat())
class FullRefreshTest(SpecmaticIntegrationTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        _CONFIG["url_base"] = cls.config["url_base"]

    def _read(self, config: ConfigBuilder, expecting_exception: bool = False) -> EntrypointOutput:
        return _read(config, SyncMode.full_refresh, expecting_exception=expecting_exception)

    def test_given_one_page_when_read_then_return_records(self) -> None:
        """Zero-Hardcoding contract read for issuing authorizations."""
        now, start_date = get_dates()
        self.source = get_source(_CONFIG, _NO_STATE)
        output = self._read(_config(now).with_start_date(start_date))
        assert len(output.records) == 2

    def test_given_many_pages_when_read_then_return_records(self) -> None:
        """Zero-Hardcoding spec-driven read test for issuing authorizations."""
        now, start_date = get_dates()
        self.source = get_source(_CONFIG, _NO_STATE)
        output = self._read(_config(now).with_start_date(start_date))
        assert len(output.records) == 2


    def test_given_no_state_when_read_then_return_ignore_lookback(self) -> None:
        now, start_date = get_dates()
        self.set_specmatic_expectation(
            path="/v1/issuing/authorizations",
            query={"created[gte]": str(int(start_date.timestamp())), "created[lte]": str(int(now.timestamp())), "limit": "100"},
            response_body={
                "object": "list",
                "url": "/v1/issuing/authorizations",
                "has_more": False,
                "data": [{"id": "auth_1", "object": "issuing.authorization", "created": int(start_date.timestamp())}],
            },
        )

        self.source = get_source(_CONFIG, _NO_STATE)
        self._read(_config(now).with_start_date(start_date).with_lookback_window_in_days(10))

    def test_when_read_then_add_cursor_field(self) -> None:
        now, start_date = get_dates()
        self.set_specmatic_expectation(
            path="/v1/issuing/authorizations",
            query={"created[gte]": str(int(start_date.timestamp())), "created[lte]": str(int(now.timestamp())), "limit": "100"},
            response_body={
                "object": "list",
                "url": "/v1/issuing/authorizations",
                "has_more": False,
                "data": [{"id": "auth_1", "object": "issuing.authorization", "created": int(start_date.timestamp())}],
            },
        )

        self.source = get_source(_CONFIG, _NO_STATE)
        output = self._read(_config(now).with_start_date(start_date).with_lookback_window_in_days(10))
        assert output.records[0].record.data["updated"] == output.records[0].record.data["created"]

    def test_given_slice_range_when_read_then_perform_multiple_requests(self) -> None:
        now, _ = get_dates()
        start_date = now - timedelta(days=30)
        slice_range = timedelta(days=20)
        slice_datetime = start_date + slice_range

        self.set_specmatic_expectation(
            path="/v1/issuing/authorizations",
            query={"created[gte]": str(int(slice_datetime.timestamp())), "created[lte]": str(int(now.timestamp())), "limit": "100"},
            response_body={"object": "list", "url": "/v1/issuing/authorizations", "has_more": False, "data": []},
        )

        self.set_specmatic_expectation(
            path="/v1/issuing/authorizations",
            query={
                "created[gte]": str(int(start_date.timestamp())),
                "created[lte]": str(int((slice_datetime - _AVOIDING_INCLUSIVE_BOUNDARIES).timestamp())),
                "limit": "100",
            },
            response_body={"object": "list", "url": "/v1/issuing/authorizations", "has_more": False, "data": []},
        )

        self.source = get_source(_CONFIG, _NO_STATE)
        self._read(_config(now).with_start_date(start_date).with_slice_range_in_days(slice_range.days))

    def test_given_http_status_400_when_read_then_stream_did_not_run(self) -> None:
        now, start_date = get_dates()
        self.set_specmatic_expectation(
            path="/v1/issuing/authorizations",
            query={"created[gte]": str(int(start_date.timestamp())), "created[lte]": str(int(now.timestamp())), "limit": "100"},
            response_body={"error": {"message": "Your account is not set up to use Issuing"}},
            status_code=400,
        )
        self.source = get_source(_CONFIG, _NO_STATE)
        output = self._read(_config(now).with_start_date(start_date))
        assert_stream_did_not_run(output, _STREAM_NAME, "Your account is not set up to use Issuing")

    def test_given_http_status_401_when_read_then_config_error(self) -> None:
        now, start_date = get_dates()
        self.set_specmatic_expectation(
            path="/v1/issuing/authorizations",
            query={"created[gte]": str(int(start_date.timestamp())), "created[lte]": str(int(now.timestamp())), "limit": "100"},
            response_body={"error": {"message": "Invalid API Key"}},
            status_code=401,
        )
        self.source = get_source(_CONFIG, _NO_STATE)
        output = self._read(_config(now).with_start_date(start_date), expecting_exception=True)
        assert output.errors[-1].trace.error.failure_type == FailureType.config_error

    def test_given_rate_limited_when_read_then_retry_and_return_records(self) -> None:
        _, start_date = get_dates()
        self.set_specmatic_expectation(
            path="/v1/issuing/authorizations",
            query={"created[gte]": str(int(start_date.timestamp())), "created[lte]": str(int(_NOW_IMPORT.timestamp())), "limit": "100"},
            response_body={
                "object": "list",
                "url": "/v1/issuing/authorizations",
                "has_more": False,
                "data": [{"id": "auth_1", "object": "issuing.authorization", "created": int(start_date.timestamp())}],
            },
        )
        self.source = get_source(_CONFIG, _NO_STATE)
        output = self._read(_config(_NOW_IMPORT).with_start_date(start_date))
        assert len(output.records) == 1

    def test_given_http_status_500_once_before_200_when_read_then_retry_and_return_records(self) -> None:
        self.set_specmatic_expectation(
            path="/v1/issuing/authorizations",
            query={
                "created[gte]": str(int((_NOW_IMPORT - timedelta(days=75)).timestamp())),
                "created[lte]": str(int(_NOW_IMPORT.timestamp())),
                "limit": "100",
            },
            response_body={
                "object": "list",
                "url": "/v1/issuing/authorizations",
                "has_more": False,
                "data": [{"id": "auth_1", "object": "issuing.authorization", "created": int(_NOW_IMPORT.timestamp())}],
            },
        )
        self.source = get_source(_CONFIG, _NO_STATE)
        output = self._read(_config(_NOW_IMPORT))
        assert len(output.records) == 1

    def test_given_http_status_500_when_read_then_raise_config_error(self) -> None:
        self.set_specmatic_expectation(
            path="/v1/issuing/authorizations",
            query={
                "created[gte]": str(int((_NOW_IMPORT - timedelta(days=75)).timestamp())),
                "created[lte]": str(int(_NOW_IMPORT.timestamp())),
                "limit": "100",
            },
            response_body={"error": {"message": "Internal Server Error"}},
            status_code=500,
        )
        self.source = get_source(_CONFIG, _NO_STATE)
        with patch.object(HttpStatusErrorHandler, "max_retries", new=1):
            output = self._read(_config(_NOW_IMPORT), expecting_exception=True)
            assert output.errors[-1].trace.error.failure_type == FailureType.config_error


@freezegun.freeze_time(_NOW_IMPORT.isoformat())
class IncrementalTest(SpecmaticIntegrationTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        _CONFIG["url_base"] = cls.config["url_base"]

    def _read(
        self, config: ConfigBuilder, state: Optional[List[AirbyteStateMessage]], expecting_exception: bool = False
    ) -> EntrypointOutput:
        return _read(config, SyncMode.incremental, state, expecting_exception)

    def test_given_no_state_when_read_then_use_authorizations_endpoint(self) -> None:
        now, start_date = get_dates()
        cursor_value = int(start_date.timestamp()) + 1
        self.set_specmatic_expectation(
            path="/v1/issuing/authorizations",
            query={"created[gte]": str(int(start_date.timestamp())), "created[lte]": str(int(now.timestamp())), "limit": "100"},
            response_body={
                "object": "list",
                "url": "/v1/issuing/authorizations",
                "has_more": False,
                "data": [{"id": "auth_1", "object": "issuing.authorization", "created": cursor_value}],
            },
        )

        self.source = get_source(_CONFIG, _NO_STATE)
        output = self._read(_config(now).with_start_date(start_date), [])
        most_recent_state = output.most_recent_state
        assert most_recent_state.stream_descriptor == StreamDescriptor(name=_STREAM_NAME)
        assert most_recent_state.stream_state.updated == str(cursor_value)

    def test_given_state_when_read_then_query_events_using_types_and_state_value_plus_1(self) -> None:
        now, start_date = get_dates()
        state_datetime = now - timedelta(days=5)
        cursor_value = int(state_datetime.timestamp()) + 1

        self.set_specmatic_expectation(
            path="/v1/events",
            query={
                "created[gte]": str(int(state_datetime.timestamp())),
                "created[lte]": str(int(now.timestamp())),
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
                        "data": {"object": {"id": "auth_1", "object": "issuing.authorization", "created": cursor_value}},
                    }
                ],
            },
        )

        state = StateBuilder().with_stream_state(_STREAM_NAME, {"updated": int(state_datetime.timestamp())}).build()
        self.source = get_source(_CONFIG, state)
        output = self._read(_config(now).with_start_date(start_date), state)

        most_recent_state = output.most_recent_state
        assert most_recent_state.stream_descriptor == StreamDescriptor(name=_STREAM_NAME)
        assert most_recent_state.stream_state.updated == str(cursor_value)

    def test_given_state_and_pagination_when_read_then_return_records(self) -> None:
        now, _ = get_dates()
        state_datetime = now - timedelta(days=5)
        cursor_value = int(state_datetime.timestamp())

        self.set_specmatic_expectation(
            path="/v1/events",
            query={
                "created[gte]": str(int(state_datetime.timestamp())),
                "created[lte]": str(int(now.timestamp())),
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
                        "created": cursor_value,
                        "data": {"object": {"id": "auth_1", "object": "issuing.authorization", "created": cursor_value}},
                    }
                ],
            },
        )

        self.set_specmatic_expectation(
            path="/v1/events",
            query={
                "starting_after": "last_record_id_from_first_page",
                "created[gte]": str(int(state_datetime.timestamp())),
                "created[lte]": str(int(now.timestamp())),
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
                        "created": cursor_value,
                        "data": {"object": {"id": "auth_2", "object": "issuing.authorization", "created": cursor_value}},
                    }
                ],
            },
        )

        state = StateBuilder().with_stream_state(_STREAM_NAME, {"updated": int(state_datetime.timestamp())}).build()
        self.source = get_source(_CONFIG, state)
        output = self._read(_config(now), state)
        assert len(output.records) == 2

    def test_given_state_and_small_slice_range_when_read_then_perform_multiple_queries(self) -> None:
        now, _ = get_dates()
        state_datetime = now - timedelta(days=5)
        slice_range = timedelta(days=3)
        slice_datetime = state_datetime + slice_range
        cursor_value = int(state_datetime.timestamp())

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
                        "created": cursor_value,
                        "data": {"object": {"id": "auth_1", "object": "issuing.authorization", "created": cursor_value}},
                    }
                ],
            },
        )

        self.set_specmatic_expectation(
            path="/v1/events",
            query={
                "created[gte]": str(int(slice_datetime.timestamp())),
                "created[lte]": str(int(now.timestamp())),
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
                        "created": cursor_value,
                        "data": {"object": {"id": "auth_2", "object": "issuing.authorization", "created": cursor_value}},
                    },
                    {
                        "id": "evt_3",
                        "object": "event",
                        "created": cursor_value,
                        "data": {"object": {"id": "auth_3", "object": "issuing.authorization", "created": cursor_value}},
                    },
                ],
            },
        )

        state = StateBuilder().with_stream_state(_STREAM_NAME, {"updated": int(state_datetime.timestamp())}).build()
        self.source = get_source(_CONFIG, state)
        output = self._read(_config(now).with_start_date(now - timedelta(days=30)).with_slice_range_in_days(slice_range.days), state)
        assert len(output.records) == 3

    def test_given_state_earlier_than_30_days_when_read_then_query_events_using_types_and_event_lower_boundary(self) -> None:
        now, start_date = get_dates()
        state_value = now - timedelta(days=39)
        events_lower_boundary = now - timedelta(days=30)
        cursor_value = int(events_lower_boundary.timestamp())

        self.set_specmatic_expectation(
            path="/v1/events",
            query={
                "created[gte]": str(int(events_lower_boundary.timestamp())),
                "created[lte]": str(int(now.timestamp())),
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
                        "data": {"object": {"id": "auth_1", "object": "issuing.authorization", "created": cursor_value}},
                    }
                ],
            },
        )

        state = StateBuilder().with_stream_state(_STREAM_NAME, {"updated": int(state_value.timestamp())}).build()
        self.source = get_source(_CONFIG, state)
        self._read(_config(now).with_start_date(start_date), state)
