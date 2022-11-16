#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import csv
import io
import logging
import re
from unittest.mock import Mock

import pytest
import requests_mock
from airbyte_cdk.models import AirbyteStream, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode, SyncMode, Type
from conftest import encoding_symbols_parameters, generate_stream
from requests.exceptions import HTTPError
from source_salesforce.source import SourceSalesforce
from source_salesforce.streams import (
    CSV_FIELD_SIZE_LIMIT,
    BulkIncrementalSalesforceStream,
    BulkSalesforceStream,
    IncrementalSalesforceStream,
    SalesforceStream,
)


def test_bulk_sync_creation_failed(stream_config, stream_api):
    stream: BulkIncrementalSalesforceStream = generate_stream("Account", stream_config, stream_api)
    with requests_mock.Mocker() as m:
        m.register_uri("POST", stream.path(), status_code=400, json=[{"message": "test_error"}])
        with pytest.raises(HTTPError) as err:
            next(stream.read_records(sync_mode=SyncMode.full_refresh))
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
        "https://fase-account.salesforce.com/services/data/v52.0/jobs/query",
        status_code=400,
        json=[{
            "errorCode": "INVALIDENTITY",
            "message": "CustomEntity is not supported by the Bulk API"
        }]
    )
    rest_stream_records = [
        {"id": 1, "name": "custom entity", "created": "2010-11-11"},
        {"id": 11, "name": "custom entity", "created": "2020-01-02"}
    ]
    # mock REST API
    mocker.patch("source_salesforce.source.SalesforceStream.read_records", Mock(return_value=rest_stream_records))
    assert type(stream) is BulkIncrementalSalesforceStream
    assert list(stream.read_records(sync_mode=SyncMode.full_refresh)) == rest_stream_records


def test_stream_unsupported_by_bulk(stream_config, stream_api, caplog):
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


@pytest.mark.parametrize("item_number", [0, 15, 2000, 2324, 3000])
def test_bulk_sync_pagination(item_number, stream_config, stream_api):
    stream: BulkIncrementalSalesforceStream = generate_stream("Account", stream_config, stream_api)
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
    stream: BulkIncrementalSalesforceStream = generate_stream("Account", stream_config, stream_api)
    with requests_mock.Mocker() as m:
        job_id = _prepare_mock(m, stream)
        m.register_uri("GET", stream.path() + f"/{job_id}", [{"json": {"state": "JobComplete"}}])
        assert _get_result_id(stream) == 1


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
        stream = generate_stream(stream_name, stream_config, stream_api)
    else:
        stream = generate_stream(stream_name, stream_config_without_start_date, stream_api)

    assert stream.start_date == expected_start_date


def test_stream_start_date_should_be_converted_to_datetime_format(stream_config_date_format, stream_api):
    stream: IncrementalSalesforceStream = generate_stream("ActiveFeatureLicenseMetric", stream_config_date_format, stream_api)
    assert stream.start_date == "2010-01-18T00:00:00Z"


def test_stream_start_datetime_format_should_not_changed(stream_config, stream_api):
    stream: IncrementalSalesforceStream = generate_stream("ActiveFeatureLicenseMetric", stream_config, stream_api)
    assert stream.start_date == "2010-01-18T21:18:20Z"


def test_download_data_filter_null_bytes(stream_config, stream_api):
    job_full_url: str = "https://fase-account.salesforce.com/services/data/v52.0/jobs/query/7504W00000bkgnpQAA"
    stream: BulkIncrementalSalesforceStream = generate_stream("Account", stream_config, stream_api)

    with requests_mock.Mocker() as m:
        m.register_uri("GET", f"{job_full_url}/results", content=b"\x00")
        res = list(stream.read_with_chunks(*stream.download_data(url=job_full_url)))
        assert res == []

        m.register_uri("GET", f"{job_full_url}/results", content=b'"Id","IsDeleted"\n\x00"0014W000027f6UwQAI","false"\n\x00\x00')
        res = list(stream.read_with_chunks(*stream.download_data(url=job_full_url)))
        assert res == [{"Id": "0014W000027f6UwQAI", "IsDeleted": False}]


