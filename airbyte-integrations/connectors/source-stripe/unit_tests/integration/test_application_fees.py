import json

import freezegun

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple
from unittest import TestCase

from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_cdk.test.entrypoint_wrapper import read, EntrypointOutput
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse

from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS
from airbyte_cdk.test.mock_http.response_builder import create_builders_from_resource, find_template, FieldPath, HttpResponseBuilder, NestedPath, RecordBuilder
from airbyte_protocol.models import SyncMode, ConfiguredAirbyteCatalog, AirbyteStreamStatus
from source_stripe import SourceStripe
from integration.config import ConfigBuilder
from integration.pagination import StripePaginationStrategy


_DATA_FIELD = NestedPath(["data", "object"])
_STREAM_NAME = "application_fees"
_NOW = datetime.now(timezone.utc)
_A_START_DATE = _NOW - timedelta(days=60)
_ACCOUNT_ID = "account_id"
_CLIENT_SECRET = "client_secret"
_AUTHENTICATION_HEADERS = {"Stripe-Account": _ACCOUNT_ID, "Authorization": f"Bearer {_CLIENT_SECRET}"}
_NO_STATE = {}
_HTTP_RESPONSE_STATUS_500 = HttpResponse(
    json.dumps(
        {"unknown": "maxi297: I could not reproduce the issue hence this response will not look like the actual 500 status response"}
    ),
    500
)
_AVOIDING_INCLUSIVE_BOUNDARIES = 1


def _config() -> ConfigBuilder:
    return ConfigBuilder().with_start_date(_NOW - timedelta(days=75)).with_account_id(_ACCOUNT_ID).with_client_secret(_CLIENT_SECRET)


def _catalog(sync_mode: SyncMode) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(_STREAM_NAME, sync_mode).build()


def _source(catalog: ConfiguredAirbyteCatalog) -> SourceStripe:
    return SourceStripe(catalog)


def _create_events_builders() -> Tuple[RecordBuilder, HttpResponseBuilder]:
    return create_builders_from_resource(
        find_template("events", __file__),
        FieldPath("data"),
        record_id_path=FieldPath("id"),
        record_cursor_path=FieldPath("created"),
        pagination_strategy=StripePaginationStrategy(),
    )


def _an_event() -> RecordBuilder:
    return _create_events_builders()[0]


def _events_response() -> HttpResponseBuilder:
    return _create_events_builders()[1]


def _response_with_status(status_code: int) -> HttpResponse:
    return HttpResponse(json.dumps(find_template(str(status_code), __file__)), status_code)


def _create_builders() -> Tuple[RecordBuilder, HttpResponseBuilder]:
    return create_builders_from_resource(
        find_template("application_fees", __file__),
        FieldPath("data"),
        record_id_path=FieldPath("id"),
        record_cursor_path=FieldPath("created"),
        pagination_strategy=StripePaginationStrategy(),
    )


def _an_application_fee() -> RecordBuilder:
    return _create_builders()[0]


def _application_fees_response() -> HttpResponseBuilder:
    return _create_builders()[1]


def _set_up_availability_check(endpoint: str, http_mocker: HttpMocker) -> None:
    http_mocker.get(
        HttpRequest(url=f"https://api.stripe.com/v1/{endpoint}", query_params=ANY_QUERY_PARAMS, headers=_AUTHENTICATION_HEADERS),
        _events_response().build()
    )


def _read(
    config: ConfigBuilder,
    sync_mode: SyncMode,
    state: Optional[Dict[str, Any]] = None,
    expecting_exception: bool = False
) -> EntrypointOutput:
    catalog = _catalog(sync_mode)
    return read(_source(catalog), config.build(), catalog, state, expecting_exception)


