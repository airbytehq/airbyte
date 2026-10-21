#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

"""Mock server tests for the channel reach report streams.

The Reporting API lists `channel_reach_basic_a1` and `channel_reach_combined_a1` for channels
(thumbnail impressions and impressions click-through rate), and they follow the same
job -> report -> CSV flow as every other report stream.
https://developers.google.com/youtube/reporting/v1/reports/channel_reports#reach-reports
"""

import json
import logging
from typing import Any, Dict, List

import freezegun
import pytest
from _helpers import get_source
from mock_server.config import ConfigBuilder
from mock_server.request_builder import YoutubeAnalyticsRequestBuilder

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_NOW = "2026-10-21T00:00:00Z"
_DEFAULT_START_TIME = "1990-01-01T00:00:00.000000Z"
_METRICS = ["video_thumbnail_impressions", "video_thumbnail_impressions_ctr"]

# Dimensions per the vendor's report tables, which are also each stream's primary key.
_REACH_STREAMS: Dict[str, List[str]] = {
    "channel_reach_basic_a1": ["date", "channel_id", "video_id"],
    "channel_reach_combined_a1": [
        "date",
        "channel_id",
        "video_id",
        "traffic_source_type",
        "traffic_source_detail",
        "operating_system",
        "device_type",
    ],
}

_DIMENSION_VALUES: Dict[str, str] = {
    "date": "20261018",
    "channel_id": "channel-1",
    "video_id": "video-1",
    "traffic_source_type": "9",
    "traffic_source_detail": "",
    "operating_system": "3",
    "device_type": "101",
}


def _csv(stream_name: str) -> str:
    columns = _REACH_STREAMS[stream_name] + _METRICS
    values = [_DIMENSION_VALUES[column] for column in _REACH_STREAMS[stream_name]] + ["1250", "0.0432"]
    return f"{','.join(columns)}\n{','.join(values)}\n"


def _given_reach_report(http_mocker: HttpMocker, stream_name: str) -> None:
    job_id = f"job-{stream_name}"
    report_id = f"report-{stream_name}"
    http_mocker.post(
        YoutubeAnalyticsRequestBuilder.token_request(), HttpResponse(body=json.dumps({"access_token": "token", "expires_in": 3600}))
    )
    http_mocker.get(
        YoutubeAnalyticsRequestBuilder.jobs_endpoint().build(),
        HttpResponse(body=json.dumps({"jobs": [{"id": job_id, "reportTypeId": stream_name}]})),
    )
    http_mocker.get(
        YoutubeAnalyticsRequestBuilder.reports_endpoint(job_id).with_created_after(_DEFAULT_START_TIME).build(),
        HttpResponse(
            body=json.dumps(
                {
                    "reports": [
                        {
                            "id": report_id,
                            "jobId": job_id,
                            "startTime": "2026-10-18T07:00:00Z",
                            "endTime": "2026-10-19T07:00:00Z",
                            "createTime": "2026-10-20T00:00:00Z",
                            "downloadUrl": YoutubeAnalyticsRequestBuilder.download_url(report_id),
                        }
                    ]
                }
            )
        ),
    )
    http_mocker.get(YoutubeAnalyticsRequestBuilder.download_endpoint(report_id).build(), HttpResponse(body=_csv(stream_name)))


@pytest.mark.parametrize("stream_name", sorted(_REACH_STREAMS))
def test_reach_stream_is_discovered_with_vendor_dimensions_as_primary_key(stream_name: str) -> None:
    config = ConfigBuilder().build()
    catalog = get_source(config=config).discover(logging.getLogger("test"), config)
    streams = {stream.name: stream for stream in catalog.streams}

    assert stream_name in streams
    stream = streams[stream_name]
    assert stream.source_defined_primary_key == [[key] for key in _REACH_STREAMS[stream_name]]
    assert SyncMode.incremental in stream.supported_sync_modes
    assert set(_REACH_STREAMS[stream_name] + _METRICS) <= set(stream.json_schema["properties"])
    assert stream.json_schema["properties"]["video_thumbnail_impressions"]["type"] == ["null", "integer"]
    assert stream.json_schema["properties"]["video_thumbnail_impressions_ctr"]["type"] == ["null", "number"]


@pytest.mark.parametrize("stream_name", sorted(_REACH_STREAMS))
@freezegun.freeze_time(_NOW)
def test_reach_stream_reads_records_from_its_reporting_job(stream_name: str) -> None:
    """The stream resolves the job for its own `reportTypeId`, lists its files and decodes the CSV."""
    config = ConfigBuilder().build()
    state = StateBuilder().build()
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()

    with HttpMocker() as http_mocker:
        _given_reach_report(http_mocker, stream_name)
        output = read(get_source(config=config, state=state), config=config, catalog=catalog, state=state)

    assert output.errors == []
    assert len(output.records) == 1
    record = output.records[0].record
    assert record.stream == stream_name
    assert record.data["date"] == 20261018
    assert record.data["video_id"] == "video-1"
    assert set(_REACH_STREAMS[stream_name] + _METRICS) <= set(record.data)
