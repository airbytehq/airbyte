#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import os
import tracemalloc
from functools import partial
from unittest.mock import ANY, MagicMock, Mock, patch

import pendulum
import pytest
import requests
from airbyte_cdk.models.airbyte_protocol import SyncMode
from airbyte_cdk.utils import AirbyteTracedException
from source_marketo.source import (
    Activities,
    Campaigns,
    IncrementalMarketoStream,
    Leads,
    MarketoExportCreate,
    MarketoStream,
    Programs,
    Segmentations,
    SourceMarketo,
)


def test_create_export_job(mocker, send_email_stream, caplog):
    mocker.patch("time.sleep")
    caplog.set_level(logging.WARNING)
    slices = list(send_email_stream.stream_slices(sync_mode=SyncMode.incremental))
    assert slices == [
        {"endAt": ANY, "id": "2c09ce6d", "startAt": ANY},
        {"endAt": ANY, "id": "cd465f55", "startAt": ANY},
        {"endAt": ANY, "id": "232aafb4", "startAt": ANY},
    ]
    assert "Failed to create export job! Status is failed!" in caplog.records[-1].message


def test_should_retry_quota_exceeded(config, requests_mock):
    create_job_url = "https://602-euo-598.mktorest.com/rest/v1/leads/export/create.json?batchSize=300"
    response_json = {
        "requestId": "d2ca#18c0b9833bf",
        "success": False,
        "errors": [
            {
                "code": "1029",
                "message": "Export daily quota 500MB exceeded."
            }
        ]
    }
    requests_mock.register_uri("GET", create_job_url, status_code=200, json=response_json)

    response = requests.get(create_job_url)
    with pytest.raises(AirbyteTracedException) as e:
        MarketoExportCreate(config).should_retry(response)

    assert e.value.message == "Daily limit for job extractions has been reached (resets daily at 12:00AM CST)."



@pytest.mark.parametrize(
    "activity, expected_schema",
    (
        (
            {
                "id": 1,
                "name": "daily_meeting",
                "description": "Connect to a daily meeting",
                "primaryAttribute": {"name": "Meeting ID", "dataType": "integer"},
                "attributes": [
                    {"name": "Priority", "dataType": "number"},
                    {"name": "Speakers", "dataType": "integer"},
                    {"name": "Phone number", "dataType": "phone"},
                    {"name": "Cost per person", "dataType": "currency"},
                    {"name": "Is mandatory", "dataType": "boolean"},
                    {"name": "Participants", "dataType": "array"},
                    {"name": "Date", "dataType": "date"},
                    {"name": "Time spent per person", "dataType": "double"},
                ],
            },
            {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "additionalProperties": True,
                "properties": {
                    "activityDate": {"format": "date-time", "type": ["null", "string"]},
                    "activityTypeId": {"type": ["null", "integer"]},
                    "campaignId": {"type": ["null", "integer"]},
                    "costperperson": {"type": ["number", "null"]},
                    "date": {"format": "date", "type": ["string", "null"]},
                    "ismandatory": {"type": ["boolean", "null"]},
                    "leadId": {"type": ["null", "integer"]},
                    "marketoGUID": {"type": ["null", "string"]},
                    "participants": {"items": {"type": ["integer", "number", "string", "null"]}, "type": ["array", "null"]},
                    "phonenumber": {"type": ["string", "null"]},
                    "primaryAttributeValue": {"type": ["null", "string"]},
                    "primaryAttributeValueId": {"type": ["null", "string"]},
                    "priority": {"type": ["string", "null"]},
                    "speakers": {"type": ["integer", "null"]},
                    "timespentperperson": {"type": ["string", "null"]},
                },
                "type": ["null", "object"],
            },
        ),
        (
            {
                "id": 1,
                "name": "daily_meeting",
                "description": "Connect to a daily meeting",
                "primaryAttribute": {"name": "Meeting ID", "dataType": "integer"},
            },
            {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "additionalProperties": True,
                "properties": {
                    "activityDate": {"format": "date-time", "type": ["null", "string"]},
                    "activityTypeId": {"type": ["null", "integer"]},
                    "campaignId": {"type": ["null", "integer"]},
                    "leadId": {"type": ["null", "integer"]},
                    "marketoGUID": {"type": ["null", "string"]},
                    "primaryAttributeValue": {"type": ["null", "string"]},
                    "primaryAttributeValueId": {"type": ["null", "string"]},
                },
                "type": ["null", "object"],
            },
        ),
    ),
)
def test_activities_schema(activity, expected_schema, config):
    cls = type(activity["name"], (Activities,), {"activity": activity})
    assert cls(config).get_json_schema() == expected_schema


