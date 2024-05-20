#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import csv
import io
import logging
import re
from datetime import datetime, timedelta
from typing import List
from unittest.mock import Mock, patch

import freezegun
import pendulum
import pytest
import requests_mock
from airbyte_cdk.models import (
    AirbyteStateBlob,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    StreamDescriptor,
    SyncMode,
    Type,
)
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.concurrent.adapters import StreamFacade
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_cdk.utils import AirbyteTracedException
from conftest import encoding_symbols_parameters, generate_stream
from requests.exceptions import ChunkedEncodingError, HTTPError
from salesforce_job_response_builder import JobInfoResponseBuilder
from source_salesforce.api import Salesforce
from source_salesforce.exceptions import AUTHENTICATION_ERROR_MESSAGE_MAPPING
from source_salesforce.source import SourceSalesforce
from source_salesforce.streams import (
    CSV_FIELD_SIZE_LIMIT,
    BulkIncrementalSalesforceStream,
    BulkSalesforceStream,
    BulkSalesforceSubStream,
    IncrementalRestSalesforceStream,
    RestSalesforceStream,
)

_A_CHUNKED_RESPONSE = [b"first chunk", b"second chunk"]
_A_JSON_RESPONSE = {"id": "any id"}
_A_SUCCESSFUL_JOB_CREATION_RESPONSE = JobInfoResponseBuilder().with_state("JobComplete").get_response()
_A_PK = "a_pk"
_A_STREAM_NAME = "a_stream_name"

_NUMBER_OF_DOWNLOAD_TRIES = 5
_FIRST_CALL_FROM_JOB_CREATION = 1

_ANY_CATALOG = ConfiguredAirbyteCatalog.parse_obj({"streams": []})
_ANY_CONFIG = {}
_ANY_STATE = None


@pytest.mark.parametrize(
    "stream_slice_step, expected_error_message",
    [
        ("2023", "Stream slice step Interval should be provided in ISO 8601 format."),
        ("PT0.1S", "Stream slice step Interval is too small. It should be no less than 1 second."),
        ("PT1D", "Unable to parse string"),
        ("P221S", "Unable to parse string"),
    ],
    ids=[
        "incorrect_ISO_8601_format",
        "too_small_duration_provided",
        "incorrect_date_format",
        "incorrect_time_format",
    ],
)
def test_stream_slice_step_validation(stream_slice_step: str, expected_error_message):
    _ANY_CONFIG.update({"stream_slice_step": stream_slice_step})
    source = SourceSalesforce(_ANY_CATALOG, _ANY_CONFIG, _ANY_STATE)
    logger = logging.getLogger("airbyte")
    with pytest.raises(AirbyteTracedException) as e:
        source.check_connection(logger, _ANY_CONFIG)
    assert expected_error_message in e.value.message


@pytest.mark.parametrize(
    "login_status_code, login_json_resp, expected_error_msg, is_config_error",
    [
        (
            400,
            {"error": "invalid_grant", "error_description": "expired access/refresh token"},
            AUTHENTICATION_ERROR_MESSAGE_MAPPING.get("expired access/refresh token"),
            True,
        ),
        (
            400,
            {"error": "invalid_grant", "error_description": "Authentication failure."},
            'An error occurred: {"error": "invalid_grant", "error_description": "Authentication failure."}',
            False,
        ),
        (
            401,
            {"error": "Unauthorized", "error_description": "Unautorized"},
            'An error occurred: {"error": "Unauthorized", "error_description": "Unautorized"}',
            False,
        ),
    ],
)
def test_login_authentication_error_handler(
    stream_config, requests_mock, login_status_code, login_json_resp, expected_error_msg, is_config_error
):
    source = SourceSalesforce(_ANY_CATALOG, _ANY_CONFIG, _ANY_STATE)
    logger = logging.getLogger("airbyte")
    requests_mock.register_uri(
        "POST", "https://login.salesforce.com/services/oauth2/token", json=login_json_resp, status_code=login_status_code
    )

    if is_config_error:
        with pytest.raises(AirbyteTracedException) as err:
            source.check_connection(logger, stream_config)
        assert err.value.message == expected_error_msg
    else:
        result, msg = source.check_connection(logger, stream_config)
        assert result is False
        assert msg == expected_error_msg


def test_bulk_sync_creation_failed(stream_config, stream_api):
    stream: BulkIncrementalSalesforceStream = generate_stream("Account", stream_config, stream_api)
    with requests_mock.Mocker() as m:
        m.register_uri("POST", stream.path(), status_code=400, json=[{"message": "test_error"}])
        with pytest.raises(HTTPError) as err:
            stream_slices = next(iter(stream.stream_slices(sync_mode=SyncMode.incremental)))
            next(stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slices))
        assert err.value.response.json()[0]["message"] == "test_error"


