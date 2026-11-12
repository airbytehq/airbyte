#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import logging

import freezegun
import pytest
import requests_mock
from _helpers import get_source
from mock_server.config import ConfigBuilder
from mock_server.request_builder import YoutubeAnalyticsRequestBuilder

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


_API = YoutubeAnalyticsRequestBuilder.BASE_URL
_DIMENSIONS = {
    "channel_id": "channel-1",
    "video_id": "video-1",
    "live_or_on_demand": "1",
    "subscribed_status": "1",
    "country_code": "US",
}
_REPORTS = [
    (
        "channel_annotations_a1",
        "channel_annotations_a2",
        {"annotation_type": "1", "annotation_id": "annotation-1"},
        {
            "annotation_click_through_rate": 0.25,
            "annotation_close_rate": 0.5,
            "annotation_impressions": 10,
            "annotation_clickable_impressions": 8,
            "annotation_closable_impressions": 6,
            "annotation_clicks": 2,
            "annotation_closes": 3,
        },
    ),
    (
        "channel_end_screens_a1",
        "channel_end_screens_a2",
        {"end_screen_element_type": "1", "end_screen_element_id": "element-1"},
        {"end_screen_element_impressions": 10, "end_screen_element_clicks": 2, "end_screen_element_click_rate": 0.2},
    ),
    (
        "channel_sharing_service_a1",
        "channel_sharing_service_a2",
        {"sharing_service": "1"},
        {"shares": 5},
    ),
]


@pytest.mark.parametrize(("stream_name", "report_type_id", "dimensions", "metrics"), _REPORTS)
@freezegun.freeze_time("2026-10-21T00:00:00Z")
def test_legacy_stream_reads_supported_report_without_changing_records(
    stream_name: str, report_type_id: str, dimensions: dict, metrics: dict
) -> None:
    config = ConfigBuilder().build()
    jobs = [{"id": "legacy-job", "reportTypeId": stream_name}]
    new_job = {"id": "supported-job", "reportTypeId": report_type_id}
    expected_records = [{"date": date, **_DIMENSIONS, **dimensions, **metrics} for date in (20261018, 20261019)]

    def create_job(request, context):
        jobs.append(new_job)
        return new_job

    with requests_mock.Mocker(case_sensitive=True) as mocker:
        mocker.post(YoutubeAnalyticsRequestBuilder.TOKEN_URL, json={"access_token": "token", "expires_in": 3600})
        mocker.get(f"{_API}/jobs", json=lambda request, context: {"jobs": jobs})
        mocker.post(f"{_API}/jobs", json=create_job)
        mocker.get(f"{_API}/jobs/legacy-job/reports", json={})
        mocker.get(
            f"{_API}/jobs/supported-job/reports",
            json={
                "reports": [
                    {
                        "id": f"report-{index}",
                        "jobId": "supported-job",
                        "startTime": "2026-10-18T07:00:00Z",
                        "endTime": "2026-10-19T07:00:00Z",
                        "createTime": f"2026-10-20T00:00:0{index}Z",
                        "downloadUrl": YoutubeAnalyticsRequestBuilder.download_url(f"report-{index}"),
                    }
                    for index in range(2)
                ]
            },
        )
        for index, record in enumerate(expected_records):
            mocker.get(
                YoutubeAnalyticsRequestBuilder.download_url(f"report-{index}"),
                text=f"{','.join(record)}\n{','.join(str(value) for value in record.values())}\n",
            )
        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
        output = read(get_source(config), config, catalog)

    job_creations = [request.json() for request in mocker.request_history if request.method == "POST" and request.path == "/v1/jobs"]
    assert job_creations == [{"name": "Airbyte reporting job", "reportTypeId": report_type_id}]
    assert output.errors == []
    assert sorted((record.record.data for record in output.records), key=lambda record: record["date"]) == expected_records
    assert all(record.record.stream == stream_name for record in output.records)
    api_requests = [(request.method, request.path, request.qs) for request in mocker.request_history if request.path.startswith("/v1/")]
    assert api_requests[:4] == [
        ("GET", "/v1/jobs", {}),
        ("POST", "/v1/jobs", {}),
        ("GET", "/v1/jobs", {}),
        ("GET", "/v1/jobs/supported-job/reports", {"createdAfter": ["1990-01-01T00:00:00.000000Z"]}),
    ]
    assert sorted(api_requests[4:]) == [
        ("GET", "/v1/media/CHANNEL/report-0", {"alt": ["media"]}),
        ("GET", "/v1/media/CHANNEL/report-1", {"alt": ["media"]}),
    ]

    discovered = get_source(config).discover(logging.getLogger("test"), config)
    schema = next(stream.json_schema for stream in discovered.streams if stream.name == stream_name)
    assert set(expected_records[0]) == set(schema["properties"])
    for field, value in metrics.items():
        assert schema["properties"][field]["type"] == ["null", "integer" if isinstance(value, int) else "number"]
