#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import datetime
from collections import OrderedDict
from unittest.mock import MagicMock

from source_youtube_analytics.source import ChannelReports, ReportResources


def test_report_resources_path(requests_mock):
    mock_jobs_call = requests_mock.post("https://youtubereporting.googleapis.com/v1/jobs", json={"id": "job1"})

    stream = ReportResources("stream_name", "job1")
    assert stream.path() == "jobs/job1/reports"
    assert not mock_jobs_call.called_once

    stream = ReportResources("stream_name", job_id=None)
    assert not mock_jobs_call.called_once
    assert stream.path() == "jobs/job1/reports"
    assert mock_jobs_call.called_once
    assert stream.path() == "jobs/job1/reports"
    assert mock_jobs_call.called_once
    assert mock_jobs_call.last_request.json() == {"name": "Airbyte reporting job", "reportTypeId": "stream_name"}


def test_report_resources_parse_response():
    stream = ReportResources("stream_name", "job1")

    response = MagicMock()
    response.json = MagicMock(return_value={})
    assert stream.parse_response(response, stream_state={}) == []
    response.json = MagicMock(return_value={"reports": []})
    assert stream.parse_response(response, stream_state={}) == []

    reports = [
        {
            "id": "4317112913",
            "jobId": "1c20da45-0604-4d60-85db-925989df1db6",
            "startTime": "2021-10-25T07:00:00Z",
            "endTime": "2021-10-26T07:00:00Z",
            "createTime": "2021-10-27T04:59:46.114806Z",
            "downloadUrl": "https://youtubereporting.googleapis.com/v1/media/CHANNEL/ybpwL6sPt6SSzazIV400WQ/jobs/1c20da45-0604-4d60-85db-925989df1db6/reports/4317112913?alt=media",
        },
        {
            "id": "4315953856",
            "jobId": "1c20da45-0604-4d60-85db-925989df1db6",
            "startTime": "2021-10-18T07:00:00Z",
            "endTime": "2021-10-19T07:00:00Z",
            "createTime": "2021-10-26T07:43:27.680074Z",
            "downloadUrl": "https://youtubereporting.googleapis.com/v1/media/CHANNEL/ybpwL6sPt6SSzazIV400WQ/jobs/1c20da45-0604-4d60-85db-925989df1db6/reports/4315953856?alt=media",
        },
    ]

    response.json = MagicMock(return_value={"reports": reports})
    result = stream.parse_response(response, stream_state={})

    assert result == [
        {
            "id": "4315953856",
            "jobId": "1c20da45-0604-4d60-85db-925989df1db6",
            "startTime": datetime.datetime(2021, 10, 18, 7, 0, tzinfo=datetime.timezone.utc),
            "endTime": datetime.datetime(2021, 10, 19, 7, 0, tzinfo=datetime.timezone.utc),
            "createTime": datetime.datetime(2021, 10, 26, 7, 43, 27, 680074, tzinfo=datetime.timezone.utc),
            "downloadUrl": "https://youtubereporting.googleapis.com/v1/media/CHANNEL/ybpwL6sPt6SSzazIV400WQ/jobs/1c20da45-0604-4d60-85db-925989df1db6/reports/4315953856?alt=media",
        },
        {
            "id": "4317112913",
            "jobId": "1c20da45-0604-4d60-85db-925989df1db6",
            "startTime": datetime.datetime(2021, 10, 25, 7, 0, tzinfo=datetime.timezone.utc),
            "endTime": datetime.datetime(2021, 10, 26, 7, 0, tzinfo=datetime.timezone.utc),
            "createTime": datetime.datetime(2021, 10, 27, 4, 59, 46, 114806, tzinfo=datetime.timezone.utc),
            "downloadUrl": "https://youtubereporting.googleapis.com/v1/media/CHANNEL/ybpwL6sPt6SSzazIV400WQ/jobs/1c20da45-0604-4d60-85db-925989df1db6/reports/4317112913?alt=media",
        },
    ]


def test_report_resources_next_page_token():
    stream = ReportResources("stream_name", "job1")
    assert stream.next_page_token({}) is None


def test_channel_reports_path():
    parent = ReportResources("stream_name", "job1")
    stream = ChannelReports("stream_name", [], parent=parent)

    stream_slice = {
        "parent": {
            "id": "4317112913",
            "jobId": "1c20da45-0604-4d60-85db-925989df1db6",
            "startTime": datetime.datetime(2021, 10, 25, 7, 0, tzinfo=datetime.timezone.utc),
            "endTime": datetime.datetime(2021, 10, 26, 7, 0, tzinfo=datetime.timezone.utc),
            "createTime": datetime.datetime(2021, 10, 27, 4, 59, 46, 114806, tzinfo=datetime.timezone.utc),
            "downloadUrl": "https://youtubereporting.googleapis.com/v1/media/CHANNEL/ybpwL6sPt6SSzazIV400WQ/jobs/1c20da45-0604-4d60-85db-925989df1db6/reports/4317112913?alt=media",
        }
    }

    path = stream.path(stream_state={}, stream_slice=stream_slice, next_page_token=None)
    assert path == "media/CHANNEL/ybpwL6sPt6SSzazIV400WQ/jobs/1c20da45-0604-4d60-85db-925989df1db6/reports/4317112913?alt=media"


def test_channel_reports_parse_response():
    parent = ReportResources("stream_name", "job1")
    stream = ChannelReports("stream_name", ["date", "channel_id"], parent=parent)

    response = MagicMock()
    response.text = "date,channel_id,likes,dislikes\n20211026,UCybpwL6sPt6SSzazIV400WQ,210,21\n20211026,UCybpwL6sPt6SSzazIV400WQ,150,18\n"

    result = stream.parse_response(response, stream_state={})
    assert list(result) == [
        OrderedDict([("date", "20211026"), ("channel_id", "UCybpwL6sPt6SSzazIV400WQ"), ("likes", "210"), ("dislikes", "21")]),
        OrderedDict([("date", "20211026"), ("channel_id", "UCybpwL6sPt6SSzazIV400WQ"), ("likes", "150"), ("dislikes", "18")]),
    ]