def test_bulk_stream_fallback_to_rest(mocker, requests_mock, stream_config, stream_api):
    """
    Here we mock BULK API with response returning error, saying BULK is not supported for this kind of entity.
    On the other hand, we mock REST API for this same entity with a successful response.
    After having instantiated a BulkStream, sync should succeed in case it falls back to REST API. Otherwise it would throw an error.
    """
    stream = generate_stream("CustomEntity", stream_config, stream_api)
    # mock a BULK API
    requests_mock.register_uri(
        "POST",
        "https://fase-account.salesforce.com/services/data/v57.0/jobs/query",
        status_code=400,
        json=[{"errorCode": "INVALIDENTITY", "message": "CustomEntity is not supported by the Bulk API"}],
    )
    rest_stream_records = [
        {"id": 1, "name": "custom entity", "created": "2010-11-11"},
        {"id": 11, "name": "custom entity", "created": "2020-01-02"},
    ]
    # mock REST API
    mocker.patch("source_salesforce.source.RestSalesforceStream.read_records", lambda *args, **kwargs: iter(rest_stream_records))
    assert type(stream) is BulkIncrementalSalesforceStream
    stream_slices = next(iter(stream.stream_slices(sync_mode=SyncMode.incremental)))
    assert list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slices)) == rest_stream_records


def test_stream_unsupported_by_bulk(stream_config, stream_api):
    """
    Stream `AcceptedEventRelation` is not supported by BULK API, so that REST API stream will be used for it.
    """
    stream_name = "AcceptedEventRelation"
    stream = generate_stream(stream_name, stream_config, stream_api)
    assert not isinstance(stream, BulkSalesforceStream)


def test_stream_contains_unsupported_properties_by_bulk(stream_config, stream_api_v2):
    """
    Stream `Account` contains compound field such as BillingAddress, which is not supported by BULK API (csv),
    in that case REST API stream will be used for it.
    """
    stream_name = "Account"
    stream = generate_stream(stream_name, stream_config, stream_api_v2)
    assert not isinstance(stream, BulkSalesforceStream)


def _prepare_mock(m, stream):
    job_id = "fake_job_1"
    m.register_uri("POST", stream.path(), json={"id": job_id})
    m.register_uri("DELETE", stream.path() + f"/{job_id}")
    m.register_uri("GET", stream.path() + f"/{job_id}/results", text="Field1,LastModifiedDate,ID\ntest,2021-11-16,1")
    m.register_uri("PATCH", stream.path() + f"/{job_id}", text="")
    return job_id


def _get_result_id(stream):
    stream_slices = next(iter(stream.stream_slices(sync_mode=SyncMode.incremental)))
    return int(list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slices))[0]["ID"])


def test_bulk_sync_successful_long_response(stream_config, stream_api):
    stream: BulkIncrementalSalesforceStream = generate_stream("Account", stream_config, stream_api)
    with requests_mock.Mocker() as m:
        job_id = _prepare_mock(m, stream)
        m.register_uri(
            "GET",
            stream.path() + f"/{job_id}",
            [
                {"json": {"state": "UploadComplete", "id": job_id}},
                {"json": {"state": "InProgress", "id": job_id}},
                {"json": {"state": "JobComplete", "id": job_id}},
            ],
        )
        assert _get_result_id(stream) == 1


# maximum timeout is wait_timeout * max_retry_attempt
# this test tries to check a job state 17 times with +-1second for very one
@pytest.mark.timeout(17)
def test_bulk_sync_successful_retry(stream_config, stream_api):
    stream: BulkIncrementalSalesforceStream = generate_stream("Account", stream_config, stream_api)
    stream.DEFAULT_WAIT_TIMEOUT_SECONDS = 6  # maximum wait timeout will be 6 seconds

    with requests_mock.Mocker() as m:
        job_id = _prepare_mock(m, stream)
        # 2 failed attempts, 3rd one should be successful
        states = [{"json": {"state": "InProgress", "id": job_id}}] * 17
        states.append({"json": {"state": "JobComplete", "id": job_id}})
        # raise Exception(states)
        m.register_uri("GET", stream.path() + f"/{job_id}", states)
        assert _get_result_id(stream) == 1


@pytest.mark.timeout(30)
def test_bulk_sync_failed_retry(stream_config, stream_api):
    stream: BulkIncrementalSalesforceStream = generate_stream("Account", stream_config, stream_api)
    stream.DEFAULT_WAIT_TIMEOUT_SECONDS = 6  # maximum wait timeout will be 6 seconds
    with requests_mock.Mocker() as m:
        job_id = _prepare_mock(m, stream)
        m.register_uri("GET", stream.path() + f"/{job_id}", json={"state": "InProgress", "id": job_id})
        with pytest.raises(Exception) as err:
            stream_slices = next(iter(stream.stream_slices(sync_mode=SyncMode.incremental)))
            next(stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slices))
        assert "stream using BULK API was failed" in str(err.value)


@pytest.mark.parametrize(
    "start_date_provided,stream_name,expected_start_date",
    [
        (True, "Account", "2010-01-18T21:18:20Z"),
        (True, "ActiveFeatureLicenseMetric", "2010-01-18T21:18:20Z"),
    ],
)
def test_stream_start_date(
    start_date_provided,
    stream_name,
    expected_start_date,
    stream_config,
    stream_api,
    stream_config_without_start_date,
):
    if start_date_provided:
        stream = generate_stream(stream_name, stream_config, stream_api)
        assert stream.start_date == expected_start_date
    else:
        stream = generate_stream(stream_name, stream_config_without_start_date, stream_api)
        assert datetime.strptime(stream.start_date, "%Y-%m-%dT%H:%M:%SZ").year == datetime.now().year - 2