@freezegun.freeze_time(_NOW.isoformat())
class FullRefreshTest(TestCase):

    @HttpMocker()
    def test_given_one_page_when_read_then_return_record(self, http_mocker: HttpMocker) -> None:
        _set_up_availability_check("events", http_mocker)
        http_mocker.get(
            HttpRequest(
                url="https://api.stripe.com/v1/application_fees",
                query_params={"created[gte]": str(int(_A_START_DATE.timestamp())), "created[lte]": str(int(_NOW.timestamp())), "limit": 100},
                headers=_AUTHENTICATION_HEADERS
            ),
            _application_fees_response().with_record(_an_application_fee()).with_record(_an_application_fee()).build()
        )

        output = self._read(_config().with_start_date(_A_START_DATE))

        assert len(output.records) == 2

    @HttpMocker()
    def test_given_many_pages_when_read_then_return_records(self, http_mocker: HttpMocker) -> None:
        _set_up_availability_check("events", http_mocker)
        http_mocker.get(
            HttpRequest(
                url="https://api.stripe.com/v1/application_fees",
                query_params={"created[gte]": str(int(_A_START_DATE.timestamp())), "created[lte]": str(int(_NOW.timestamp())), "limit": 100},
                headers=_AUTHENTICATION_HEADERS,
            ),
            _application_fees_response().with_pagination().with_record(_an_application_fee().with_id("last_record_id_from_first_page")).build()
        )
        http_mocker.get(
            HttpRequest(
                url="https://api.stripe.com/v1/application_fees",
                query_params={
                    "starting_after": "last_record_id_from_first_page",
                    "created[gte]": str(int(_A_START_DATE.timestamp())),
                    "created[lte]": str(int(_NOW.timestamp())),
                    "limit": 100,
                },
                headers=_AUTHENTICATION_HEADERS,
            ),
            _application_fees_response().with_record(_an_application_fee()).with_record(_an_application_fee()).build()
        )

        output = self._read(_config().with_start_date(_A_START_DATE))

        assert len(output.records) == 3

    @HttpMocker()
    def test_given_no_state_when_read_then_return_ignore_lookback(self, http_mocker: HttpMocker) -> None:
        _set_up_availability_check("events", http_mocker)
        http_mocker.get(
            HttpRequest(
                url="https://api.stripe.com/v1/application_fees",
                query_params={"created[gte]": str(int(_A_START_DATE.timestamp())), "created[lte]": str(int(_NOW.timestamp())), "limit": 100},
                headers=_AUTHENTICATION_HEADERS
            ),
            _application_fees_response().with_record(_an_application_fee()).build()
        )

        self._read(_config().with_start_date(_A_START_DATE).with_lookback_window_in_days(10))

        # request matched http_mocker

    @HttpMocker()
    def test_when_read_then_add_cursor_field(self, http_mocker: HttpMocker) -> None:
        _set_up_availability_check("events", http_mocker)
        http_mocker.get(
            HttpRequest(
                url="https://api.stripe.com/v1/application_fees",
                query_params={"created[gte]": str(int(_A_START_DATE.timestamp())), "created[lte]": str(int(_NOW.timestamp())), "limit": 100},
                headers=_AUTHENTICATION_HEADERS
            ),
            _application_fees_response().with_record(_an_application_fee()).build()
        )

        output = self._read(_config().with_start_date(_A_START_DATE).with_lookback_window_in_days(10))

        assert output.records[0].record.data["updated"] == output.records[0].record.data["created"]

    @HttpMocker()
    def test_given_http_status_400_when_read_then_stream_is_ignored(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            HttpRequest(
                url="https://api.stripe.com/v1/application_fees",
                query_params=ANY_QUERY_PARAMS,
                headers=_AUTHENTICATION_HEADERS
            ),
            _response_with_status(400),
        )
        output = self._read(_config())
        assert len(output.get_stream_statuses(_STREAM_NAME)) == 0

    @HttpMocker()
    def test_given_http_status_401_when_read_then_stream_is_incomplete(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            HttpRequest(
                url="https://api.stripe.com/v1/application_fees",
                query_params=ANY_QUERY_PARAMS,
                headers=_AUTHENTICATION_HEADERS
            ),
            _response_with_status(401),
        )
        output = self._read(_config(), expecting_exception=True)
        assert output.get_stream_statuses(_STREAM_NAME) == [AirbyteStreamStatus.INCOMPLETE]

    @HttpMocker()
    def test_given_rate_limited_when_read_then_retry_and_return_records(self, http_mocker: HttpMocker) -> None:
        _set_up_availability_check("events", http_mocker)
        http_mocker.get(
            HttpRequest(
                url="https://api.stripe.com/v1/application_fees",
                query_params=ANY_QUERY_PARAMS,
                headers=_AUTHENTICATION_HEADERS
            ),
            [
                _response_with_status(429),
                _application_fees_response().with_record(_an_application_fee()).build(),
            ]
        )
        output = self._read(_config().with_start_date(_A_START_DATE))
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_http_status_500_once_before_200_when_read_then_retry_and_return_records(self, http_mocker: HttpMocker) -> None:
        _set_up_availability_check("events", http_mocker)
        http_mocker.get(
            HttpRequest(
                url="https://api.stripe.com/v1/application_fees",
                query_params=ANY_QUERY_PARAMS,
                headers=_AUTHENTICATION_HEADERS
            ),
            [_response_with_status(500), _application_fees_response().with_record(_an_application_fee()).build()]
        )
        output = self._read(_config())
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_http_status_500_on_availability_when_read_then_stream_is_incomplete(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            HttpRequest(
                url="https://api.stripe.com/v1/application_fees",
                query_params=ANY_QUERY_PARAMS,
                headers=_AUTHENTICATION_HEADERS
            ),
            _response_with_status(500),
        )
        output = self._read(_config(), expecting_exception=True)
        assert output.get_stream_statuses(_STREAM_NAME) == [AirbyteStreamStatus.INCOMPLETE]

    # TODO slice range

    def _set_up_events_availability_check(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            HttpRequest(url="https://api.stripe.com/v1/events", query_params=ANY_QUERY_PARAMS, headers=_AUTHENTICATION_HEADERS),
            _events_response().build()
        )

    def _read(self, config: ConfigBuilder, expecting_exception: bool = False) -> EntrypointOutput:
        return _read(config, SyncMode.full_refresh, expecting_exception=expecting_exception)


