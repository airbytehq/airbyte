# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
import urllib.parse
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from unittest import TestCase

import freezegun
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_protocol.models import SyncMode
from config_builder import ConfigBuilder
from integration.utils import create_base_url, given_authentication, given_stream, read
from salesforce_describe_response_builder import SalesforceDescribeResponseBuilder
from salesforce_job_response_builder import SalesforceJobResponseBuilder
from source_salesforce.streams import LOOKBACK_SECONDS

_A_FIELD_NAME = "a_field"
_ACCESS_TOKEN = "an_access_token"
_CLIENT_ID = "a_client_id"
_CLIENT_SECRET = "a_client_secret"
_CURSOR_FIELD = "SystemModstamp"
_INSTANCE_URL = "https://instance.salesforce.com"
_JOB_ID = "a-job-id"
_LOOKBACK_WINDOW = timedelta(seconds=LOOKBACK_SECONDS)
_NOW = datetime.now(timezone.utc)
_REFRESH_TOKEN = "a_refresh_token"
_STREAM_NAME = "a_stream_name"

_BASE_URL = create_base_url(_INSTANCE_URL)


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
class BulkStreamTest(TestCase):

    def setUp(self) -> None:
        self._config = ConfigBuilder().client_id(_CLIENT_ID).client_secret(_CLIENT_SECRET).refresh_token(_REFRESH_TOKEN)

        self._http_mocker = HttpMocker()
        self._http_mocker.__enter__()

        given_authentication(self._http_mocker, _CLIENT_ID, _CLIENT_SECRET, _REFRESH_TOKEN, _INSTANCE_URL)

    def tearDown(self) -> None:
        self._http_mocker.__exit__(None, None, None)

    def test_when_read_then_create_job_and_extract_records_from_result(self) -> None:
        given_stream(self._http_mocker, _BASE_URL, _STREAM_NAME, SalesforceDescribeResponseBuilder().field(_A_FIELD_NAME))
        self._http_mocker.post(
            HttpRequest(f"{_BASE_URL}/jobs/query", body=json.dumps({"operation": "queryAll", "query": "SELECT a_field FROM a_stream_name", "contentType": "CSV", "columnDelimiter": "COMMA", "lineEnding": "LF"})),
            HttpResponse(json.dumps({"id": _JOB_ID})),
        )
        self._http_mocker.get(
            HttpRequest(f"{_BASE_URL}/jobs/query/{_JOB_ID}"),
            SalesforceJobResponseBuilder().with_id(_JOB_ID).with_state("JobComplete").build(),
        )
        self._http_mocker.get(
            HttpRequest(f"{_BASE_URL}/jobs/query/{_JOB_ID}/results"),
            HttpResponse(f"{_A_FIELD_NAME}\nfield_value"),
        )

        output = read(_STREAM_NAME, SyncMode.full_refresh, self._config)

        assert len(output.records) == 1

    def test_given_incremental_when_read_then_create_job_and_extract_records_from_result(self) -> None:
        start_date = (_NOW - timedelta(days=10)).replace(microsecond=0)
        first_upper_boundary = start_date + timedelta(days=7)
        self._config.start_date(start_date).stream_slice_step("P7D")
        given_stream(self._http_mocker, _BASE_URL, _STREAM_NAME, SalesforceDescribeResponseBuilder().field(_A_FIELD_NAME).field(_CURSOR_FIELD, "datetime"))
        self._create_sliced_job(start_date, first_upper_boundary, "first_slice_job_id", self._generate_csv([_A_FIELD_NAME, _CURSOR_FIELD], count=2))
        self._create_sliced_job(first_upper_boundary, _NOW, "second_slice_job_id", self._generate_csv([_A_FIELD_NAME, _CURSOR_FIELD], count=1))

        output = read(_STREAM_NAME, SyncMode.incremental, self._config)

        assert len(output.records) == 3

    def test_given_slice_fails_when_read_then_state_is_partitioned(self) -> None:
        start_date = (_NOW - timedelta(days=20)).replace(microsecond=0)
        slice_range = timedelta(days=7)
        first_upper_boundary = start_date + slice_range
        second_upper_boundary = first_upper_boundary + slice_range
        self._config.start_date(start_date).stream_slice_step("P7D")
        given_stream(self._http_mocker, _BASE_URL, _STREAM_NAME, SalesforceDescribeResponseBuilder().field(_A_FIELD_NAME).field(_CURSOR_FIELD, "datetime"))
        self._create_sliced_job(start_date, first_upper_boundary, "first_slice_job_id", self._generate_csv([_A_FIELD_NAME, _CURSOR_FIELD], count=2))
        self._http_mocker.post(
            self._create_job_creation_request(first_upper_boundary, second_upper_boundary),
            HttpResponse("", status_code=400),
        )
        self._create_sliced_job(second_upper_boundary, _NOW, "third_slice_job_id", self._generate_csv([_A_FIELD_NAME, _CURSOR_FIELD], count=1))

        output = read(_STREAM_NAME, SyncMode.incremental, self._config)

        assert len(output.records) == 3
        assert len(output.most_recent_state.stream_state.dict()["slices"]) == 2

    def _create_sliced_job(self, start_date: datetime, first_upper_boundary: datetime, job_id: str, job_result: str) -> None:
        self._http_mocker.post(
            self._create_job_creation_request(start_date, first_upper_boundary),
            HttpResponse(json.dumps({"id": job_id})),
        )
        self._http_mocker.get(
            HttpRequest(f"{_BASE_URL}/jobs/query/{job_id}"),
            SalesforceJobResponseBuilder().with_id(_JOB_ID).with_state("JobComplete").build(),
        )
        self._http_mocker.get(
            HttpRequest(f"{_BASE_URL}/jobs/query/{job_id}/results"),
            HttpResponse(job_result),
        )
        self._http_mocker._mock_request_method(  # FIXME to add DELETE method in airbyte_cdk tests
            "delete",
            HttpRequest(f"{_BASE_URL}/jobs/query/{job_id}"),
            HttpResponse(job_result),
        )

    def _create_job_creation_request(self, start_date: datetime, first_upper_boundary: datetime) -> HttpRequest:
        return HttpRequest(f"{_BASE_URL}/jobs/query", body=json.dumps({
            "operation": "queryAll",
            "query": f"SELECT a_field, SystemModstamp FROM a_stream_name WHERE SystemModstamp >= {start_date.isoformat(timespec='milliseconds')} AND SystemModstamp < {first_upper_boundary.isoformat(timespec='milliseconds')}",
            "contentType": "CSV",
            "columnDelimiter": "COMMA",
            "lineEnding": "LF"
        }))

    def _generate_csv(self, fields: List[str], count: int = 1) -> str:
        record = ','.join([f"{field}_value" for field in fields])
        records = '\n'.join([record for _ in range(count)])
        return f"{','.join(fields)}\n{records}"