def test_stream_start_date_should_be_converted_to_datetime_format(stream_config_date_format, stream_api):
    stream: IncrementalRestSalesforceStream = generate_stream("ActiveFeatureLicenseMetric", stream_config_date_format, stream_api)
    assert stream.start_date == "2010-01-18T00:00:00Z"


def test_stream_start_datetime_format_should_not_changed(stream_config, stream_api):
    stream: IncrementalRestSalesforceStream = generate_stream("ActiveFeatureLicenseMetric", stream_config, stream_api)
    assert stream.start_date == "2010-01-18T21:18:20Z"


def test_download_data_filter_null_bytes(stream_config, stream_api):
    job_full_url_results: str = "https://fase-account.salesforce.com/services/data/v57.0/jobs/query/7504W00000bkgnpQAA/results"
    stream: BulkIncrementalSalesforceStream = generate_stream("Account", stream_config, stream_api)

    with requests_mock.Mocker() as m:
        m.register_uri("GET", job_full_url_results, content=b"\x00")
        tmp_file, response_encoding, _ = stream.download_data(url=job_full_url_results)
        res = list(stream.read_with_chunks(tmp_file, response_encoding))
        assert res == []

        m.register_uri("GET", job_full_url_results, content=b'"Id","IsDeleted"\n\x00"0014W000027f6UwQAI","false"\n\x00\x00')
        tmp_file, response_encoding, _ = stream.download_data(url=job_full_url_results)
        res = list(stream.read_with_chunks(tmp_file, response_encoding))
        assert res == [{"Id": "0014W000027f6UwQAI", "IsDeleted": "false"}]


def test_read_with_chunks_should_return_only_object_data_type(stream_config, stream_api):
    job_full_url_results: str = "https://fase-account.salesforce.com/services/data/v57.0/jobs/query/7504W00000bkgnpQAA/results"
    stream: BulkIncrementalSalesforceStream = generate_stream("Account", stream_config, stream_api)

    with requests_mock.Mocker() as m:
        m.register_uri("GET", job_full_url_results, content=b'"IsDeleted","Age"\n"false",24\n')
        tmp_file, response_encoding, _ = stream.download_data(url=job_full_url_results)
        res = list(stream.read_with_chunks(tmp_file, response_encoding))
        assert res == [{"IsDeleted": "false", "Age": "24"}]


def test_read_with_chunks_should_return_a_string_when_a_string_with_only_digits_is_provided(stream_config, stream_api):
    job_full_url_results: str = "https://fase-account.salesforce.com/services/data/v57.0/jobs/query/7504W00000bkgnpQAA/results"
    stream: BulkIncrementalSalesforceStream = generate_stream("Account", stream_config, stream_api)

    with requests_mock.Mocker() as m:
        m.register_uri("GET", job_full_url_results, content=b'"ZipCode"\n"01234"\n')
        tmp_file, response_encoding, _ = stream.download_data(url=job_full_url_results)
        res = list(stream.read_with_chunks(tmp_file, response_encoding))
        assert res == [{"ZipCode": "01234"}]


def test_read_with_chunks_should_return_null_value_when_no_data_is_provided(stream_config, stream_api):
    job_full_url_results: str = "https://fase-account.salesforce.com/services/data/v57.0/jobs/query/7504W00000bkgnpQAA/results"
    stream: BulkIncrementalSalesforceStream = generate_stream("Account", stream_config, stream_api)

    with requests_mock.Mocker() as m:
        m.register_uri("GET", job_full_url_results, content=b'"IsDeleted","Age","Name"\n"false",,"Airbyte"\n')
        tmp_file, response_encoding, _ = stream.download_data(url=job_full_url_results)
        res = list(stream.read_with_chunks(tmp_file, response_encoding))
        assert res == [{"IsDeleted": "false", "Age": None, "Name": "Airbyte"}]


@pytest.mark.parametrize(
    "chunk_size, content_type_header, content, expected_result",
    encoding_symbols_parameters(),
    ids=[f"charset: {x[1]}, chunk_size: {x[0]}" for x in encoding_symbols_parameters()],
)
def test_encoding_symbols(stream_config, stream_api, chunk_size, content_type_header, content, expected_result):
    job_full_url_results: str = "https://fase-account.salesforce.com/services/data/v57.0/jobs/query/7504W00000bkgnpQAA/results"
    stream: BulkIncrementalSalesforceStream = generate_stream("Account", stream_config, stream_api)

    with requests_mock.Mocker() as m:
        m.register_uri("GET", job_full_url_results, headers=content_type_header, content=content)
        tmp_file, response_encoding, _ = stream.download_data(url=job_full_url_results)
        res = list(stream.read_with_chunks(tmp_file, response_encoding))
        assert res == expected_result


