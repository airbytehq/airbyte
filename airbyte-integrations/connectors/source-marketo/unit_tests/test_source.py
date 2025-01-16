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
from source_marketo.source import Activities, IncrementalMarketoStream, Leads, MarketoExportCreate, MarketoStream, SourceMarketo

from airbyte_cdk.models.airbyte_protocol import SyncMode
from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.utils import AirbyteTracedException

from .conftest import START_DATE, get_stream_by_name


logger = logging.getLogger("airbyte")


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
        "errors": [{"code": "1029", "message": "Export daily quota 500MB exceeded."}],
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
            (
                "Campaign Run ID,Choice Number,Has Predictive,Step ID,Test Variant,attributes\n"
                '1,3,true,10,15,{"spam": "true"}\n'
                '2,3,false,11,16,{"spam": "false"}'
            ),
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


@pytest.mark.parametrize("job_statuses", ((("Created",), ("Completed",)), (("Created",), ("Cancelled",))))
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


@pytest.mark.parametrize("next_page_token", ({"nextPageToken": 2}, {}))
def test_next_page_token(config, next_page_token):
    stream = MarketoStream(config)
    token = stream.next_page_token(Mock(json=Mock(return_value=next_page_token)))
    assert token == (next_page_token or None)


def test_parse_response_incremental(config, requests_mock):
    created_at_record_1 = START_DATE.add(days=1).strftime("%Y-%m-%dT%H:%M:%SZ")
    created_at_record_2 = START_DATE.add(days=3).strftime("%Y-%m-%dT%H:%M:%SZ")
    current_state = START_DATE.add(days=2).strftime("%Y-%m-%dT%H:%M:%SZ")
    response = {"result": [{"id": "1", "createdAt": created_at_record_1}, {"id": "2", "createdAt": created_at_record_2}]}
    requests_mock.get("/rest/v1/campaigns.json", json=response)

    stream = get_stream_by_name("campaigns", config)
    stream.state = {"createdAt": current_state}
    records = []
    for stream_slice in stream.stream_slices(sync_mode=SyncMode.incremental):
        for record in stream.read_records(sync_mode=SyncMode.incremental, stream_slice=stream_slice):
            records.append(dict(record))
    assert records == [{"id": "2", "createdAt": created_at_record_2}]


def test_source_streams(config, activity, requests_mock):
    source = SourceMarketo()
    requests_mock.get("/rest/v1/activities/types.json", json={"result": [activity]})
    streams = source.streams(config)

    # 5 declarative streams (activity_types, segmentations, campaigns, lists, programs),
    # 1 python stream (leads)
    # 1 dynamically created (activities_send_email)
    assert len(streams) == 7
    assert all(isinstance(stream, (MarketoStream, DeclarativeStream)) for stream in streams)


def test_programs_normalize_datetime(config, requests_mock):
    created_at = START_DATE.add(days=1).strftime("%Y-%m-%dT%H:%M:%SZ")
    updated_at = START_DATE.add(days=2).strftime("%Y-%m-%dT%H:%M:%SZ")
    requests_mock.get(
        "/rest/asset/v1/programs.json",
        json={"result": [{"createdAt": f"{created_at}+0000", "updatedAt": f"{updated_at}+0000"}]},
    )

    stream = get_stream_by_name("programs", config)
    stream_slice = stream.stream_slices(sync_mode=SyncMode.full_refresh)[0]
    record = next(stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice))

    assert dict(record) == {"createdAt": created_at, "updatedAt": updated_at}


def test_programs_next_page_token(config):
    page_size = 200
    records = [{"id": i} for i in range(page_size)]
    last_record = {"id": page_size - 1}
    mocked_response = MagicMock()
    mocked_response.json.return_value = {"result": records}
    stream = get_stream_by_name("programs", config)
    assert stream.retriever.paginator.pagination_strategy.next_page_token(mocked_response, len(records), last_record) == page_size


def test_segmentations_next_page_token(config):
    page_size = 200
    records = [{"id": i} for i in range(page_size)]
    last_record = {"id": page_size - 1}
    mocked_response = MagicMock()
    mocked_response.json.return_value = {"result": records}
    stream = get_stream_by_name("segmentations", config)
    assert stream.retriever.paginator.pagination_strategy.next_page_token(mocked_response, len(records), last_record) == page_size


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

    test_lines = ["Hello\x00World\n", "Name,Email\n", "John\x00Doe,john.doe@example.com\n"]
    expected_lines = ["HelloWorld\n", "Name,Email\n", "JohnDoe,john.doe@example.com\n"]
    filtered_lines = stream.filter_null_bytes(test_lines)
    for expected_line, filtered_line in zip(expected_lines, filtered_lines):
        assert expected_line == filtered_line


def test_csv_rows(config):
    stream = Leads(config)

    test_lines = ["Name,Email\n", "John Doe,john.doe@example.com\n", "Jane Doe,jane.doe@example.com\n"]
    expected_records = [{"Name": "John Doe", "Email": "john.doe@example.com"}, {"Name": "Jane Doe", "Email": "jane.doe@example.com"}]
    records = stream.csv_rows(test_lines)
    for expected_record, record in zip(expected_records, records):
        assert expected_record == record


def test_availability_strategy(config):
    stream = Leads(config)
    assert stream.availability_strategy is None


def test_path(config):
    stream = MarketoStream(config)
    assert stream.path() == "rest/v1/marketo_stream.json"


def test_get_state(config):
    stream = IncrementalMarketoStream(config)
    assert stream.state == {}


def test_set_state(config):
    stream = IncrementalMarketoStream(config)
    expected_state = {"id": 1}
    stream.state = expected_state
    assert stream._state == expected_state
