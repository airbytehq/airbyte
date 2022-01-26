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
def stream_config():
    """Generates streams settings for BULK logic"""
    return {
        "client_id": "fake_client_id",
        "client_secret": "fake_client_secret",
        "refresh_token": "fake_refresh_token",
        "start_date": "2010-01-18T21:18:20Z",
        "is_sandbox": False,
        "wait_timeout": 15,
    }


@pytest.fixture(scope="module")
def stream_config_date_format():
    """Generates streams settings with `start_date` in format YYYY-MM-DD"""
    return {
        "client_id": "fake_client_id",
        "client_secret": "fake_client_secret",
        "refresh_token": "fake_refresh_token",
        "start_date": "2010-01-18",
        "is_sandbox": False,
        "wait_timeout": 15,
    }


@pytest.fixture(scope="module")
def stream_config_without_start_date():
    """Generates streams settings for REST logic without start_date"""
    return {
        "client_id": "fake_client_id",
        "client_secret": "fake_client_secret",
        "refresh_token": "fake_refresh_token",
        "is_sandbox": False,
        "wait_timeout": 15,
    }


def _stream_api(stream_config, describe_response_data=None):
    sf_object = Salesforce(**stream_config)
    sf_object.login = Mock()
    sf_object.access_token = Mock()
    sf_object.instance_url = "https://fase-account.salesforce.com"

    response_data = {"fields": [{"name": "LastModifiedDate", "type": "string"}]}
    if describe_response_data:
        response_data = describe_response_data
    sf_object.describe = Mock(return_value=response_data)
    return sf_object


@pytest.fixture(scope="module")
def stream_api(stream_config):
    return _stream_api(stream_config)


@pytest.fixture(scope="module")
def stream_api_v2(stream_config):
    describe_response_data = {"fields": [{"name": "LastModifiedDate", "type": "string"}, {"name": "BillingAddress", "type": "address"}]}
    return _stream_api(stream_config, describe_response_data=describe_response_data)


def _generate_stream(stream_name, stream_config, stream_api, state=None):
    return SourceSalesforce.generate_streams(stream_config, [stream_name], stream_api, state=state)[0]


def test_bulk_sync_creation_failed(stream_config, stream_api):
    stream: BulkIncrementalSalesforceStream = _generate_stream("Account", stream_config, stream_api)
    with requests_mock.Mocker() as m:
        m.register_uri("POST", stream.path(), status_code=400, json=[{"message": "test_error"}])
        with pytest.raises(HTTPError) as err:
            next(stream.read_records(sync_mode=SyncMode.full_refresh))
        assert err.value.response.json()[0]["message"] == "test_error"


def test_stream_unsupported_by_bulk(stream_config, stream_api, caplog):
    """
    Stream `AcceptedEventRelation` is not supported by BULK API, so that REST API stream will be used for it.
    """
    stream_name = "AcceptedEventRelation"
    stream = _generate_stream(stream_name, stream_config, stream_api)
    assert not isinstance(stream, BulkSalesforceStream)


def test_stream_contains_unsupported_properties_by_bulk(stream_config, stream_api_v2):
    """
    Stream `Account` contains compound field such as BillingAddress, which is not supported by BULK API (csv),
    in that case REST API stream will be used for it.
    """
    stream_name = "Account"
    stream = _generate_stream(stream_name, stream_config, stream_api_v2)
    assert not isinstance(stream, BulkSalesforceStream)


def test_stream_has_state_rest_api_should_be_used(stream_config, stream_api):
    """
    Stream `ActiveFeatureLicenseMetric` has state, in that case REST API stream will be used for it.
    """
    stream_name = "ActiveFeatureLicenseMetric"
    state = {stream_name: {"SystemModstamp": "2122-08-22T05:08:29.000Z"}}
    stream = _generate_stream(stream_name, stream_config, stream_api, state=state)
    assert not isinstance(stream, BulkSalesforceStream)


def test_stream_has_no_state_bulk_api_should_be_used(stream_config, stream_api):
    """
    Stream `ActiveFeatureLicenseMetric` has no state, in that case BULK API stream will be used for it.
    """
    stream_name = "ActiveFeatureLicenseMetric"
    state = {"other_stream": {"SystemModstamp": "2122-08-22T05:08:29.000Z"}}
    stream = _generate_stream(stream_name, stream_config, stream_api, state=state)
    assert isinstance(stream, BulkSalesforceStream)


@pytest.mark.parametrize("item_number", [0, 15, 2000, 2324, 193434])
def test_bulk_sync_pagination(item_number, stream_config, stream_api):
    stream: BulkIncrementalSalesforceStream = _generate_stream("Account", stream_config, stream_api)
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


def test_bulk_sync_successful(stream_config, stream_api):
    stream: BulkIncrementalSalesforceStream = _generate_stream("Account", stream_config, stream_api)
    with requests_mock.Mocker() as m:
        job_id = _prepare_mock(m, stream)
        m.register_uri("GET", stream.path() + f"/{job_id}", [{"json": {"state": "JobComplete"}}])
        assert _get_result_id(stream) == 1