@pytest.mark.parametrize(
    "login_status_code, login_json_resp, discovery_status_code, discovery_resp_json, expected_error_msg",
    (
        (
            403,
            [{"errorCode": "REQUEST_LIMIT_EXCEEDED", "message": "TotalRequests Limit exceeded."}],
            200,
            {},
            "API Call limit is exceeded. Make sure that you have enough API allocation for your organization needs or retry later. For more information, see https://developer.salesforce.com/docs/atlas.en-us.salesforce_app_limits_cheatsheet.meta/salesforce_app_limits_cheatsheet/salesforce_app_limits_platform_api.htm"),
        (
            200,
            {"access_token": "access_token", "instance_url": "https://instance_url"},
            403,
            [{"errorCode": "FORBIDDEN", "message": "You do not have enough permissions"}],
            'An error occurred: [{"errorCode": "FORBIDDEN", "message": "You do not have enough permissions"}]',
        ),
    ),
)
def test_check_connection_rate_limit(
    stream_config, login_status_code, login_json_resp, discovery_status_code, discovery_resp_json, expected_error_msg
):
    source = SourceSalesforce(_ANY_CATALOG, _ANY_CONFIG, _ANY_STATE)
    logger = logging.getLogger("airbyte")

    with requests_mock.Mocker() as m:
        m.register_uri("POST", "https://login.salesforce.com/services/oauth2/token", json=login_json_resp, status_code=login_status_code)
        m.register_uri(
            "GET", "https://instance_url/services/data/v57.0/sobjects", json=discovery_resp_json, status_code=discovery_status_code
        )
        result, msg = source.check_connection(logger, stream_config)
        assert result is False
        assert msg == expected_error_msg


def configure_request_params_mock(stream_1, stream_2):
    stream_1.request_params = Mock()
    stream_1.request_params.return_value = {"q": "query"}

    stream_2.request_params = Mock()
    stream_2.request_params.return_value = {"q": "query"}


def test_pagination_rest(stream_config, stream_api):
    stream_name = "AcceptedEventRelation"
    stream: RestSalesforceStream = generate_stream(stream_name, stream_config, stream_api)
    stream.DEFAULT_WAIT_TIMEOUT_SECONDS = 6  # maximum wait timeout will be 6 seconds
    next_page_url = "/services/data/v57.0/query/012345"
    with requests_mock.Mocker() as m:
        resp_1 = {
            "done": False,
            "totalSize": 4,
            "nextRecordsUrl": next_page_url,
            "records": [
                {
                    "ID": 1,
                    "LastModifiedDate": "2021-11-15",
                },
                {
                    "ID": 2,
                    "LastModifiedDate": "2021-11-16",
                },
            ],
        }
        resp_2 = {
            "done": True,
            "totalSize": 4,
            "records": [
                {
                    "ID": 3,
                    "LastModifiedDate": "2021-11-17",
                },
                {
                    "ID": 4,
                    "LastModifiedDate": "2021-11-18",
                },
            ],
        }

        m.register_uri("GET", stream.path(), json=resp_1)
        m.register_uri("GET", next_page_url, json=resp_2)

        records = [record for record in stream.read_records(sync_mode=SyncMode.full_refresh)]
        assert len(records) == 4


def test_csv_reader_dialect_unix():
    stream: BulkSalesforceStream = BulkSalesforceStream(stream_name=None, sf_api=None, pk=None)
    url_results = "https://fake-account.salesforce.com/services/data/v57.0/jobs/query/7504W00000bkgnpQAA/results"

    data = [
        {"Id": "1", "Name": '"first_name" "last_name"'},
        {"Id": "2", "Name": "'" + 'first_name"\n' + "'" + 'last_name\n"'},
        {"Id": "3", "Name": "first_name last_name"},
    ]

    with io.StringIO("", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["Id", "Name"], dialect="unix")
        writer.writeheader()
        for line in data:
            writer.writerow(line)
        text = csvfile.getvalue()

    with requests_mock.Mocker() as m:
        m.register_uri("GET", url_results, text=text)
        tmp_file, response_encoding, _ = stream.download_data(url=url_results)
        result = [i for i in stream.read_with_chunks(tmp_file, response_encoding)]
        assert result == data


@patch("source_salesforce.source.BulkSalesforceStream._non_retryable_send_http_request")
def test_given_retryable_error_when_download_data_then_retry(send_http_request_patch):
    send_http_request_patch.return_value.iter_content.side_effect = [HTTPError(), _A_CHUNKED_RESPONSE]
    BulkSalesforceStream(stream_name=_A_STREAM_NAME, sf_api=Mock(), pk=_A_PK).download_data(url="any url")
    assert send_http_request_patch.call_count == 2


@patch("source_salesforce.source.BulkSalesforceStream._non_retryable_send_http_request")
def test_given_first_download_fail_when_download_data_then_retry_job_only_once(send_http_request_patch):
    sf_api = Mock()
    sf_api.generate_schema.return_value = JobInfoResponseBuilder().with_state("JobComplete").get_response()
    sf_api.instance_url = "http://test_given_first_download_fail_when_download_data_then_retry_job.com"
    job_creation_return_values = [_A_JSON_RESPONSE, _A_SUCCESSFUL_JOB_CREATION_RESPONSE]
    send_http_request_patch.return_value.json.side_effect = job_creation_return_values * 2
    send_http_request_patch.return_value.iter_content.side_effect = HTTPError()

    with pytest.raises(Exception):
        list(BulkSalesforceStream(stream_name=_A_STREAM_NAME, sf_api=sf_api, pk=_A_PK).read_records(SyncMode.full_refresh))

    assert send_http_request_patch.call_count == (len(job_creation_return_values) + _NUMBER_OF_DOWNLOAD_TRIES) * 2