@freezegun.freeze_time(_NOW.isoformat())
class IncrementalTest(TestCase):

    @HttpMocker()
    def test_given_no_state_when_read_then_use_application_fees_endpoint(self, http_mocker: HttpMocker) -> None:
        _set_up_availability_check("events", http_mocker)
        cursor_value = int(_A_START_DATE.timestamp()) + 1
        http_mocker.get(
            HttpRequest(
                url="https://api.stripe.com/v1/application_fees",
                query_params={"created[gte]": str(int(_A_START_DATE.timestamp())), "created[lte]": str(int(_NOW.timestamp())), "limit": 100},
                headers=_AUTHENTICATION_HEADERS
            ),
            _application_fees_response().with_record(_an_application_fee().with_cursor(cursor_value)).build()
        )
        output = self._read(_config().with_start_date(_A_START_DATE), _NO_STATE)
        assert output.most_recent_state == {"application_fees": {"updated": cursor_value}}

    @HttpMocker()
    def test_given_state_when_read_then_query_events_using_types_and_state_value_plus_1(self, http_mocker: HttpMocker) -> None:
        start_date = _NOW - timedelta(days=40)
        state_value = int((_NOW - timedelta(days=5)).timestamp())
        cursor_value = state_value + 1

        _set_up_availability_check("application_fees", http_mocker)
        _set_up_availability_check("events", http_mocker)
        http_mocker.get(
            HttpRequest(
                url="https://api.stripe.com/v1/events",
                query_params={
                    "created[gte]": str(state_value + _AVOIDING_INCLUSIVE_BOUNDARIES),
                    "created[lte]": str(int(_NOW.timestamp())),
                    "limit": 100,
                    "types[]": ["application_fee.created", "application_fee.refunded"],
                },
                headers=_AUTHENTICATION_HEADERS
            ),
            _events_response().with_record(
                _an_event().with_cursor(cursor_value).with_field(_DATA_FIELD, _an_application_fee().build())
            ).build()
        )

        output = self._read(
            _config().with_start_date(start_date),
            StateBuilder().with_stream_state("application_fees", {"updated": state_value}).build(),
        )

        assert output.most_recent_state == {"application_fees": {"updated": cursor_value}}

    @HttpMocker()
    def test_given_state_and_pagination_when_read_then_return_records(self, http_mocker: HttpMocker) -> None:
        _set_up_availability_check("application_fees", http_mocker)
        _set_up_availability_check("events", http_mocker)
        state_value = int((_NOW - timedelta(days=5)).timestamp())
        http_mocker.get(
            HttpRequest(
                url="https://api.stripe.com/v1/events",
                query_params={
                    "created[gte]": str(state_value + _AVOIDING_INCLUSIVE_BOUNDARIES),
                    "created[lte]": str(int(_NOW.timestamp())),
                    "limit": 100,
                    "types[]": ["application_fee.created", "application_fee.refunded"],
                },
                headers=_AUTHENTICATION_HEADERS
            ),
            _events_response().with_pagination().with_record(
                _an_event().with_id("last_record_id_from_first_page").with_field(_DATA_FIELD, _an_application_fee().build())
            ).build()
        )
        http_mocker.get(
            HttpRequest(
                url="https://api.stripe.com/v1/events",
                query_params={
                    "created[gte]": str(state_value + _AVOIDING_INCLUSIVE_BOUNDARIES),
                    "created[lte]": str(int(_NOW.timestamp())),
                    "starting_after": "last_record_id_from_first_page",
                    "limit": 100,
                    "types[]": ["application_fee.created", "application_fee.refunded"],
                },
                headers=_AUTHENTICATION_HEADERS
            ),
            _events_response().with_record(
                _an_event().with_field(_DATA_FIELD, _an_application_fee().build())
            ).build()
        )

        output = self._read(
            _config(),
            StateBuilder().with_stream_state("application_fees", {"updated": state_value}).build(),
        )

        assert len(output.records) == 2

    @HttpMocker()
    def test_given_state_earlier_than_30_days_when_read_then_query_events_using_types_and_event_lower_boundary(self, http_mocker: HttpMocker) -> None:
        # this seems odd as we would miss some data between start_date and events_lower_boundary
        _set_up_availability_check("application_fees", http_mocker)
        start_date = _NOW - timedelta(days=40)
        state_value = _NOW - timedelta(days=39)
        events_lower_boundary = _NOW - timedelta(days=30)
        http_mocker.get(
            HttpRequest(
                url="https://api.stripe.com/v1/events",
                query_params={
                    "created[gte]": str(int(events_lower_boundary.timestamp())),
                    "created[lte]": str(int(_NOW.timestamp())),
                    "limit": 100,
                    "types[]": ["application_fee.created", "application_fee.refunded"],
                },
                headers=_AUTHENTICATION_HEADERS
            ),
            _events_response().with_record(
                _an_event().with_field(_DATA_FIELD, _an_application_fee().build())
            ).build()
        )

        self._read(
            _config().with_start_date(start_date),
            StateBuilder().with_stream_state("application_fees", {"updated": int(state_value.timestamp())}).build(),
        )

        # request matched http_mocker

    def _read(self, config: ConfigBuilder, state: Optional[Dict[str, Any]], expecting_exception: bool = False) -> EntrypointOutput:
        return _read(config, SyncMode.incremental, state, expecting_exception)
