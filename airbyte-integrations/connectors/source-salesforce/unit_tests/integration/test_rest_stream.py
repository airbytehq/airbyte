# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
import urllib.parse
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from unittest import TestCase

import freezegun
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_protocol.models import SyncMode
from config_builder import ConfigBuilder
from integration.utils import create_base_url, given_authentication, given_stream, read
from salesforce_describe_response_builder import SalesforceDescribeResponseBuilder
from source_salesforce.api import UNSUPPORTED_BULK_API_SALESFORCE_OBJECTS
from source_salesforce.streams import LOOKBACK_SECONDS

_A_FIELD_NAME = "a_field"
_CLIENT_ID = "a_client_id"
_CLIENT_SECRET = "a_client_secret"
_CURSOR_FIELD = "SystemModstamp"
_INSTANCE_URL = "https://instance.salesforce.com"
_BASE_URL = create_base_url(_INSTANCE_URL)
_LOOKBACK_WINDOW = timedelta(seconds=LOOKBACK_SECONDS)
_NOW = datetime.now(timezone.utc)
_REFRESH_TOKEN = "a_refresh_token"
_STREAM_NAME = UNSUPPORTED_BULK_API_SALESFORCE_OBJECTS[0]


def create_http_request(stream_name: str, field_names: List[str], access_token: Optional[str] = None) -> HttpRequest:
    return HttpRequest(
        f"{_BASE_URL}/queryAll?q=SELECT+{','.join(field_names)}+FROM+{stream_name}+",
        headers={"Authorization": f"Bearer {access_token}"} if access_token else None
    )


def create_http_response(field_names: List[str], record_count: int = 1) -> HttpResponse:
    """
    This method does not handle field types for now which may cause some test failures on change if we start considering using some
    fields for calculation. One example of that would be cursor field parsing to datetime.
    """
    records = [{field_name: f"{field_name}_{i}" for field_name in field_names} for i in range(record_count)]
    return HttpResponse(json.dumps({"records": records}))


def _create_field(name: str, _type: Optional[str] = None) -> Dict[str, Any]:
    return {"name": name, "type": _type if _type else "string"}


def _to_url(to_convert: datetime) -> str:
    to_format = to_convert.isoformat(timespec="milliseconds")
    return urllib.parse.quote_plus(to_format)


def _to_partitioned_datetime(to_convert: datetime) -> str:
    return to_convert.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def _calculate_start_time(start_time: datetime) -> datetime:
    # the start is granular to the second hence why we have `0` in terms of milliseconds
    return start_time.replace(microsecond=0)


@freezegun.freeze_time(_NOW.isoformat())
class FullRefreshTest(TestCase):

    def setUp(self) -> None:
        self._config = ConfigBuilder().client_id(_CLIENT_ID).client_secret(_CLIENT_SECRET).refresh_token(_REFRESH_TOKEN)

    @HttpMocker()
    def test_given_error_on_fetch_chunk_of_properties_when_read_then_retry(self, http_mocker: HttpMocker) -> None:
        given_authentication(http_mocker, _CLIENT_ID, _CLIENT_SECRET, _REFRESH_TOKEN, _INSTANCE_URL)
        given_stream(http_mocker, _BASE_URL, _STREAM_NAME, SalesforceDescribeResponseBuilder().field(_A_FIELD_NAME))
        http_mocker.get(
            create_http_request(_STREAM_NAME, [_A_FIELD_NAME]),
            [
                HttpResponse("", status_code=406),
                create_http_response([_A_FIELD_NAME], record_count=1),
            ]
        )

        output = read(_STREAM_NAME, SyncMode.full_refresh, self._config)

        assert len(output.records) == 1