@patch("source_salesforce.source.BulkSalesforceStream._non_retryable_send_http_request")
def test_given_http_errors_when_create_stream_job_then_retry(send_http_request_patch):
    send_http_request_patch.return_value.json.side_effect = [HTTPError(), _A_JSON_RESPONSE]
    BulkSalesforceStream(stream_name=_A_STREAM_NAME, sf_api=Mock(), pk=_A_PK).create_stream_job(query="any query", url="any url")
    assert send_http_request_patch.call_count == 2


@patch("source_salesforce.source.BulkSalesforceStream._non_retryable_send_http_request")
def test_given_fail_with_http_errors_when_create_stream_job_then_handle_error(send_http_request_patch):
    mocked_response = Mock()
    mocked_response.status_code = 666
    send_http_request_patch.return_value.json.side_effect = HTTPError(response=mocked_response)

    with pytest.raises(HTTPError):
        BulkSalesforceStream(stream_name=_A_STREAM_NAME, sf_api=Mock(), pk=_A_PK).create_stream_job(query="any query", url="any url")


@patch("source_salesforce.source.BulkSalesforceStream._non_retryable_send_http_request")
def test_given_retryable_error_that_are_not_http_errors_when_create_stream_job_then_retry(send_http_request_patch):
    send_http_request_patch.return_value.json.side_effect = [ChunkedEncodingError(), _A_JSON_RESPONSE]
    BulkSalesforceStream(stream_name=_A_STREAM_NAME, sf_api=Mock(), pk=_A_PK).create_stream_job(query="any query", url="any url")
    assert send_http_request_patch.call_count == 2


@pytest.mark.parametrize(
    "stream_names,catalog_stream_names,",
    (
        (
            ["stream_1", "stream_2", "Describe"],
            None,
        ),
        (
            ["stream_1", "stream_2"],
            ["stream_1", "stream_2", "Describe"],
        ),
        (
            ["stream_1", "stream_2", "stream_3", "Describe"],
            ["stream_1", "Describe"],
        ),
    ),
)
def test_forwarding_sobject_options(stream_config, stream_names, catalog_stream_names) -> None:
    sobjects_matcher = re.compile("/sobjects$")
    token_matcher = re.compile("/token$")
    describe_matcher = re.compile("/describe$")
    catalog = None
    if catalog_stream_names:
        catalog = ConfiguredAirbyteCatalog(
            streams=[
                ConfiguredAirbyteStream(
                    stream=AirbyteStream(
                        name=catalog_stream_name, supported_sync_modes=[SyncMode.full_refresh], json_schema={"type": "object"}
                    ),
                    sync_mode=SyncMode.full_refresh,
                    destination_sync_mode=DestinationSyncMode.overwrite,
                )
                for catalog_stream_name in catalog_stream_names
            ]
        )
    with requests_mock.Mocker() as m:
        m.register_uri("POST", token_matcher, json={"instance_url": "https://fake-url.com", "access_token": "fake-token"})
        m.register_uri(
            "GET",
            describe_matcher,
            json={
                "fields": [
                    {
                        "name": "field",
                        "type": "string",
                    }
                ]
            },
        )
        m.register_uri(
            "GET",
            sobjects_matcher,
            json={
                "sobjects": [
                    {
                        "name": stream_name,
                        "flag1": True,
                        "queryable": True,
                    }
                    for stream_name in stream_names
                    if stream_name != "Describe"
                ],
            },
        )
        source = SourceSalesforce(_ANY_CATALOG, _ANY_CONFIG, _ANY_STATE)
        source.catalog = catalog
        streams = source.streams(config=stream_config)
    expected_names = catalog_stream_names if catalog else stream_names
    assert not set(expected_names).symmetric_difference(set(stream.name for stream in streams)), "doesn't match excepted streams"

    for stream in streams:
        if stream.name != "Describe":
            if isinstance(stream, StreamFacade):
                assert stream._legacy_stream.sobject_options == {"flag1": True, "queryable": True}
            else:
                assert stream.sobject_options == {"flag1": True, "queryable": True}
    return


@pytest.mark.parametrize(
    "stream_names,catalog_stream_names,",
    (
        (
            ["stream_1", "stream_2"],
            ["stream_1", "stream_2", "Describe"],
        ),
        (
            ["stream_1", "stream_2", "stream_3", "Describe"],
            ["stream_1", "Describe"],
        ),
    ),
)
def test_full_refresh_streams_are_concurrent(stream_config, stream_names, catalog_stream_names) -> None:
    for stream in _get_streams(stream_config, stream_names, catalog_stream_names, SyncMode.full_refresh):
        assert isinstance(stream, StreamFacade)


