#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import csv
import io
import logging
import re
from datetime import datetime, timedelta
from typing import List
from unittest.mock import Mock

import freezegun
import pytest
import requests_mock
from config_builder import ConfigBuilder
from conftest import generate_stream
from salesforce_job_response_builder import JobInfoResponseBuilder
from source_salesforce.api import API_VERSION, Salesforce
from source_salesforce.source import SourceSalesforce
from source_salesforce.streams import (
    CSV_FIELD_SIZE_LIMIT,
    BulkIncrementalSalesforceStream,
    BulkSalesforceStream,
    BulkSalesforceSubStream,
    IncrementalRestSalesforceStream,
    RestSalesforceStream,
)

from airbyte_cdk.models import (
    AirbyteStateBlob,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteCatalogSerializer,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
    Type,
)
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.concurrent.adapters import StreamFacade
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_cdk.utils import AirbyteTracedException


_A_CHUNKED_RESPONSE = [b"first chunk", b"second chunk"]
_A_JSON_RESPONSE = {"id": "any id"}
_A_SUCCESSFUL_JOB_CREATION_RESPONSE = JobInfoResponseBuilder().with_state("JobComplete").get_response()
_A_PK = "a_pk"
_A_STREAM_NAME = "a_stream_name"

_NUMBER_OF_DOWNLOAD_TRIES = 5
_FIRST_CALL_FROM_JOB_CREATION = 1

_ANY_CATALOG = ConfiguredAirbyteCatalogSerializer.load({"streams": []})
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
    "login_status_code, login_json_resp, expected_error_msg",
    [
        (
            400,
            {"error": "invalid_grant", "error_description": "expired access/refresh token"},
            "The authentication to SalesForce has expired. Re-authenticate to restore access to SalesForce.",
        ),
        (
            400,
            {"error": "invalid_grant", "error_description": "Authentication failure."},
            'An error occurred: {"error": "invalid_grant", "error_description": "Authentication failure."}',
        ),
        (
            401,
            {"error": "Unauthorized", "error_description": "Unautorized"},
            'An error occurred: {"error": "Unauthorized", "error_description": "Unautorized"}',
        ),
    ],
)
def test_login_authentication_error_handler(stream_config, requests_mock, login_status_code, login_json_resp, expected_error_msg):
    source = SourceSalesforce(_ANY_CATALOG, _ANY_CONFIG, _ANY_STATE)
    logger = logging.getLogger("airbyte")
    requests_mock.register_uri(
        "POST", "https://login.salesforce.com/services/oauth2/token", json=login_json_resp, status_code=login_status_code
    )

    with pytest.raises(AirbyteTracedException) as err:
        source.check_connection(logger, stream_config)
    assert err.value.message == expected_error_msg


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
    m.register_uri("POST", _bulk_stream_path(), json={"id": job_id})
    m.register_uri("DELETE", _bulk_stream_path() + f"/{job_id}")
    m.register_uri("GET", _bulk_stream_path() + f"/{job_id}/results", text="Field1,LastModifiedDate,ID\ntest,2021-11-16,1")
    m.register_uri("PATCH", _bulk_stream_path() + f"/{job_id}", text="")
    return job_id


def _bulk_stream_path() -> str:
    return f"/services/data/{API_VERSION}/jobs/query"


def _get_result_id(stream):
    stream_slices = next(iter(stream.stream_slices(sync_mode=SyncMode.incremental)))
    return int(list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slices))[0]["ID"])


# maximum timeout is wait_timeout * max_retry_attempt
# this test tries to check a job state 17 times with +-1second for very one
@pytest.mark.timeout(17)
@freezegun.freeze_time("2023-01-07")
def test_bulk_sync_successful_retry(stream_config, stream_api):
    # setting the test to only have one slice
    stream_config = ConfigBuilder().start_date(datetime.fromisoformat("2023-01-01T00:00:00+00:00")).stream_slice_step("P100D").build()
    stream: BulkIncrementalSalesforceStream = generate_stream("Account", stream_config, stream_api)
    stream.DEFAULT_WAIT_TIMEOUT = timedelta(seconds=6)

    with requests_mock.Mocker() as m:
        job_id = _prepare_mock(m, stream)
        # 2 failed attempts, 3rd one should be successful
        states = [{"json": {"state": "InProgress", "id": job_id}}] * 17
        states.append({"json": {"state": "JobComplete", "id": job_id}})
        # raise Exception(states)
        m.register_uri("GET", _bulk_stream_path() + f"/{job_id}", states)
        assert _get_result_id(stream) == 1


@pytest.mark.timeout(30)
def test_bulk_sync_failed_retry(stream_config, stream_api):
    stream_config = ConfigBuilder().start_date(datetime.now() - timedelta(days=5)).stream_slice_step("P100D").build()
    stream: BulkIncrementalSalesforceStream = generate_stream("Account", stream_config, stream_api)
    stream.DEFAULT_WAIT_TIMEOUT = timedelta(seconds=1)
    with requests_mock.Mocker() as m:
        job_id = _prepare_mock(m, stream)
        m.register_uri("GET", _bulk_stream_path() + f"/{job_id}", json={"state": "InProgress", "id": job_id})
        with pytest.raises(Exception) as err:
            stream_slices = next(iter(stream.stream_slices(sync_mode=SyncMode.incremental)))
            next(stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slices))
        assert "At least one job could not be completed" in str(err.value.internal_message)


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


