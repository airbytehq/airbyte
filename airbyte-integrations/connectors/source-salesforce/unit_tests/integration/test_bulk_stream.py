# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
import urllib.parse
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from unittest import TestCase

import freezegun
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_protocol.models import AirbyteStreamStatus, SyncMode
from config_builder import ConfigBuilder
from integration.test_rest_stream import create_http_request as create_standard_http_request
from integration.test_rest_stream import create_http_response as create_standard_http_response
from integration.utils import create_base_url, given_authentication, given_stream, read
from salesforce_describe_response_builder import SalesforceDescribeResponseBuilder
from salesforce_job_response_builder import JobCreateResponseBuilder, JobInfoResponseBuilder
from source_salesforce.streams import LOOKBACK_SECONDS

_A_FIELD_NAME = "a_field"
_ACCESS_TOKEN = "an_access_token"
_CLIENT_ID = "a_client_id"
_CLIENT_SECRET = "a_client_secret"
_CURSOR_FIELD = "SystemModstamp"
_INCREMENTAL_FIELDS = [_A_FIELD_NAME, _CURSOR_FIELD]
_INCREMENTAL_SCHEMA_BUILDER = SalesforceDescribeResponseBuilder().field(_A_FIELD_NAME).field(_CURSOR_FIELD, "datetime")  # re-using same fields as _INCREMENTAL_FIELDS
_INSTANCE_URL = "https://instance.salesforce.com"
_JOB_ID = "a-job-id"
_LOOKBACK_WINDOW = timedelta(seconds=LOOKBACK_SECONDS)
_NOW = datetime.now(timezone.utc)
_REFRESH_TOKEN = "a_refresh_token"
_METHOD_FAILURE_HTTP_STATUS = 420
_RETRYABLE_RESPONSE = HttpResponse("{}", _METHOD_FAILURE_HTTP_STATUS)  # TODO: document what the body actually is on 420 errors
_SECOND_PAGE_LOCATOR = "second-page-locator"
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

        given_authentication(self._http_mocker, _CLIENT_ID, _CLIENT_SECRET, _REFRESH_TOKEN, _INSTANCE_URL, _ACCESS_TOKEN)

    def tearDown(self) -> None:
        self._http_mocker.__exit__(None, None, None)

    def test_when_read_then_create_job_and_extract_records_from_result(self) -> None:
        given_stream(self._http_mocker, _BASE_URL, _STREAM_NAME, SalesforceDescribeResponseBuilder().field(_A_FIELD_NAME))
        self._http_mocker.post(
            self._make_full_job_request([_A_FIELD_NAME]),
            JobCreateResponseBuilder().with_id(_JOB_ID).build(),
        )
        self._http_mocker.get(
            HttpRequest(f"{_BASE_URL}/jobs/query/{_JOB_ID}"),
            [
                JobInfoResponseBuilder().with_id(_JOB_ID).with_state("InProgress").build(),
                JobInfoResponseBuilder().with_id(_JOB_ID).with_state("UploadComplete").build(),
                JobInfoResponseBuilder().with_id(_JOB_ID).with_state("JobComplete").build(),
            ],
        )
        self._http_mocker.get(
            HttpRequest(f"{_BASE_URL}/jobs/query/{_JOB_ID}/results"),
            HttpResponse(f"{_A_FIELD_NAME}\nfield_value"),
        )
        self._mock_delete_job(_JOB_ID)

        output = read(_STREAM_NAME, SyncMode.full_refresh, self._config)

        assert len(output.records) == 1

    def test_given_locator_when_read_then_extract_records_from_both_pages(self):
        given_stream(self._http_mocker, _BASE_URL, _STREAM_NAME, SalesforceDescribeResponseBuilder().field(_A_FIELD_NAME))
        self._http_mocker.post(
            self._make_full_job_request([_A_FIELD_NAME]),
            JobCreateResponseBuilder().with_id(_JOB_ID).build(),
        )
        self._http_mocker.get(
            HttpRequest(f"{_BASE_URL}/jobs/query/{_JOB_ID}"),
            JobInfoResponseBuilder().with_id(_JOB_ID).with_state("JobComplete").build(),
        )
        self._http_mocker.get(
            HttpRequest(f"{_BASE_URL}/jobs/query/{_JOB_ID}/results"),
            HttpResponse(f"{_A_FIELD_NAME}\nfield_value", headers={"Sforce-Locator": _SECOND_PAGE_LOCATOR}),
        )
        self._http_mocker.get(
            HttpRequest(f"{_BASE_URL}/jobs/query/{_JOB_ID}/results", query_params={"locator": _SECOND_PAGE_LOCATOR}),
            HttpResponse(f"{_A_FIELD_NAME}\nanother_field_value"),
        )
        self._mock_delete_job(_JOB_ID)

        output = read(_STREAM_NAME, SyncMode.full_refresh, self._config)

        assert len(output.records) == 2

    def test_given_job_creation_have_transient_error_when_read_then_sync_properly(self):
        given_stream(self._http_mocker, _BASE_URL, _STREAM_NAME, SalesforceDescribeResponseBuilder().field(_A_FIELD_NAME))
        self._http_mocker.post(
            self._make_full_job_request([_A_FIELD_NAME]),
            [
                _RETRYABLE_RESPONSE,
                JobCreateResponseBuilder().with_id(_JOB_ID).build(),
            ],
        )
        self._http_mocker.get(
            HttpRequest(f"{_BASE_URL}/jobs/query/{_JOB_ID}"),
            JobInfoResponseBuilder().with_id(_JOB_ID).with_state("JobComplete").build(),
        )
        self._http_mocker.get(
            HttpRequest(f"{_BASE_URL}/jobs/query/{_JOB_ID}/results"),
            HttpResponse(f"{_A_FIELD_NAME}\nfield_value"),
        )
        self._mock_delete_job(_JOB_ID)

        output = read(_STREAM_NAME, SyncMode.full_refresh, self._config)

        assert len(output.errors) == 0
        assert len(output.records) == 1

    def test_given_bulk_restrictions_when_read_then_switch_to_standard(self):
        given_stream(self._http_mocker, _BASE_URL, _STREAM_NAME, SalesforceDescribeResponseBuilder().field(_A_FIELD_NAME))
        self._http_mocker.post(
            self._make_full_job_request([_A_FIELD_NAME]),
            [
                HttpResponse("[{}]", 403),
                JobCreateResponseBuilder().with_id(_JOB_ID).build(),
            ],
        )
        self._http_mocker.get(
            create_standard_http_request(_STREAM_NAME, [_A_FIELD_NAME]),
            create_standard_http_response([_A_FIELD_NAME]),
        )

        output = read(_STREAM_NAME, SyncMode.full_refresh, self._config)

        assert len(output.records) == 1

    def test_given_non_transient_error_on_job_creation_when_read_then_fail_sync(self):
        given_stream(self._http_mocker, _BASE_URL, _STREAM_NAME, SalesforceDescribeResponseBuilder().field(_A_FIELD_NAME))
        self._http_mocker.post(
            self._make_full_job_request([_A_FIELD_NAME]),
            HttpResponse(json.dumps([{"errorCode": "API_ERROR", "message": "Implementation restriction... <can't complete the error message as I can't reproduce this issue>"}]), 400),
        )

        output = read(_STREAM_NAME, SyncMode.full_refresh, self._config)

        assert output.get_stream_statuses(_STREAM_NAME)[-1] == AirbyteStreamStatus.INCOMPLETE

    def test_given_job_is_aborted_when_read_then_fail_sync(self):
        given_stream(self._http_mocker, _BASE_URL, _STREAM_NAME, SalesforceDescribeResponseBuilder().field(_A_FIELD_NAME))
        self._http_mocker.post(
            self._make_full_job_request([_A_FIELD_NAME]),
            JobCreateResponseBuilder().with_id(_JOB_ID).build(),
        )
        self._http_mocker.get(
            HttpRequest(f"{_BASE_URL}/jobs/query/{_JOB_ID}"),
            JobInfoResponseBuilder().with_id(_JOB_ID).with_state("Aborted").build(),
        )
        self._mock_delete_job(_JOB_ID)

        output = read(_STREAM_NAME, SyncMode.full_refresh, self._config)

        assert output.get_stream_statuses(_STREAM_NAME)[-1] == AirbyteStreamStatus.INCOMPLETE

    def test_given_job_is_failed_when_read_then_switch_to_standard(self):
        given_stream(self._http_mocker, _BASE_URL, _STREAM_NAME, SalesforceDescribeResponseBuilder().field(_A_FIELD_NAME))
        self._http_mocker.post(
            self._make_full_job_request([_A_FIELD_NAME]),
            JobCreateResponseBuilder().with_id(_JOB_ID).build(),
        )
        self._http_mocker.get(
            HttpRequest(f"{_BASE_URL}/jobs/query/{_JOB_ID}"),
            JobInfoResponseBuilder().with_id(_JOB_ID).with_state("Failed").build(),
        )
        self._http_mocker.get(
            create_standard_http_request(_STREAM_NAME, [_A_FIELD_NAME], _ACCESS_TOKEN),
            create_standard_http_response([_A_FIELD_NAME]),
        )
        self._mock_delete_job(_JOB_ID)

        output = read(_STREAM_NAME, SyncMode.full_refresh, self._config)

        assert len(output.records) == 1

    def test_given_retryable_error_on_download_job_result_when_read_then_extract_records(self):
        given_stream(self._http_mocker, _BASE_URL, _STREAM_NAME, SalesforceDescribeResponseBuilder().field(_A_FIELD_NAME))
        self._http_mocker.post(
            self._make_full_job_request([_A_FIELD_NAME]),
            JobCreateResponseBuilder().with_id(_JOB_ID).build(),
        )
        self._http_mocker.get(
            HttpRequest(f"{_BASE_URL}/jobs/query/{_JOB_ID}"),
            JobInfoResponseBuilder().with_id(_JOB_ID).with_state("JobComplete").build(),
        )
        self._http_mocker.get(
            HttpRequest(f"{_BASE_URL}/jobs/query/{_JOB_ID}/results"),
            [
                _RETRYABLE_RESPONSE,
                HttpResponse(f"{_A_FIELD_NAME}\nfield_value"),
            ],
        )
        self._mock_delete_job(_JOB_ID)

        output = read(_STREAM_NAME, SyncMode.full_refresh, self._config)

        assert len(output.records) == 1

    def test_given_retryable_error_on_delete_job_result_when_read_then_do_not_break(self):
        given_stream(self._http_mocker, _BASE_URL, _STREAM_NAME, SalesforceDescribeResponseBuilder().field(_A_FIELD_NAME))
        self._http_mocker.post(
            self._make_full_job_request([_A_FIELD_NAME]),
            JobCreateResponseBuilder().with_id(_JOB_ID).build(),
        )
        self._http_mocker.get(
            HttpRequest(f"{_BASE_URL}/jobs/query/{_JOB_ID}"),
            JobInfoResponseBuilder().with_id(_JOB_ID).with_state("JobComplete").build(),
        )
        self._http_mocker.get(
            HttpRequest(f"{_BASE_URL}/jobs/query/{_JOB_ID}/results"),
            HttpResponse(f"{_A_FIELD_NAME}\nfield_value"),
        )
        self._http_mocker.delete(
            HttpRequest(f"{_BASE_URL}/jobs/query/{_JOB_ID}"),
            [
                _RETRYABLE_RESPONSE,
                HttpResponse(""),
            ],
        )

        output = read(_STREAM_NAME, SyncMode.full_refresh, self._config)

        assert output.get_stream_statuses(_STREAM_NAME)[-1] == AirbyteStreamStatus.COMPLETE

    def test_given_non_retryable_error_on_delete_job_result_when_read_then_fail_to_sync(self):
        """
        This is interesting: right now, we retry with the same policies has the other requests but it seems fair to just be a best effort,
        catch everything and not retry
        """
        given_stream(self._http_mocker, _BASE_URL, _STREAM_NAME, SalesforceDescribeResponseBuilder().field(_A_FIELD_NAME))
        self._http_mocker.post(
            self._make_full_job_request([_A_FIELD_NAME]),
            JobCreateResponseBuilder().with_id(_JOB_ID).build(),
        )
        self._http_mocker.get(
            HttpRequest(f"{_BASE_URL}/jobs/query/{_JOB_ID}"),
            JobInfoResponseBuilder().with_id(_JOB_ID).with_state("JobComplete").build(),
        )
        self._http_mocker.get(
            HttpRequest(f"{_BASE_URL}/jobs/query/{_JOB_ID}/results"),
            HttpResponse(f"{_A_FIELD_NAME}\nfield_value"),
        )
        self._http_mocker.delete(
            HttpRequest(f"{_BASE_URL}/jobs/query/{_JOB_ID}"),
            HttpResponse("", 429),
        )

        output = read(_STREAM_NAME, SyncMode.full_refresh, self._config)

        assert output.get_stream_statuses(_STREAM_NAME)[-1] == AirbyteStreamStatus.INCOMPLETE

    def test_given_incremental_when_read_then_create_job_and_extract_records_from_result(self) -> None:
        start_date = (_NOW - timedelta(days=10)).replace(microsecond=0)
        first_upper_boundary = start_date + timedelta(days=7)
        self._config.start_date(start_date).stream_slice_step("P7D")
        given_stream(self._http_mocker, _BASE_URL, _STREAM_NAME, _INCREMENTAL_SCHEMA_BUILDER)
        self._create_sliced_job(start_date, first_upper_boundary, _INCREMENTAL_FIELDS, "first_slice_job_id", record_count=2)
        self._create_sliced_job(first_upper_boundary, _NOW, _INCREMENTAL_FIELDS, "second_slice_job_id", record_count=1)

        output = read(_STREAM_NAME, SyncMode.incremental, self._config)

        assert len(output.records) == 3

    def test_given_slice_fails_when_read_then_state_is_partitioned(self) -> None:
        start_date = (_NOW - timedelta(days=20)).replace(microsecond=0)
        slice_range = timedelta(days=7)
        first_upper_boundary = start_date + slice_range
        second_upper_boundary = first_upper_boundary + slice_range
        self._config.start_date(start_date).stream_slice_step("P7D")
        given_stream(self._http_mocker, _BASE_URL, _STREAM_NAME, _INCREMENTAL_SCHEMA_BUILDER)
        self._create_sliced_job(start_date, first_upper_boundary, _INCREMENTAL_FIELDS, "first_slice_job_id", record_count=2)
        self._http_mocker.post(
            self._make_sliced_job_request(first_upper_boundary, second_upper_boundary, _INCREMENTAL_FIELDS),
            HttpResponse("", status_code=400),
        )
        self._create_sliced_job(second_upper_boundary, _NOW, _INCREMENTAL_FIELDS, "third_slice_job_id", record_count=1)

        output = read(_STREAM_NAME, SyncMode.incremental, self._config)

        assert len(output.records) == 3
        assert len(output.most_recent_state.stream_state.dict()["slices"]) == 2

    def _create_sliced_job(self, lower_boundary: datetime, upper_boundary: datetime, fields: List[str], job_id: str, record_count: int) -> None:
        self._http_mocker.post(
            self._make_sliced_job_request(lower_boundary, upper_boundary, fields),
            JobCreateResponseBuilder().with_id(job_id).build(),
        )
        self._http_mocker.get(
            HttpRequest(f"{_BASE_URL}/jobs/query/{job_id}"),
            JobInfoResponseBuilder().with_id(_JOB_ID).with_state("JobComplete").build(),
        )
        self._http_mocker.get(
            HttpRequest(f"{_BASE_URL}/jobs/query/{job_id}/results"),
            HttpResponse(self._generate_csv(fields, count=record_count)),
        )
        self._mock_delete_job(job_id)

    def _mock_delete_job(self, job_id: str) -> None:
        self._http_mocker.delete(
            HttpRequest(f"{_BASE_URL}/jobs/query/{job_id}"),
            HttpResponse(""),
        )

    def _make_sliced_job_request(self, lower_boundary: datetime, upper_boundary: datetime, fields: List[str]) -> HttpRequest:
        return self._build_job_creation_request(f"SELECT {', '.join(fields)} FROM a_stream_name WHERE SystemModstamp >= {lower_boundary.isoformat(timespec='milliseconds')} AND SystemModstamp < {upper_boundary.isoformat(timespec='milliseconds')}")

    def _make_full_job_request(self, fields: List[str]) -> HttpRequest:
        return self._build_job_creation_request(f"SELECT {', '.join(fields)} FROM a_stream_name")

    def _generate_csv(self, fields: List[str], count: int = 1) -> str:
        """
        This method does not handle field types for now which may cause some test failures on change if we start considering using some
        fields for calculation. One example of that would be cursor field parsing to datetime.
        """
        record = ','.join([f"{field}_value" for field in fields])
        records = '\n'.join([record for _ in range(count)])
        return f"{','.join(fields)}\n{records}"

    def _build_job_creation_request(self, query: str) -> HttpRequest:
        return HttpRequest(f"{_BASE_URL}/jobs/query", body=json.dumps({
            "operation": "queryAll",
            "query": query,
            "contentType": "CSV",
            "columnDelimiter": "COMMA",
            "lineEnding": "LF"
        }))