@pytest.mark.parametrize(
    "response_text, expected_records",
    (
        (
            """Campaign Run ID,Choice Number,Has Predictive,Step ID,Test Variant,attributes
1,3,true,10,15,{"spam": "true"}
2,3,false,11,16,{"spam": "false"}""",
            [
                {
                    "Campaign Run ID": "1",
                    "Choice Number": "3",
                    "Has Predictive": "true",
                    "Step ID": "10",
                    "Test Variant": "15",
                    "spam": "true",
                },
                {
                    "Campaign Run ID": "2",
                    "Choice Number": "3",
                    "Has Predictive": "false",
                    "Step ID": "11",
                    "Test Variant": "16",
                    "spam": "false",
                },
            ],
        ),
    ),
)
def test_export_parse_response(send_email_stream, response_text, expected_records):
    def iter_lines(*args, **kwargs):
        yield from response_text.splitlines()

    assert list(send_email_stream.parse_response(Mock(iter_lines=iter_lines, request=Mock(url="/send_email/1")))) == expected_records


def test_memory_usage(send_email_stream, file_generator):
    min_file_size = 5 * (1024**2)  # 5 MB
    big_file_path, records_generated = file_generator(min_size=min_file_size)
    small_file_path, _ = file_generator(min_size=1)

    def iter_lines(file_path="", **kwargs):
        with open(file_path, "r") as file:
            for line in file:
                yield line

    tracemalloc.start()
    records = 0

    for _ in send_email_stream.parse_response(
        Mock(iter_lines=partial(iter_lines, file_path=big_file_path), request=Mock(url="/send_email/1"))
    ):
        records += 1
    _, big_file_peak = tracemalloc.get_traced_memory()
    assert records == records_generated

    tracemalloc.reset_peak()
    tracemalloc.clear_traces()

    for _ in send_email_stream.parse_response(
        Mock(iter_lines=partial(iter_lines, file_path=small_file_path), request=Mock(url="/send_email/1"))
    ):
        pass
    _, small_file_peak = tracemalloc.get_traced_memory()

    os.remove(big_file_path)
    os.remove(small_file_path)
    # First we run parse_response() on a large file and track how much memory was consumed.
    # Then we do the same with a tiny file. The goal is not to load the whole file into memory when parsing the response,
    # so we assert the memory consumed was almost the same for two runs. Allowed delta is 50 KB which is 1% of a big file size.
    assert abs(big_file_peak - small_file_peak) < 50 * 1024


@pytest.mark.parametrize(
    "job_statuses",
    (
        (("Created",), ("Completed",)),
        (
            ("Created",),
            ("Cancelled",),
        ),
    ),
)
def test_export_sleep(send_email_stream, job_statuses):
    def tuple_to_generator(tuple_):
        yield from tuple_

    job_statuses_side_effect = [tuple_to_generator(tuple_) for tuple_ in job_statuses]
    stream_slice = {"startAt": "2020-08-01", "endAt": "2020-08-02", "id": "1"}
    with patch("source_marketo.source.MarketoExportStart.read_records", return_value=iter([Mock()])) as export_start:
        with patch("source_marketo.source.MarketoExportStatus.read_records", side_effect=job_statuses_side_effect) as export_status:
            with patch("source_marketo.source.sleep") as sleep:
                if job_statuses[-1] == ("Cancelled",):
                    with pytest.raises(Exception):
                        send_email_stream.sleep_till_export_completed(stream_slice)
                else:
                    assert send_email_stream.sleep_till_export_completed(stream_slice) is True
                export_start.assert_called()
                export_status.assert_called()
                sleep.assert_called()


