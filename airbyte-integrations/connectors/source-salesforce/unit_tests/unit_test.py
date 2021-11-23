#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from unittest.mock import Mock

import pytest
import requests_mock
from airbyte_cdk.models import SyncMode
from requests.exceptions import HTTPError
from source_salesforce.api import Salesforce
from source_salesforce.source import SourceSalesforce
from source_salesforce.streams import BulkIncrementalSalesforceStream, BulkSalesforceStream, IncrementalSalesforceStream, SalesforceStream


@pytest.fixture(scope="module")
def stream_bulk_config():
    """Generates streams settings for BULK logic"""
    return {
        "client_id": "fake_client_id",
        "client_secret": "fake_client_secret",
        "refresh_token": "fake_refresh_token",
        "start_date": "2010-01-18T21:18:20Z",
        "is_sandbox": False,
        "wait_timeout": 15,
        "api_type": "BULK",
    }


@pytest.fixture(scope="module")
def stream_rest_config():
    """Generates streams settings for BULK logic"""
    return {
        "client_id": "fake_client_id",
        "client_secret": "fake_client_secret",
        "refresh_token": "fake_refresh_token",
        "start_date": "2010-01-18T21:18:20Z",
        "is_sandbox": False,
        "wait_timeout": 15,
        "api_type": "REST",
    }


def _stream_api(stream_config):
    sf_object = Salesforce(**stream_config)
    sf_object.login = Mock()
    sf_object.access_token = Mock()
    sf_object.instance_url = "https://fase-account.salesforce.com"
    sf_object.describe = Mock(return_value={"fields": [{"name": "LastModifiedDate", "type": "string"}]})
    return sf_object


@pytest.fixture(scope="module")
def stream_rest_api(stream_rest_config):
    return _stream_api(stream_rest_config)


@pytest.fixture(scope="module")
def stream_bulk_api(stream_bulk_config):
    return _stream_api(stream_bulk_config)


def _generate_stream(stream_name, stream_config, stream_api):
    return SourceSalesforce.generate_streams(stream_config, [stream_name], stream_api)[0]


@pytest.mark.parametrize(
    "api_type,stream_name,expected_cls",
    [
        ("BULK", "Account", BulkIncrementalSalesforceStream),
        ("BULK", "FormulaFunctionAllowedType", BulkSalesforceStream),
        ("REST", "ActiveFeatureLicenseMetric", IncrementalSalesforceStream),
        ("REST", "AppDefinition", SalesforceStream),
    ],
)
def test_stream_generator(api_type, stream_name, expected_cls, stream_bulk_config, stream_bulk_api, stream_rest_config, stream_rest_api):
    stream_config, stream_api = (stream_rest_config, stream_rest_api) if api_type == "REST" else (stream_bulk_config, stream_bulk_api)
    stream = _generate_stream(stream_name, stream_config, stream_api)
    assert stream.name == stream_name
    assert isinstance(stream, expected_cls)


def test_bulk_sync_creation_failed(stream_bulk_config, stream_bulk_api):
    stream: BulkIncrementalSalesforceStream = _generate_stream("Account", stream_bulk_config, stream_bulk_api)
    with requests_mock.Mocker() as m:
        m.register_uri("POST", stream.path(), status_code=400, json=[{"message": "test_error"}])
        with pytest.raises(HTTPError) as err:
            next(stream.read_records(sync_mode=SyncMode.full_refresh))
        assert err.value.response.json()[0]["message"] == "test_error"


@pytest.mark.parametrize("item_number", [0, 15, 2000, 2324, 193434])
def test_bulk_sync_pagination(item_number, stream_bulk_config, stream_bulk_api):
    stream: BulkIncrementalSalesforceStream = _generate_stream("Account", stream_bulk_config, stream_bulk_api)
    test_ids = [i for i in range(1, item_number)]
    pages = [test_ids[i : i + stream.page_size] for i in range(0, len(test_ids), stream.page_size)]
    if not pages:
        pages = [[]]
    with requests_mock.Mocker() as m:
        creation_responses = []

        for page in range(len(pages)):
            job_id = f"fake_job_{page}"
            creation_responses.append({"json": {"id": job_id}})
            m.register_uri("GET", stream.path() + f"/{job_id}", json={"state": "JobComplete"})
            resp = ["Field1,LastModifiedDate,ID"] + [f"test,2021-11-16,{i}" for i in pages[page]]
            m.register_uri("GET", stream.path() + f"/{job_id}/results", text="\n".join(resp))
            m.register_uri("DELETE", stream.path() + f"/{job_id}")
        m.register_uri("POST", stream.path(), creation_responses)

        loaded_ids = [int(record["ID"]) for record in stream.read_records(sync_mode=SyncMode.full_refresh)]
        assert not set(test_ids).symmetric_difference(set(loaded_ids))
        post_request_count = len([r for r in m.request_history if r.method == "POST"])
        assert post_request_count == len(pages)


def _prepare_mock(m, stream):
    job_id = "fake_job_1"
    m.register_uri("POST", stream.path(), json={"id": job_id})
    m.register_uri("DELETE", stream.path() + f"/{job_id}")
    m.register_uri("GET", stream.path() + f"/{job_id}/results", text="Field1,LastModifiedDate,ID\ntest,2021-11-16,1")
    m.register_uri("PATCH", stream.path() + f"/{job_id}", text="")
    return job_id


def _get_result_id(stream):
    return int(list(stream.read_records(sync_mode=SyncMode.full_refresh))[0]["ID"])


def test_bulk_sync_successful(stream_bulk_config, stream_bulk_api):
    stream: BulkIncrementalSalesforceStream = _generate_stream("Account", stream_bulk_config, stream_bulk_api)
    with requests_mock.Mocker() as m:
        job_id = _prepare_mock(m, stream)
        m.register_uri("GET", stream.path() + f"/{job_id}", [{"json": {"state": "JobComplete"}}])
        assert _get_result_id(stream) == 1


def test_bulk_sync_successful_long_response(stream_bulk_config, stream_bulk_api):
    stream: BulkIncrementalSalesforceStream = _generate_stream("Account", stream_bulk_config, stream_bulk_api)
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
def test_bulk_sync_successful_retry(stream_bulk_config, stream_bulk_api):
    stream: BulkIncrementalSalesforceStream = _generate_stream("Account", stream_bulk_config, stream_bulk_api)
    stream._wait_timeout = 0.1  # maximum wait timeout will be 6 seconds
    with requests_mock.Mocker() as m:
        job_id = _prepare_mock(m, stream)
        # 2 failed attempts, 3rd one should be successful
        states = [{"json": {"state": "InProgress", "id": job_id}}] * 17
        states.append({"json": {"state": "JobComplete", "id": job_id}})
        # raise Exception(states)
        m.register_uri("GET", stream.path() + f"/{job_id}", states)
        assert _get_result_id(stream) == 1


@pytest.mark.timeout(30)
def test_bulk_sync_failed_retry(stream_bulk_config, stream_bulk_api):
    stream: BulkIncrementalSalesforceStream = _generate_stream("Account", stream_bulk_config, stream_bulk_api)
    stream._wait_timeout = 0.1  # maximum wait timeout will be 6 seconds
    with requests_mock.Mocker() as m:
        job_id = _prepare_mock(m, stream)
        m.register_uri("GET", stream.path() + f"/{job_id}", json={"state": "InProgress", "id": job_id})
        with pytest.raises(Exception) as err:
            next(stream.read_records(sync_mode=SyncMode.full_refresh))
        assert "stream using BULK API was failed" in str(err.value)