def _get_streams(stream_config, stream_names, catalog_stream_names, sync_type) -> List[Stream]:
    sobjects_matcher = re.compile("/sobjects$")
    token_matcher = re.compile("/token$")
    describe_matcher = re.compile("/describe$")
    catalog = None
    if catalog_stream_names:
        catalog = ConfiguredAirbyteCatalog(
            streams=[
                ConfiguredAirbyteStream(
                    stream=AirbyteStream(name=catalog_stream_name, supported_sync_modes=[sync_type], json_schema={"type": "object"}),
                    sync_mode=sync_type,
                    destination_sync_mode=DestinationSyncMode.overwrite,
                )
                for catalog_stream_name in catalog_stream_names
            ]
        )
    with requests_mock.Mocker() as m:
        m.register_uri("POST", token_matcher, json={"instance_url": "https://fake-url.com", "access_token": "fake-token"})
        m.register_uri(
            "GET",
            describe_matcher,
            json={
                "fields": [
                    {
                        "name": "field",
                        "type": "string",
                    }
                ]
            },
        )
        m.register_uri(
            "GET",
            sobjects_matcher,
            json={
                "sobjects": [
                    {
                        "name": stream_name,
                        "flag1": True,
                        "queryable": True,
                    }
                    for stream_name in stream_names
                    if stream_name != "Describe"
                ],
            },
        )
        source = SourceSalesforce(_ANY_CATALOG, _ANY_CONFIG, _ANY_STATE)
        source.catalog = catalog
        return source.streams(config=stream_config)


def test_csv_field_size_limit():
    DEFAULT_CSV_FIELD_SIZE_LIMIT = 1024 * 128

    field_size = 1024 * 1024
    text = '"Id","Name"\n"1","' + field_size * "a" + '"\n'

    csv.field_size_limit(DEFAULT_CSV_FIELD_SIZE_LIMIT)
    reader = csv.reader(io.StringIO(text))
    with pytest.raises(csv.Error):
        for _ in reader:
            pass

    csv.field_size_limit(CSV_FIELD_SIZE_LIMIT)
    reader = csv.reader(io.StringIO(text))
    for _ in reader:
        pass


def test_convert_to_standard_instance(stream_config, stream_api):
    bulk_stream = generate_stream("Account", stream_config, stream_api)
    rest_stream = bulk_stream.get_standard_instance()
    assert isinstance(rest_stream, IncrementalRestSalesforceStream)


def test_rest_stream_init_with_too_many_properties(stream_config, stream_api_v2_too_many_properties):
    with pytest.raises(AssertionError):
        # v2 means the stream is going to be a REST stream.
        # A missing primary key is not allowed
        generate_stream("Account", stream_config, stream_api_v2_too_many_properties)


def test_too_many_properties(stream_config, stream_api_v2_pk_too_many_properties, requests_mock):
    stream = generate_stream("Account", stream_config, stream_api_v2_pk_too_many_properties)
    chunks = list(stream.chunk_properties())
    for chunk in chunks:
        assert stream.primary_key in chunk
    chunks_len = len(chunks)
    assert stream.too_many_properties
    assert stream.primary_key
    assert type(stream) == RestSalesforceStream
    url = next_page_url = "https://fase-account.salesforce.com/services/data/v57.0/queryAll"
    requests_mock.get(
        url,
        [
            {
                "json": {
                    "records": [
                        {"Id": 1, "propertyA": "A"},
                        {"Id": 2, "propertyA": "A"},
                        {"Id": 3, "propertyA": "A"},
                        {"Id": 4, "propertyA": "A"},
                    ]
                }
            },
            {"json": {"nextRecordsUrl": next_page_url, "records": [{"Id": 1, "propertyB": "B"}, {"Id": 2, "propertyB": "B"}]}},
            # 2 for 2 chunks above
            *[{"json": {"records": [{"Id": 1}, {"Id": 2}], "nextRecordsUrl": next_page_url}} for _ in range(chunks_len - 2)],
            {"json": {"records": [{"Id": 3, "propertyB": "B"}, {"Id": 4, "propertyB": "B"}]}},
            # 2 for 1 chunk above and 1 chunk had no next page
            *[{"json": {"records": [{"Id": 3}, {"Id": 4}]}} for _ in range(chunks_len - 2)],
        ],
    )
    records = list(stream.read_records(sync_mode=SyncMode.full_refresh))
    assert records == [
        {"Id": 1, "propertyA": "A", "propertyB": "B"},
        {"Id": 2, "propertyA": "A", "propertyB": "B"},
        {"Id": 3, "propertyA": "A", "propertyB": "B"},
        {"Id": 4, "propertyA": "A", "propertyB": "B"},
    ]
    for call in requests_mock.request_history:
        assert len(call.url) < Salesforce.REQUEST_SIZE_LIMITS


def test_stream_with_no_records_in_response(stream_config, stream_api_v2_pk_too_many_properties, requests_mock):
    stream = generate_stream("Account", stream_config, stream_api_v2_pk_too_many_properties)
    chunks = list(stream.chunk_properties())
    for chunk in chunks:
        assert stream.primary_key in chunk
    assert stream.too_many_properties
    assert stream.primary_key
    assert type(stream) == RestSalesforceStream
    url = "https://fase-account.salesforce.com/services/data/v57.0/queryAll"
    requests_mock.get(
        url,
        [
            {"json": {"records": []}},
        ],
    )
    records = list(stream.read_records(sync_mode=SyncMode.full_refresh))
    assert records == []