def test_programs_request_params(config):
    stream = Programs(config)
    params = stream.request_params(
        stream_slice={"startAt": "2020-08-01", "endAt": "2020-08-02"}, next_page_token={"nextPageToken": 2}, stream_state={}
    )
    assert params == {
        "batchSize": 200,
        "maxReturn": 200,
        "earliestUpdatedAt": "2020-08-01",
        "latestUpdatedAt": "2020-08-02",
        "nextPageToken": 2,
    }


@pytest.mark.parametrize(
    "next_page_token",
    (
        {"nextPageToken": 2},
        {},
    ),
)
def test_next_page_token(mocker, config, next_page_token):
    stream = MarketoStream(config)
    token = stream.next_page_token(Mock(json=Mock(return_value=next_page_token)))
    assert token == (next_page_token or None)


@pytest.mark.parametrize(
    "response, state, expected_records",
    (
        (
            {"result": [{"id": "1", "createdAt": "2020-07-01T00:00:00Z"}, {"id": "2", "createdAt": "2020-08-02T00:00:00Z"}]},
            {"createdAt": "2020-08-01T20:20:00Z"},
            [{"id": "2", "createdAt": "2020-08-02T00:00:00Z"}],
        ),
    ),
)
def test_parse_response_incremental(config, response, state, expected_records):
    stream = Campaigns(config)
    records = stream.parse_response(Mock(json=Mock(return_value=response)), stream_state=state)
    assert list(records) == expected_records


def test_source_streams(config, activity):
    source = SourceMarketo()
    with patch("source_marketo.source.ActivityTypes.read_records", Mock(return_value=[activity])):
        streams = source.streams(config)
    assert len(streams) == 7
    assert all(isinstance(stream, MarketoStream) for stream in streams)


@pytest.mark.parametrize(
    "status_code, response, is_connection_successful, error_msg",
    (
        (200, "", True, None),
        (
            400,
            "Bad request",
            False,
            "HTTPError('400 Client Error: None for url: https://602-euo-598.mktorest.com/rest/v1/leads/describe')",
        ),
        (
            403,
            "Forbidden",
            False,
            "HTTPError('403 Client Error: None for url: https://602-euo-598.mktorest.com/rest/v1/leads/describe')",
        ),
    ),
)
def test_check_connection(config, requests_mock, status_code, response, is_connection_successful, error_msg):
    requests_mock.register_uri("GET", "https://602-euo-598.mktorest.com/rest/v1/leads/describe", status_code=status_code)
    source = SourceMarketo()
    success, error = source.check_connection(logger=None, config=config)
    assert success is is_connection_successful
    assert error == error_msg


@pytest.mark.parametrize(
    "input, format, expected_result",
    (
        ("2020-08-01T20:20:21Z", "%Y-%m-%dT%H:%M:%SZ%z", "2020-08-01T20:20:21Z"),
        ("2020-08-01 20:20", "%Y-%m-%d %H:%M", "2020-08-01T20:20:00Z"),
        ("2020-08-01", "%Y-%m-%dT%H:%M:%SZ%z", "2020-08-01"),
    ),
)
def test_programs_normalize_datetime(config, input, format, expected_result):
    stream = Programs(config)
    assert stream.normalize_datetime(input, format) == expected_result

def test_programs_next_page_token(config):
    mock_json = MagicMock()
    mock_json.return_value = {"result": [{"test": 'testValue'}]}
    mocked_response = MagicMock()
    mocked_response.json = mock_json
    stream = Programs(config)
    result = stream.next_page_token(mocked_response)
    assert result == {"offset": 201}

