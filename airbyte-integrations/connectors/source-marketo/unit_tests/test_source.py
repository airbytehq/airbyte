#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from unittest.mock import ANY, Mock, patch

import pytest
from airbyte_cdk.models.airbyte_protocol import SyncMode
from source_marketo.source import Activities, Campaigns, MarketoStream, Programs, SourceMarketo


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
                    "date": {"format": "date-time", "type": ["string", "null"]},
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
    assert list(send_email_stream.parse_response(Mock(text=response_text))) == expected_records


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
    assert len(streams) == 6
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
def test_normalize_datetime(config, input, format, expected_result):
    stream = Programs(config)
    assert stream.normalize_datetime(input, format) == expected_result