@pytest.mark.parametrize(
    "chunk_size, content_type, content, expected_result",
    encoding_symbols_parameters(),
    ids=[f"charset: {x[1]}, chunk_size: {x[0]}" for x in encoding_symbols_parameters()],
)
def test_encoding_symbols(stream_config, stream_api, chunk_size, content_type, content, expected_result):
    job_full_url: str = "https://fase-account.salesforce.com/services/data/v52.0/jobs/query/7504W00000bkgnpQAA"
    stream: BulkIncrementalSalesforceStream = generate_stream("Account", stream_config, stream_api)

    with requests_mock.Mocker() as m:
        m.register_uri("GET", f"{job_full_url}/results", headers={"Content-Type": f"text/html; charset={content_type}"}, content=content)
        res = list(stream.read_with_chunks(*stream.download_data(url=job_full_url, chunk_size=chunk_size)))
        assert res == expected_result


@pytest.mark.parametrize(
    "login_status_code, login_json_resp, discovery_status_code, discovery_resp_json, expected_error_msg",
    (
        (403, [{"errorCode": "REQUEST_LIMIT_EXCEEDED", "message": "TotalRequests Limit exceeded."}], 200, {}, "API Call limit is exceeded"),
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
    source = SourceSalesforce()
    logger = logging.getLogger("airbyte")

    with requests_mock.Mocker() as m:
        m.register_uri("POST", "https://login.salesforce.com/services/oauth2/token", json=login_json_resp, status_code=login_status_code)
        m.register_uri(
            "GET", "https://instance_url/services/data/v52.0/sobjects", json=discovery_resp_json, status_code=discovery_status_code
        )
        result, msg = source.check_connection(logger, stream_config)
        assert result is False
        assert msg == expected_error_msg


def configure_request_params_mock(stream_1, stream_2):
    stream_1.request_params = Mock()
    stream_1.request_params.return_value = {"q": "query"}

    stream_2.request_params = Mock()
    stream_2.request_params.return_value = {"q": "query"}


def test_rate_limit_bulk(stream_config, stream_api, bulk_catalog, state):
    """
    Connector should stop the sync if one stream reached rate limit
    stream_1, stream_2, stream_3, ...
    While reading `stream_1` if 403 (Rate Limit) is received, it should finish that stream with success and stop the sync process.
    Next streams should not be executed.
    """
    stream_1: BulkIncrementalSalesforceStream = generate_stream("Account", stream_config, stream_api)
    stream_2: BulkIncrementalSalesforceStream = generate_stream("Asset", stream_config, stream_api)
    streams = [stream_1, stream_2]
    configure_request_params_mock(stream_1, stream_2)

    stream_1.page_size = 6
    stream_1.state_checkpoint_interval = 5

    source = SourceSalesforce()
    source.streams = Mock()
    source.streams.return_value = streams
    logger = logging.getLogger("airbyte")

    json_response = [{"errorCode": "REQUEST_LIMIT_EXCEEDED", "message": "TotalRequests Limit exceeded."}]
    with requests_mock.Mocker() as m:
        for stream in streams:
            creation_responses = []
            for page in [1, 2]:
                job_id = f"fake_job_{page}_{stream.name}"
                creation_responses.append({"json": {"id": job_id}})

                m.register_uri("GET", stream.path() + f"/{job_id}", json={"state": "JobComplete"})

                resp = ["Field1,LastModifiedDate,ID"] + [f"test,2021-11-0{i},{i}" for i in range(1, 7)]  # 6 records per page

                if page == 1:
                    # Read the first page successfully
                    m.register_uri("GET", stream.path() + f"/{job_id}/results", text="\n".join(resp))
                else:
                    # Requesting for results when reading second page should fail with 403 (Rate Limit error)
                    m.register_uri("GET", stream.path() + f"/{job_id}/results", status_code=403, json=json_response)

                m.register_uri("DELETE", stream.path() + f"/{job_id}")

            m.register_uri("POST", stream.path(), creation_responses)

        result = [i for i in source.read(logger=logger, config=stream_config, catalog=bulk_catalog, state=state)]
        assert stream_1.request_params.called
        assert (
            not stream_2.request_params.called
        ), "The second stream should not be executed, because the first stream finished with Rate Limit."

        records = [item for item in result if item.type == Type.RECORD]
        assert len(records) == 6  # stream page size: 6

        state_record = [item for item in result if item.type == Type.STATE][0]
        assert state_record.state.data["Account"]["LastModifiedDate"] == "2021-11-05"  # state checkpoint interval is 5.


def test_rate_limit_rest(stream_config, stream_api, rest_catalog, state):
    """
    Connector should stop the sync if one stream reached rate limit
    stream_1, stream_2, stream_3, ...
    While reading `stream_1` if 403 (Rate Limit) is received, it should finish that stream with success and stop the sync process.
    Next streams should not be executed.
    """

    stream_1: IncrementalSalesforceStream = generate_stream("KnowledgeArticle", stream_config, stream_api)
    stream_2: IncrementalSalesforceStream = generate_stream("AcceptedEventRelation", stream_config, stream_api)

    stream_1.state_checkpoint_interval = 3
    configure_request_params_mock(stream_1, stream_2)

    source = SourceSalesforce()
    source.streams = Mock()
    source.streams.return_value = [stream_1, stream_2]

    logger = logging.getLogger("airbyte")

    next_page_url = "/services/data/v52.0/query/012345"
    response_1 = {
        "done": False,
        "totalSize": 10,
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
            {
                "ID": 3,
                "LastModifiedDate": "2021-11-17",  # check point interval
            },
            {
                "ID": 4,
                "LastModifiedDate": "2021-11-18",
            },
            {
                "ID": 5,
                "LastModifiedDate": "2021-11-19",
            },
        ],
    }
    response_2 = [{"errorCode": "REQUEST_LIMIT_EXCEEDED", "message": "TotalRequests Limit exceeded."}]

    with requests_mock.Mocker() as m:
        m.register_uri("GET", stream_1.path(), json=response_1, status_code=200)
        m.register_uri("GET", next_page_url, json=response_2, status_code=403)

        result = [i for i in source.read(logger=logger, config=stream_config, catalog=rest_catalog, state=state)]

        assert stream_1.request_params.called
        assert (
            not stream_2.request_params.called
        ), "The second stream should not be executed, because the first stream finished with Rate Limit."

        records = [item for item in result if item.type == Type.RECORD]
        assert len(records) == 5

        state_record = [item for item in result if item.type == Type.STATE][0]
        assert state_record.state.data["KnowledgeArticle"]["LastModifiedDate"] == "2021-11-17"


def test_pagination_rest(stream_config, stream_api):
    stream_name = "AcceptedEventRelation"
    stream: SalesforceStream = generate_stream(stream_name, stream_config, stream_api)
    stream.DEFAULT_WAIT_TIMEOUT_SECONDS = 6  # maximum wait timeout will be 6 seconds
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


def test_csv_reader_dialect_unix():
    stream: BulkSalesforceStream = BulkSalesforceStream(stream_name=None, sf_api=None, pk=None)
    url = "https://fake-account.salesforce.com/services/data/v52.0/jobs/query/7504W00000bkgnpQAA"

    data = [
        {"Id": 1, "Name": '"first_name" "last_name"'},
        {"Id": 2, "Name": "'" + 'first_name"\n' + "'" + 'last_name\n"'},
        {"Id": 3, "Name": "first_name last_name"},
    ]

    with io.StringIO("", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["Id", "Name"], dialect="unix")
        writer.writeheader()
        for line in data:
            writer.writerow(line)
        text = csvfile.getvalue()

    with requests_mock.Mocker() as m:
        m.register_uri("GET", url + "/results", text=text)
        result = [i for i in stream.read_with_chunks(*stream.download_data(url))]
        assert result == data


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
        source = SourceSalesforce()
        source.catalog = catalog
        streams = source.streams(config=stream_config)
    expected_names = catalog_stream_names if catalog else stream_names
    assert not set(expected_names).symmetric_difference(set(stream.name for stream in streams)), "doesn't match excepted streams"

    for stream in streams:
        if stream.name != "Describe":
            assert stream.sobject_options == {"flag1": True, "queryable": True}
    return


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
    assert isinstance(rest_stream, IncrementalSalesforceStream)


def test_bulk_stream_paging(stream_config, stream_api_pk):
    last_modified_date1 = "2022-10-01T00:00:00Z"
    last_modified_date2 = "2022-10-02T00:00:00Z"
    assert last_modified_date1 < last_modified_date2

    stream_config["start_date"] = last_modified_date1
    stream: BulkIncrementalSalesforceStream = generate_stream("Account", stream_config, stream_api_pk)
    stream.page_size = 2

    csv_header = "Field1,LastModifiedDate,Id"
    pages = [
        [f"test,{last_modified_date1},1", f"test,{last_modified_date1},3"],
        [f"test,{last_modified_date1},5", f"test,{last_modified_date2},2"],
        [f"test,{last_modified_date2},2", f"test,{last_modified_date2},4"],
        [f"test,{last_modified_date2},6"],
    ]

    with requests_mock.Mocker() as mocked_requests:

        post_responses = []
        for job_id, page in enumerate(pages, 1):
            post_responses.append({"json": {"id": f"{job_id}"}})
            mocked_requests.register_uri("GET", stream.path() + f"/{job_id}", json={"state": "JobComplete"})
            mocked_requests.register_uri("GET", stream.path() + f"/{job_id}/results", text="\n".join([csv_header] + page))
            mocked_requests.register_uri("DELETE", stream.path() + f"/{job_id}")
        mocked_requests.register_uri("POST", stream.path(), post_responses)

        records = list(stream.read_records(sync_mode=SyncMode.full_refresh))

        assert records == [
            {"Field1": "test", "Id": 1, "LastModifiedDate": last_modified_date1},
            {"Field1": "test", "Id": 3, "LastModifiedDate": last_modified_date1},
            {"Field1": "test", "Id": 5, "LastModifiedDate": last_modified_date1},
            {"Field1": "test", "Id": 2, "LastModifiedDate": last_modified_date2},
            {"Field1": "test", "Id": 2, "LastModifiedDate": last_modified_date2},  # duplicate record
            {"Field1": "test", "Id": 4, "LastModifiedDate": last_modified_date2},
            {"Field1": "test", "Id": 6, "LastModifiedDate": last_modified_date2},
        ]

        def get_query(request_index):
            return mocked_requests.request_history[request_index].json()["query"]

        SELECT = "SELECT LastModifiedDate,Id FROM Account"
        ORDER_BY = "ORDER BY LastModifiedDate,Id ASC LIMIT 2"

        assert get_query(0) == f"{SELECT} WHERE LastModifiedDate >= {last_modified_date1} {ORDER_BY}"

        q = f"{SELECT} WHERE (LastModifiedDate = {last_modified_date1} AND Id > '3') OR (LastModifiedDate > {last_modified_date1}) {ORDER_BY}"
        assert get_query(4) == q

        assert get_query(8) == f"{SELECT} WHERE LastModifiedDate >= {last_modified_date2} {ORDER_BY}"

        q = f"{SELECT} WHERE (LastModifiedDate = {last_modified_date2} AND Id > '4') OR (LastModifiedDate > {last_modified_date2}) {ORDER_BY}"
        assert get_query(12) == q