@pytest.mark.parametrize("input, stream_state, expected_result",[(
      {"result": [{"id": "1", "createdAt": "2020-07-01T00:00:00Z+0000", "updatedAt": "2020-07-01T00:00:00Z+0000"}]},
      {"updatedAt": "2020-06-01T00:00:00Z"},
      [{"id": "1", "createdAt": "2020-07-01T00:00:00Z", "updatedAt": "2020-07-01T00:00:00Z"}],
    )],
)
def test_programs_parse_response(mocker, config, input, stream_state, expected_result):
    response = requests.Response()
    mocker.patch.object(response, "json", return_value=input)
    stream = Programs(config)
    result = stream.parse_response(response, stream_state)
    assert list(result) == expected_result

def test_segmentations_next_page_token(config):
    mock_json = MagicMock()
    mock_json.return_value = {"result": [{"test": 'testValue'}]}
    mocked_response = MagicMock()
    mocked_response.json = mock_json
    stream = Segmentations(config)
    result = stream.next_page_token(mocked_response)
    assert result == {"offset": 201}

today = pendulum.now()
yesterday = pendulum.now().subtract(days=1).strftime("%Y-%m-%dT%H:%M:%SZ")
today = today.strftime("%Y-%m-%dT%H:%M:%SZ")


@pytest.mark.parametrize(
    "latest_record, current_state, expected_state",
    (
        ({}, {}, "start_date"),
        ({"updatedAt": None}, {"updatedAt": None}, "start_date"),
        ({}, {"updatedAt": None}, "start_date"),
        ({"updatedAt": None}, {}, "start_date"),
        ({}, {"updatedAt": today}, {"updatedAt": today}),
        ({"updatedAt": None}, {"updatedAt": today}, {"updatedAt": today}),
        ({"updatedAt": today}, {"updatedAt": None}, {"updatedAt": today}),
        ({"updatedAt": today}, {}, {"updatedAt": today}),
        ({"updatedAt": yesterday}, {"updatedAt": today}, {"updatedAt": today}),
        ({"updatedAt": today}, {"updatedAt": yesterday}, {"updatedAt": today}),
    ),
)
def test_get_updated_state(config, latest_record, current_state, expected_state):
    stream = Leads(config)
    if expected_state == "start_date":
        expected_state = {"updatedAt": config["start_date"]}
    assert stream.get_updated_state(latest_record, current_state) == expected_state


def test_filter_null_bytes(config):
    stream = Leads(config)

    test_lines = [
        "Hello\x00World\n",
        "Name,Email\n",
        "John\x00Doe,john.doe@example.com\n"
    ]
    expected_lines = [
        "HelloWorld\n",
        "Name,Email\n",
        "JohnDoe,john.doe@example.com\n"
    ]
    filtered_lines = stream.filter_null_bytes(test_lines)
    for expected_line, filtered_line in zip(expected_lines, filtered_lines):
        assert expected_line == filtered_line


def test_csv_rows(config):
    stream = Leads(config)

    test_lines = [
        "Name,Email\n",
        "John Doe,john.doe@example.com\n",
        "Jane Doe,jane.doe@example.com\n"
    ]
    expected_records = [
        {"Name": "John Doe", "Email": "john.doe@example.com"},
        {"Name": "Jane Doe", "Email": "jane.doe@example.com"}
    ]
    records = stream.csv_rows(test_lines)
    for expected_record, record in zip(expected_records, records):
        assert expected_record == record

def test_availablity_strategy(config):
    stream = Leads(config)
    assert stream.availability_strategy == None

def test_path(config):
    stream = MarketoStream(config)
    assert stream.path() == "rest/v1/marketo_stream.json"

def test_get_state(config):
    stream = IncrementalMarketoStream(config)
    assert stream.state == {}

def test_set_tate(config):
    stream = IncrementalMarketoStream(config)
    expected_state = {"id": 1}
    stream.state = expected_state
    assert stream._state == expected_state