def test_bulk_sync_successful_long_response(stream_config, stream_api):
    stream: BulkIncrementalSalesforceStream = _generate_stream("Account", stream_config, stream_api)
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
    stream: BulkIncrementalSalesforceStream = _generate_stream("Account", stream_config, stream_api)
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
def test_bulk_sync_failed_retry(stream_config, stream_api):
    stream: BulkIncrementalSalesforceStream = _generate_stream("Account", stream_config, stream_api)
    stream._wait_timeout = 0.1  # maximum wait timeout will be 6 seconds
    with requests_mock.Mocker() as m:
        job_id = _prepare_mock(m, stream)
        m.register_uri("GET", stream.path() + f"/{job_id}", json={"state": "InProgress", "id": job_id})
        with pytest.raises(Exception) as err:
            next(stream.read_records(sync_mode=SyncMode.full_refresh))
        assert "stream using BULK API was failed" in str(err.value)


@pytest.mark.parametrize(
    "start_date_provided,stream_name,expected_start_date",
    [
        (True, "Account", "2010-01-18T21:18:20Z"),
        (False, "Account", None),
        (True, "ActiveFeatureLicenseMetric", "2010-01-18T21:18:20Z"),
        (False, "ActiveFeatureLicenseMetric", None),
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
        stream = _generate_stream(stream_name, stream_config, stream_api)
    else:
        stream = _generate_stream(stream_name, stream_config_without_start_date, stream_api)

    assert stream.start_date == expected_start_date


def test_stream_start_date_should_be_converted_to_datetime_format(stream_config_date_format, stream_api):
    stream: IncrementalSalesforceStream = _generate_stream("ActiveFeatureLicenseMetric", stream_config_date_format, stream_api)
    assert stream.start_date == "2010-01-18T00:00:00Z"


def test_stream_start_datetime_format_should_not_changed(stream_config, stream_api):
    stream: IncrementalSalesforceStream = _generate_stream("ActiveFeatureLicenseMetric", stream_config, stream_api)
    assert stream.start_date == "2010-01-18T21:18:20Z"


def test_download_data_filter_null_bytes(stream_config, stream_api):
    job_full_url: str = "https://fase-account.salesforce.com/services/data/v52.0/jobs/query/7504W00000bkgnpQAA"
    stream: BulkIncrementalSalesforceStream = _generate_stream("Account", stream_config, stream_api)

    with requests_mock.Mocker() as m:
        m.register_uri("GET", f"{job_full_url}/results", content=b"\x00")
        res = list(stream.download_data(url=job_full_url))
        assert res == []

        m.register_uri("GET", f"{job_full_url}/results", content=b'"Id","IsDeleted"\n\x00"0014W000027f6UwQAI","false"\n\x00\x00')
        res = list(stream.download_data(url=job_full_url))
        assert res == [(1, {"Id": "0014W000027f6UwQAI", "IsDeleted": "false"})]


@pytest.mark.parametrize(
    "streams_criteria,predicted_filtered_streams",
    [
        ([{"criteria": "exacts", "value": "Account"}], ["Account"]),
        (
            [{"criteria": "not exacts", "value": "CustomStreamHistory"}],
            ["Account", "AIApplications", "Leads", "LeadHistory", "Orders", "OrderHistory", "CustomStream"],
        ),
        ([{"criteria": "starts with", "value": "lead"}], ["Leads", "LeadHistory"]),
        (
            [{"criteria": "starts not with", "value": "custom"}],
            ["Account", "AIApplications", "Leads", "LeadHistory", "Orders", "OrderHistory"],
        ),
        ([{"criteria": "ends with", "value": "story"}], ["LeadHistory", "OrderHistory", "CustomStreamHistory"]),
        ([{"criteria": "ends not with", "value": "s"}], ["Account", "LeadHistory", "OrderHistory", "CustomStream", "CustomStreamHistory"]),
        ([{"criteria": "contains", "value": "applicat"}], ["AIApplications"]),
        ([{"criteria": "contains", "value": "hist"}], ["LeadHistory", "OrderHistory", "CustomStreamHistory"]),
        (
            [{"criteria": "not contains", "value": "stream"}],
            ["Account", "AIApplications", "Leads", "LeadHistory", "Orders", "OrderHistory"],
        ),
        (
            [{"criteria": "not contains", "value": "Account"}],
            ["AIApplications", "Leads", "LeadHistory", "Orders", "OrderHistory", "CustomStream", "CustomStreamHistory"],
        ),
    ],
)
def test_discover_with_streams_criteria_param(streams_criteria, predicted_filtered_streams, stream_config):
    updated_config = {**stream_config, **{"streams_criteria": streams_criteria}}
    sf_object = Salesforce(**stream_config)
    sf_object.login = Mock()
    sf_object.access_token = Mock()
    sf_object.instance_url = "https://fase-account.salesforce.com"
    sf_object.describe = Mock(
        return_value={
            "sobjects": [
                {"name": "Account"},
                {"name": "AIApplications"},
                {"name": "Leads"},
                {"name": "LeadHistory"},
                {"name": "Orders"},
                {"name": "OrderHistory"},
                {"name": "CustomStream"},
                {"name": "CustomStreamHistory"},
            ]
        }
    )
    filtered_streams = sf_object.get_validated_streams(config=updated_config)
    assert sorted(filtered_streams) == sorted(predicted_filtered_streams)


def test_pagination_rest(stream_config, stream_api):
    stream_name = "ActiveFeatureLicenseMetric"
    state = {stream_name: {"SystemModstamp": "2122-08-22T05:08:29.000Z"}}

    stream: SalesforceStream = _generate_stream(stream_name, stream_config, stream_api, state=state)
    stream._wait_timeout = 0.1  # maximum wait timeout will be 6 seconds
    next_page_url = "/services/data/v52.0/query/012345"
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
