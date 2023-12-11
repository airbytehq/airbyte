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
from airbyte_cdk.test.mock_http.response_builder import create_builders_from_resource, find_template, FieldPath, HttpResponseBuilder, RecordBuilder
from airbyte_protocol.models import SyncMode, ConfiguredAirbyteCatalog, AirbyteStreamStatus
from source_stripe import SourceStripe
from integration.config import ConfigBuilder
from integration.pagination import StripePaginationStrategy


_STREAM_NAME = "events"
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
    return ConfigBuilder().with_account_id(_ACCOUNT_ID).with_client_secret(_CLIENT_SECRET)


def _catalog(sync_mode: SyncMode) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(_STREAM_NAME, sync_mode).build()


def _source(catalog: ConfiguredAirbyteCatalog) -> SourceStripe:
    return SourceStripe(catalog)


def _create_builders() -> Tuple[RecordBuilder, HttpResponseBuilder]:
    return create_builders_from_resource(
        find_template("events", __file__),
        FieldPath("data"),
        record_id_path=FieldPath("id"),
        record_cursor_path=FieldPath("created"),
        pagination_strategy=StripePaginationStrategy(),
    )


def _a_record() -> RecordBuilder:
    return _create_builders()[0]


def _a_response() -> HttpResponseBuilder:
    return _create_builders()[1]


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
        http_mocker.get(
            HttpRequest(
                url="https://api.stripe.com/v1/events",
                query_params={"created[gte]": str(int(_A_START_DATE.timestamp())), "created[lte]": str(int(_NOW.timestamp())), "limit": 100},
                headers=_AUTHENTICATION_HEADERS
            ),
            _a_response().with_record(_a_record()).build()
        )
        output = self._read(_config().with_start_date(_A_START_DATE))
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_many_pages_when_read_then_return_records(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            HttpRequest(
                url="https://api.stripe.com/v1/events",
                query_params={"created[gte]": str(int(_A_START_DATE.timestamp())), "created[lte]": str(int(_NOW.timestamp())), "limit": 100},
                headers=_AUTHENTICATION_HEADERS,
            ),
            _a_response().with_pagination().with_record(_a_record().with_id("last_record_id_from_first_page")).build()
        )
        http_mocker.get(
            HttpRequest(
                url="https://api.stripe.com/v1/events",
                query_params={
                    "starting_after": "last_record_id_from_first_page",
                    "created[gte]": str(int(_A_START_DATE.timestamp())),
                    "created[lte]": str(int(_NOW.timestamp())),
                    "limit": 100,
                },
                headers=_AUTHENTICATION_HEADERS,
            ),
            _a_response().with_record(_a_record()).build()
        )
        output = self._read(_config().with_start_date(_A_START_DATE))
        assert len(output.records) == 2

    @HttpMocker()
    def test_given_start_date_before_30_days_stripe_limit_when_read_then_request_more_than_30_days(self, http_mocker: HttpMocker) -> None:
        start_date = _NOW - timedelta(days=60)
        http_mocker.get(
            HttpRequest(
                url="https://api.stripe.com/v1/events",
                query_params={"created[gte]": str(int(start_date.timestamp())), "created[lte]": str(int(_NOW.timestamp())), "limit": 100},
                headers=_AUTHENTICATION_HEADERS,
            ),
            _a_response().build()
        )
        self._read(_config().with_start_date(start_date))
        # request matched http_mocker

    @HttpMocker()
    def test_given_lookback_window_when_read_then_request_before_start_date(self, http_mocker: HttpMocker) -> None:
        start_date = _NOW - timedelta(days=30)
        lookback_window = timedelta(days=10)
        http_mocker.get(
            HttpRequest(
                url="https://api.stripe.com/v1/events",
                query_params={"created[gte]": str(int((start_date - lookback_window).timestamp())), "created[lte]": str(int(_NOW.timestamp())), "limit": 100},
                headers=_AUTHENTICATION_HEADERS,
            ),
            _a_response().build()
        )

        self._read(_config().with_start_date(start_date).with_lookback_window_in_days(lookback_window.days))

        # request matched http_mocker

    @HttpMocker()
    def test_given_slice_range_when_read_then_request_before_start_date(self, http_mocker: HttpMocker) -> None:
        start_date = _NOW - timedelta(days=30)
        slice_range = timedelta(days=20)
        slice_datetime = start_date + slice_range
        http_mocker.get(
            HttpRequest(
                url="https://api.stripe.com/v1/events",
                query_params={"created[gte]": str(int(start_date.timestamp())), "created[lte]": str(int(slice_datetime.timestamp())), "limit": 100},
                headers=_AUTHENTICATION_HEADERS,
            ),
            _a_response().build()
        )
        http_mocker.get(
            HttpRequest(
                url="https://api.stripe.com/v1/events",
                query_params={"created[gte]": str(int(slice_datetime.timestamp()) + 1), "created[lte]": str(int(_NOW.timestamp())), "limit": 100},
                headers=_AUTHENTICATION_HEADERS,
            ),
            _a_response().build()
        )

        self._read(_config().with_start_date(start_date).with_slice_range_in_days(slice_range.days))

    @HttpMocker()
    def test_given_http_status_400_when_read_then_stream_is_ignored(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            HttpRequest(
                url="https://api.stripe.com/v1/events",
                query_params=ANY_QUERY_PARAMS,
                headers=_AUTHENTICATION_HEADERS
            ),
            HttpResponse(
                json.dumps({
                    "error": {
                        "code": "parameter_invalid_integer",
                        "doc_url": "https://stripe.com/docs/error-codes/parameter-invalid-integer",
                        "message": "Invalid integer: not_an_integer",
                        "param": "limit",
                        "request_log_url": "https://dashboard.stripe.com/test/logs/req_yVDTOo9Jrd1suG?t=1701959063",
                        "type": "invalid_request_error"
                    }
                }),
                400)
        )
        output = self._read(_config().with_start_date(_A_START_DATE))
        assert len(output.get_stream_statuses(_STREAM_NAME)) == 0

    @HttpMocker()
    def test_given_http_status_401_when_read_then_stream_is_incomplete(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            HttpRequest(
                url="https://api.stripe.com/v1/events",
                query_params=ANY_QUERY_PARAMS,
                headers=_AUTHENTICATION_HEADERS
            ),
            HttpResponse(
                json.dumps({
                    "error": {
                        "message": "Invalid API Key provided: sk_test_*****************************************************mFeM",
                        "type": "invalid_request_error"
                    }
                }),
                401
            )
        )
        output = self._read(_config().with_start_date(_A_START_DATE), expecting_exception=True)
        assert output.get_stream_statuses(_STREAM_NAME) == [AirbyteStreamStatus.INCOMPLETE]

    @HttpMocker()
    def test_given_rate_limited_when_read_then_retry_and_return_records(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            HttpRequest(
                url="https://api.stripe.com/v1/events",
                query_params=ANY_QUERY_PARAMS,
                headers=_AUTHENTICATION_HEADERS
            ),
            [
                HttpResponse(
                    json.dumps({
                        "error": {
                            "message": "Request rate limit exceeded. Learn more about rate limits here https://stripe.com/docs/rate-limits.",
                            "type": "invalid_request_error",
                            "code": "rate_limit",
                            "doc_url": "https://stripe.com/docs/error-codes/rate-limit"
                        }
                    }),
                    429
                ),
                _a_response().with_record(_a_record()).build(),
            ]
        )
        output = self._read(_config().with_start_date(_A_START_DATE))
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_http_status_500_once_before_200_when_read_then_retry_and_return_records(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            HttpRequest(
                url="https://api.stripe.com/v1/events",
                query_params=ANY_QUERY_PARAMS,
                headers=_AUTHENTICATION_HEADERS
            ),
            [_HTTP_RESPONSE_STATUS_500, _a_response().with_record(_a_record()).build()]
        )
        output = self._read(_config().with_start_date(_A_START_DATE))
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_http_status_500_on_availability_when_read_then_stream_is_incomplete(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            HttpRequest(
                url="https://api.stripe.com/v1/events",
                query_params=ANY_QUERY_PARAMS,
                headers=_AUTHENTICATION_HEADERS
            ),
            [_HTTP_RESPONSE_STATUS_500]
        )
        output = self._read(_config().with_start_date(_A_START_DATE), expecting_exception=True)
        assert output.get_stream_statuses(_STREAM_NAME) == [AirbyteStreamStatus.INCOMPLETE]

    @HttpMocker()
    def test_when_read_then_validate_availability_for_full_refresh_and_incremental(self, http_mocker: HttpMocker) -> None:
        request = HttpRequest(url="https://api.stripe.com/v1/events", query_params=ANY_QUERY_PARAMS, headers=_AUTHENTICATION_HEADERS)
        http_mocker.get(
            request,
            _a_response().build()
        )
        self._read(_config().with_start_date(_A_START_DATE))
        http_mocker.assert_number_of_calls(request, 3)  # one call for full_refresh availability, one call for incremental availability and one call for the actual read

    def _read(self, config: ConfigBuilder, expecting_exception: bool = False) -> EntrypointOutput:
        return _read(config, SyncMode.full_refresh, expecting_exception=expecting_exception)