@freezegun.freeze_time(_NOW.isoformat())
class IncrementalTest(TestCase):
    def setUp(self) -> None:
        self._config = ConfigBuilder().client_id(_CLIENT_ID).client_secret(_CLIENT_SECRET).refresh_token(_REFRESH_TOKEN)

        self._http_mocker = HttpMocker()
        self._http_mocker.__enter__()

        given_authentication(self._http_mocker, _CLIENT_ID, _CLIENT_SECRET, _REFRESH_TOKEN, _INSTANCE_URL)
        given_stream(self._http_mocker, _BASE_URL, _STREAM_NAME, SalesforceDescribeResponseBuilder().field(_A_FIELD_NAME).field(_CURSOR_FIELD, "datetime"))

    def tearDown(self) -> None:
        self._http_mocker.__exit__(None, None, None)

    def test_given_no_state_when_read_then_start_sync_from_start(self) -> None:
        start = _calculate_start_time(_NOW - timedelta(days=5))
        # as the start comes from the config, we can't use the same format as `_to_url`
        start_format_url = urllib.parse.quote_plus(start.strftime('%Y-%m-%dT%H:%M:%SZ'))
        self._config.stream_slice_step("P30D").start_date(start)

        self._http_mocker.get(
            HttpRequest(f"{_BASE_URL}/queryAll?q=SELECT+{_A_FIELD_NAME},{_CURSOR_FIELD}+FROM+{_STREAM_NAME}+WHERE+SystemModstamp+%3E%3D+{start_format_url}+AND+SystemModstamp+%3C+{_to_url(_NOW)}"),
            create_http_response([_A_FIELD_NAME], record_count=1),
        )

        read(_STREAM_NAME, SyncMode.incremental, self._config, StateBuilder().with_stream_state(_STREAM_NAME, {}))

        # then HTTP requests are performed

    def test_given_sequential_state_when_read_then_migrate_to_partitioned_state(self) -> None:
        cursor_value = _NOW - timedelta(days=5)
        start = _calculate_start_time(_NOW - timedelta(days=10))
        self._config.stream_slice_step("P30D").start_date(start)
        self._http_mocker.get(
            HttpRequest(f"{_BASE_URL}/queryAll?q=SELECT+{_A_FIELD_NAME},{_CURSOR_FIELD}+FROM+{_STREAM_NAME}+WHERE+SystemModstamp+%3E%3D+{_to_url(cursor_value - _LOOKBACK_WINDOW)}+AND+SystemModstamp+%3C+{_to_url(_NOW)}"),
            create_http_response([_A_FIELD_NAME], record_count=1),
        )

        output = read(_STREAM_NAME, SyncMode.incremental, self._config, StateBuilder().with_stream_state(_STREAM_NAME, {_CURSOR_FIELD: cursor_value.isoformat(timespec="milliseconds")}))

        assert output.most_recent_state.stream_state.dict() == {"state_type": "date-range", "slices": [{"start": _to_partitioned_datetime(start), "end": _to_partitioned_datetime(_NOW)}]}

    def test_given_partitioned_state_when_read_then_sync_missing_partitions_and_update_state(self) -> None:
        missing_chunk = (_NOW - timedelta(days=5), _NOW - timedelta(days=3))
        most_recent_state_value = _NOW - timedelta(days=1)
        start = _calculate_start_time(_NOW - timedelta(days=10))
        state = StateBuilder().with_stream_state(
            _STREAM_NAME,
            {
                "state_type": "date-range",
                "slices": [
                    {"start": start.strftime("%Y-%m-%dT%H:%M:%S.000") + "Z", "end": _to_partitioned_datetime(missing_chunk[0])},
                    {"start": _to_partitioned_datetime(missing_chunk[1]), "end": _to_partitioned_datetime(most_recent_state_value)},
                ]
            }
        )
        self._config.stream_slice_step("P30D").start_date(start)

        self._http_mocker.get(
            HttpRequest(f"{_BASE_URL}/queryAll?q=SELECT+{_A_FIELD_NAME},{_CURSOR_FIELD}+FROM+{_STREAM_NAME}+WHERE+SystemModstamp+%3E%3D+{_to_url(missing_chunk[0])}+AND+SystemModstamp+%3C+{_to_url(missing_chunk[1])}"),
            create_http_response([_A_FIELD_NAME], record_count=1),
        )
        self._http_mocker.get(
            HttpRequest(f"{_BASE_URL}/queryAll?q=SELECT+{_A_FIELD_NAME},{_CURSOR_FIELD}+FROM+{_STREAM_NAME}+WHERE+SystemModstamp+%3E%3D+{_to_url(most_recent_state_value - _LOOKBACK_WINDOW)}+AND+SystemModstamp+%3C+{_to_url(_NOW)}"),
            create_http_response([_A_FIELD_NAME], record_count=1),
        )

        output = read(_STREAM_NAME, SyncMode.incremental, self._config, state)

        # the start is granular to the second hence why we have `000` in terms of milliseconds
        assert output.most_recent_state.stream_state.dict() == {"state_type": "date-range", "slices": [{"start": _to_partitioned_datetime(start), "end": _to_partitioned_datetime(_NOW)}]}