@pytest.mark.parametrize(
    "status_code,response_json,log_message",
    [
        (
            400,
            [{"errorCode": "INVALIDENTITY", "message": "Account is not supported by the Bulk API"}],
            "Account is not supported by the Bulk API",
        ),
        (403, [{"errorCode": "REQUEST_LIMIT_EXCEEDED", "message": "API limit reached"}], "API limit reached"),
        (400, [{"errorCode": "API_ERROR", "message": "API does not support query"}], "The stream 'Account' is not queryable,"),
        (
            400,
            [{"errorCode": "LIMIT_EXCEEDED", "message": "Max bulk v2 query jobs (10000) per 24 hrs has been reached (10021)"}],
            "Your API key for Salesforce has reached its limit for the 24-hour period. We will resume replication once the limit has elapsed.",
        ),
    ],
)
def test_bulk_stream_error_in_logs_on_create_job(requests_mock, stream_config, stream_api, status_code, response_json, log_message, caplog):
    """ """
    stream = generate_stream("Account", stream_config, stream_api)
    url = f"{stream.sf_api.instance_url}/services/data/{stream.sf_api.version}/jobs/query"
    requests_mock.register_uri(
        "POST",
        url,
        status_code=status_code,
        json=response_json,
    )
    query = "Select Id, Subject from Account"
    with caplog.at_level(logging.ERROR):
        assert stream.create_stream_job(query, url) is None, "this stream should be skipped"

    # check logs
    assert log_message in caplog.records[-1].message


@pytest.mark.parametrize(
    "status_code,response_json,error_message",
    [
        (
            400,
            [
                {
                    "errorCode": "TXN_SECURITY_METERING_ERROR",
                    "message": "We can't complete the action because enabled transaction security policies took too long to complete.",
                }
            ],
            'A transient authentication error occurred. To prevent future syncs from failing, assign the "Exempt from Transaction Security" user permission to the authenticated user.',
        ),
    ],
)
def test_bulk_stream_error_on_wait_for_job(requests_mock, stream_config, stream_api, status_code, response_json, error_message):

    stream = generate_stream("Account", stream_config, stream_api)
    url = f"{stream.sf_api.instance_url}/services/data/{stream.sf_api.version}/jobs/query/queryJobId"
    requests_mock.register_uri(
        "GET",
        url,
        status_code=status_code,
        json=response_json,
    )
    with pytest.raises(AirbyteTracedException) as e:
        stream.wait_for_job(url=url)
    assert e.value.message == error_message


@freezegun.freeze_time("2023-01-01")
@pytest.mark.parametrize(
    "lookback, stream_slice_step, expected_len_stream_slices, expect_error",
    [(0, "P30D", 158, False)],
    ids=["lookback-is-0-step-30D"],
)
def test_bulk_stream_slices(
    stream_config_date_format, stream_api, lookback, expect_error, stream_slice_step: str, expected_len_stream_slices: int
):
    stream_config_date_format["stream_slice_step"] = stream_slice_step
    with patch("source_salesforce.source.LOOKBACK_SECONDS", lookback):
        stream: BulkIncrementalSalesforceStream = generate_stream("FakeBulkStream", stream_config_date_format, stream_api)
        if expect_error:
            with pytest.raises(AssertionError):
                list(stream.stream_slices(sync_mode=SyncMode.full_refresh))
        else:
            stream_slices = list(stream.stream_slices(sync_mode=SyncMode.full_refresh))

            expected_slices = []
            today = pendulum.today(tz="UTC")
            start_date = pendulum.parse(stream.start_date, tz="UTC") - timedelta(seconds=lookback)
            while start_date < today:
                end_date = start_date + stream.stream_slice_step
                expected_slices.append(
                    {
                        "start_date": start_date.isoformat(timespec="milliseconds"),
                        "end_date": min(today, end_date).isoformat(timespec="milliseconds"),
                    }
                )
                start_date += stream.stream_slice_step
            assert expected_slices == stream_slices
            assert len(stream_slices) == expected_len_stream_slices