@freezegun.freeze_time(_NOW.isoformat())
class IncrementalTest(TestCase):

    @HttpMocker()
    def test_given_no_initial_state_when_read_then_return_state_based_on_cursor_field(self, http_mocker: HttpMocker) -> None:
        cursor_value = int(_A_START_DATE.timestamp()) + 1
        http_mocker.get(
            HttpRequest(
                url="https://api.stripe.com/v1/events",
                query_params={"created[gte]": str(int(_A_START_DATE.timestamp())), "created[lte]": str(int(_NOW.timestamp())), "limit": 100},
                headers=_AUTHENTICATION_HEADERS
            ),
            _a_response().with_record(_a_record().with_cursor(cursor_value)).build()
        )
        output = self._read(_config().with_start_date(_A_START_DATE), {})
        assert output.most_recent_state == {"events": {"created": cursor_value}}

    @HttpMocker()
    def test_given_state_when_read_then_use_state_for_query_params(self, http_mocker: HttpMocker) -> None:
        state_value = int(_A_START_DATE.timestamp()) + 1
        availability_check_requests = HttpRequest(
            url="https://api.stripe.com/v1/events",
            query_params=ANY_QUERY_PARAMS,
            headers=_AUTHENTICATION_HEADERS
        )
        http_mocker.get(
            availability_check_requests,
            _a_response().with_record(_a_record()).build()
        )
        http_mocker.get(
            HttpRequest(
                url="https://api.stripe.com/v1/events",
                query_params={"created[gte]": str(state_value + _AVOIDING_INCLUSIVE_BOUNDARIES), "created[lte]": str(int(_NOW.timestamp())), "limit": 100},
                headers=_AUTHENTICATION_HEADERS
            ),
            _a_response().with_record(_a_record()).build()
        )

        self._read(
            _config().with_start_date(_A_START_DATE),
            StateBuilder().with_stream_state("events", {"created": state_value}).build()
        )

        # request matched http_mocker

    @HttpMocker()
    def test_given_state_more_recent_than_cursor_when_read_then_return_state_based_on_cursor_field(self, http_mocker: HttpMocker) -> None:
        cursor_value = int(_A_START_DATE.timestamp()) + 1
        more_recent_than_record_cursor = int(_NOW.timestamp()) - 1
        http_mocker.get(
            HttpRequest(
                url="https://api.stripe.com/v1/events",
                query_params={"created[gte]": str(int(_A_START_DATE.timestamp())), "created[lte]": str(int(_NOW.timestamp())), "limit": 100},
                headers=_AUTHENTICATION_HEADERS
            ),
            _a_response().with_record(_a_record().with_cursor(cursor_value)).build()
        )
        output = self._read(
            _config().with_start_date(_A_START_DATE),
            StateBuilder().with_stream_state("events", {"created": more_recent_than_record_cursor}).build()
        )
        assert output.most_recent_state == {"events": {"created": more_recent_than_record_cursor}}

    def _read(self, config: ConfigBuilder, state: Optional[Dict[str, Any]], expecting_exception: bool = False) -> EntrypointOutput:
        return _read(config, SyncMode.incremental, state, expecting_exception)