@pytest.mark.parametrize(
    "login_status_code, login_json_resp, discovery_status_code, discovery_resp_json, expected_error_msg",
    (
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
            "GET", f"https://instance_url/services/data/{API_VERSION}/sobjects", json=discovery_resp_json, status_code=discovery_status_code
        )
        with pytest.raises(AirbyteTracedException) as exception:
            source.check_connection(logger, stream_config)
        assert exception.value.message == expected_error_msg


def configure_request_params_mock(stream_1, stream_2):
    stream_1.request_params = Mock()
    stream_1.request_params.return_value = {"q": "query"}

    stream_2.request_params = Mock()
    stream_2.request_params.return_value = {"q": "query"}


def test_pagination_rest(stream_config, stream_api):
    stream_name = "AcceptedEventRelation"
    stream: RestSalesforceStream = generate_stream(stream_name, stream_config, stream_api)
    stream.DEFAULT_WAIT_TIMEOUT = timedelta(seconds=6)
    next_page_url = f"/services/data/{API_VERSION}/query/012345"
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


@pytest.fixture(name="mocked_response")
def _create_mocked_response():
    http_response = Mock()
    http_response.headers = {}
    return http_response


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
    url = next_page_url = f"https://fase-account.salesforce.com/services/data/{API_VERSION}/queryAll"
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
    url = f"https://fase-account.salesforce.com/services/data/{API_VERSION}/queryAll"
    requests_mock.get(
        url,
        [
            {"json": {"records": []}},
        ],
    )
    records = list(stream.read_records(sync_mode=SyncMode.full_refresh))
    assert records == []


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
    requests_mock.register_uri(
        "GET",
        _bulk_stream_path() + f"/{job_id_1}",
        [{"json": JobInfoResponseBuilder().with_id(job_id_1).with_state("JobComplete").get_response()}],
    )
    requests_mock.register_uri("DELETE", _bulk_stream_path() + f"/{job_id_1}")
    requests_mock.register_uri("GET", _bulk_stream_path() + f"/{job_id_1}/results", text="Field1,LastModifiedDate,ID\ntest,2023-01-15,1")
    requests_mock.register_uri("PATCH", _bulk_stream_path() + f"/{job_id_1}")

    job_id_2 = "fake_job_2"
    requests_mock.register_uri(
        "GET",
        _bulk_stream_path() + f"/{job_id_2}",
        [{"json": JobInfoResponseBuilder().with_id(job_id_2).with_state("JobComplete").get_response()}],
    )
    requests_mock.register_uri("DELETE", _bulk_stream_path() + f"/{job_id_2}")
    requests_mock.register_uri(
        "GET", _bulk_stream_path() + f"/{job_id_2}/results", text="Field1,LastModifiedDate,ID\ntest,2023-04-01,2\ntest,2023-02-20,22"
    )
    requests_mock.register_uri("PATCH", _bulk_stream_path() + f"/{job_id_2}")

    job_id_3 = "fake_job_3"
    queries_history = requests_mock.register_uri(
        "POST", _bulk_stream_path(), [{"json": {"id": job_id_1}}, {"json": {"id": job_id_2}}, {"json": {"id": job_id_3}}]
    )
    requests_mock.register_uri(
        "GET",
        _bulk_stream_path() + f"/{job_id_3}",
        [{"json": JobInfoResponseBuilder().with_id(job_id_3).with_state("JobComplete").get_response()}],
    )
    requests_mock.register_uri("DELETE", _bulk_stream_path() + f"/{job_id_3}")
    requests_mock.register_uri("GET", _bulk_stream_path() + f"/{job_id_3}/results", text="Field1,LastModifiedDate,ID\ntest,2023-04-01,3")
    requests_mock.register_uri("PATCH", _bulk_stream_path() + f"/{job_id_3}")

    logger = logging.getLogger("airbyte")
    bulk_catalog.streams.pop(1)

    result = [i for i in source.read(logger=logger, config=stream_config_date_format, catalog=bulk_catalog, state=state)]

    # assert request params: has requests might not be performed in a specific order because of concurrent CDK, we match on any request
    all_requests = {request.text for request in queries_history.request_history}
    assert any(
        [
            "LastModifiedDate >= 2023-01-01T10:10:10.000+00:00 AND LastModifiedDate < 2023-01-31T10:10:10.000+00:00" in request
            for request in all_requests
        ]
    )
    assert any(
        [
            "LastModifiedDate >= 2023-01-31T10:10:10.000+00:00 AND LastModifiedDate < 2023-03-02T10:10:10.000+00:00" in request
            for request in all_requests
        ]
    )
    assert any(
        [
            "LastModifiedDate >= 2023-03-02T10:10:10.000+00:00 AND LastModifiedDate < 2023-04-01T00:00:00.000+00:00" in request
            for request in all_requests
        ]
    )

    # as the execution is concurrent, we can only assert the last state message here
    last_actual_state = [item.state.stream.stream_state for item in result if item.type == Type.STATE][-1]
    last_expected_state = {"slices": [{"start": "2023-01-01T00:00:00.000Z", "end": "2023-04-01T00:00:00.000Z"}], "state_type": "date-range"}
    assert last_actual_state == AirbyteStateBlob(last_expected_state)


def test_request_params_incremental(stream_config_date_format, stream_api):
    stream = generate_stream("ContentDocument", stream_config_date_format, stream_api)
    params = stream.request_params(stream_state={}, stream_slice={"start_date": "2020", "end_date": "2021"})

    assert params == {"q": "SELECT LastModifiedDate, Id FROM ContentDocument WHERE LastModifiedDate >= 2020 AND LastModifiedDate < 2021"}


def test_request_params_substream(stream_config_date_format, stream_api):
    stream = generate_stream("ContentDocumentLink", stream_config_date_format, stream_api)
    params = stream.request_params(stream_state={}, stream_slice={"parents": [{"Id": 1}, {"Id": 2}]})

    assert params == {"q": "SELECT LastModifiedDate, Id FROM ContentDocumentLink WHERE ContentDocumentId IN ('1','2')"}