@freezegun.freeze_time("2023-04-01")
def test_bulk_stream_request_params_states(stream_config_date_format, stream_api, bulk_catalog, requests_mock):
    """Check that request params ignore records cursor and use start date from slice ONLY"""
    stream_config_date_format.update({"start_date": "2023-01-01"})
    state = StateBuilder().with_stream_state("Account", {"LastModifiedDate": "2023-01-01T10:20:10.000Z"}).build()

    source = SourceSalesforce(CatalogBuilder().with_stream("Account", SyncMode.full_refresh).build(), _ANY_CONFIG, _ANY_STATE)
    source.streams = Mock()
    source.streams.return_value = [generate_stream("Account", stream_config_date_format, stream_api, state=state, legacy=False)]

    # using legacy state to configure HTTP requests
    stream: BulkIncrementalSalesforceStream = generate_stream("Account", stream_config_date_format, stream_api, state=state, legacy=True)

    job_id_1 = "fake_job_1"
    requests_mock.register_uri("GET", stream.path() + f"/{job_id_1}", [{"json": JobInfoResponseBuilder().with_id(job_id_1).with_state("JobComplete").get_response()}])
    requests_mock.register_uri("DELETE", stream.path() + f"/{job_id_1}")
    requests_mock.register_uri("GET", stream.path() + f"/{job_id_1}/results", text="Field1,LastModifiedDate,ID\ntest,2023-01-15,1")
    requests_mock.register_uri("PATCH", stream.path() + f"/{job_id_1}")

    job_id_2 = "fake_job_2"
    requests_mock.register_uri("GET", stream.path() + f"/{job_id_2}", [{"json": JobInfoResponseBuilder().with_id(job_id_2).with_state("JobComplete").get_response()}])
    requests_mock.register_uri("DELETE", stream.path() + f"/{job_id_2}")
    requests_mock.register_uri(
        "GET", stream.path() + f"/{job_id_2}/results", text="Field1,LastModifiedDate,ID\ntest,2023-04-01,2\ntest,2023-02-20,22"
    )
    requests_mock.register_uri("PATCH", stream.path() + f"/{job_id_2}")

    job_id_3 = "fake_job_3"
    queries_history = requests_mock.register_uri(
        "POST", stream.path(), [{"json": {"id": job_id_1}}, {"json": {"id": job_id_2}}, {"json": {"id": job_id_3}}]
    )
    requests_mock.register_uri("GET", stream.path() + f"/{job_id_3}", [{"json": JobInfoResponseBuilder().with_id(job_id_3).with_state("JobComplete").get_response()}])
    requests_mock.register_uri("DELETE", stream.path() + f"/{job_id_3}")
    requests_mock.register_uri("GET", stream.path() + f"/{job_id_3}/results", text="Field1,LastModifiedDate,ID\ntest,2023-04-01,3")
    requests_mock.register_uri("PATCH", stream.path() + f"/{job_id_3}")

    logger = logging.getLogger("airbyte")
    bulk_catalog.streams.pop(1)

    result = [i for i in source.read(logger=logger, config=stream_config_date_format, catalog=bulk_catalog, state=state)]

    # assert request params: has requests might not be performed in a specific order because of concurrent CDK, we match on any request
    all_requests = {request.text for request in queries_history.request_history}
    assert any([
        "LastModifiedDate >= 2023-01-01T10:10:10.000+00:00 AND LastModifiedDate < 2023-01-31T10:10:10.000+00:00"
        in request for request in all_requests
    ])
    assert any([
        "LastModifiedDate >= 2023-01-31T10:10:10.000+00:00 AND LastModifiedDate < 2023-03-02T10:10:10.000+00:00"
        in request for request in all_requests
    ])
    assert any([
        "LastModifiedDate >= 2023-03-02T10:10:10.000+00:00 AND LastModifiedDate < 2023-04-01T00:00:00.000+00:00"
        in request for request in all_requests
    ])

    # as the execution is concurrent, we can only assert the last state message here
    last_actual_state = [item.state.stream.stream_state.dict() for item in result if item.type == Type.STATE][-1]
    last_expected_state = {"slices": [{"start": "2023-01-01T00:00:00.000Z", "end": "2023-04-01T00:00:00.000Z"}], "state_type": "date-range"}
    assert last_actual_state == last_expected_state


def test_request_params_incremental(stream_config_date_format, stream_api):
    stream = generate_stream("ContentDocument", stream_config_date_format, stream_api)
    params = stream.request_params(stream_state={}, stream_slice={"start_date": "2020", "end_date": "2021"})

    assert params == {"q": "SELECT LastModifiedDate, Id FROM ContentDocument WHERE LastModifiedDate >= 2020 AND LastModifiedDate < 2021"}


def test_request_params_substream(stream_config_date_format, stream_api):
    stream = generate_stream("ContentDocumentLink", stream_config_date_format, stream_api)
    params = stream.request_params(stream_state={}, stream_slice={"parents": [{"Id": 1}, {"Id": 2}]})

    assert params == {"q": "SELECT LastModifiedDate, Id FROM ContentDocumentLink WHERE ContentDocumentId IN ('1','2')"}


@freezegun.freeze_time("2023-03-20")
def test_stream_slices_for_substream(stream_config, stream_api, requests_mock):
    """Test BulkSalesforceSubStream for ContentDocumentLink (+ parent ContentDocument)
    ContentDocument return 1 record for each slice request.
    Given start/end date leads to 3 date slice for ContentDocument, thus 3 total records
    ContentDocumentLink
    It means that ContentDocumentLink should have 2 slices, with 2 and 1 records in each
    """
    stream_config["start_date"] = "2023-01-01"
    stream: BulkSalesforceSubStream = generate_stream("ContentDocumentLink", stream_config, stream_api)
    stream.SLICE_BATCH_SIZE = 2  # each ContentDocumentLink should contain 2 records from parent ContentDocument stream

    job_id = "fake_job"
    requests_mock.register_uri("POST", stream.path(), json={"id": job_id})
    requests_mock.register_uri("GET", stream.path() + f"/{job_id}", json=JobInfoResponseBuilder().with_id(job_id).with_state("JobComplete").get_response())
    requests_mock.register_uri(
        "GET",
        stream.path() + f"/{job_id}/results",
        [{"text": "Field1,LastModifiedDate,ID\ntest,2021-11-16,123", "headers": {"Sforce-Locator": "null"}}],
    )
    requests_mock.register_uri("DELETE", stream.path() + f"/{job_id}")

    stream_slices = list(stream.stream_slices(sync_mode=SyncMode.full_refresh))
    assert stream_slices == [
        {
            "parents": [
                {"Field1": "test", "ID": "123", "LastModifiedDate": "2021-11-16"},
                {"Field1": "test", "ID": "123", "LastModifiedDate": "2021-11-16"},
            ]
        },
        {"parents": [{"Field1": "test", "ID": "123", "LastModifiedDate": "2021-11-16"}]},
    ]
