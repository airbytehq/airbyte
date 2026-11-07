# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import re
from pathlib import Path

import freezegun
import pendulum
import pytest
import requests_mock
from jsonschema import Draft7Validator, FormatChecker

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.entrypoint_wrapper import discover

from ..conftest import get_source
from .config import MARKETPLACE_ID, ConfigBuilder
from .utils import read_output


STREAMS = (
    ("GET_BRAND_ANALYTICS_MARKET_BASKET_REPORT", "dataByAsin"),
    ("GET_BRAND_ANALYTICS_REPEAT_PURCHASE_REPORT", "dataByAsin"),
    ("GET_BRAND_ANALYTICS_SEARCH_TERMS_REPORT", "dataByDepartmentAndSearchTerm"),
)
BASE_URL = "https://sellingpartnerapi-na.amazon.com/reports/2021-06-30"


def mock_reports(mocker: requests_mock.Mocker, stream_name: str, records_path: str, empty: bool = False) -> list[dict]:
    jobs = []
    mocker.post("https://api.amazon.com/auth/o2/token", json={"access_token": "test_token", "expires_in": 3600})
    mocker.get(f"{BASE_URL}/reports", json={"reports": []})

    def create(request, context):
        jobs.append(request.json())
        return {"reportId": str(len(jobs) - 1)}

    def poll(request, context):
        job_id = request.path.rsplit("/", 1)[1]
        return {"processingStatus": "DONE", "reportDocumentId": job_id}

    def document(request, context):
        job_id = request.path.rsplit("/", 1)[1]
        return {"url": f"https://reports.test/{job_id}"}

    def download(request, context):
        job = jobs[int(request.path.strip("/"))]
        report = json.loads((Path(__file__).parents[1] / "resource" / "http" / "response" / f"{stream_name}.json").read_text())
        report["reportSpecification"].update(dataStartTime=job["dataStartTime"][:10], dataEndTime=job["dataEndTime"][:10])
        if empty:
            report[records_path] = []
        for record in report[records_path]:
            if "startDate" in record:
                record["startDate"] = job["dataStartTime"][:10]
            if "endDate" in record:
                record["endDate"] = job["dataEndTime"][:10]
        return report

    mocker.post(f"{BASE_URL}/reports", json=create)
    mocker.get(re.compile(f"{BASE_URL}/reports/[0-9]+$"), json=poll)
    mocker.get(re.compile(f"{BASE_URL}/documents/[0-9]+$"), json=document)
    mocker.get(re.compile(r"https://reports.test/[0-9]+$"), json=download)
    return jobs


def expected_jobs(stream_name: str, weeks: list[tuple[str, str]]) -> list[dict]:
    return [
        {
            "reportType": stream_name,
            "marketplaceIds": [MARKETPLACE_ID],
            "reportOptions": {"reportPeriod": "WEEK"},
            "dataStartTime": f"{start}T00:00:00Z",
            "dataEndTime": f"{end}T23:59:59Z",
        }
        for start, end in weeks
    ]


@pytest.mark.parametrize("stream_name,records_path", STREAMS)
@pytest.mark.parametrize("sync_mode", [SyncMode.incremental, SyncMode.full_refresh])
def test_weekly_backfill_and_resume(stream_name: str, records_path: str, sync_mode: SyncMode) -> None:
    config = ConfigBuilder().with_start_date(pendulum.datetime(2024, 5, 15, 12)).without_end_date()
    with requests_mock.Mocker() as mocker:
        jobs = mock_reports(mocker, stream_name, records_path)
        with freezegun.freeze_time("2024-06-02T12:00:00Z"):
            first = read_output(config, stream_name, sync_mode)
            catalog = discover(get_source(config.build()), config.build()).catalog.catalog
        weeks = [("2024-05-12", "2024-05-18"), ("2024-05-19", "2024-05-25"), ("2024-05-26", "2024-06-01")]
        assert sorted(jobs, key=lambda job: job["dataStartTime"]) == expected_jobs(stream_name, weeks)
        assert sorted(record.record.data["endDate"] for record in first.records) == [end for _, end in weeks for _ in range(2)]
        schema = next(stream.json_schema for stream in catalog.streams if stream.name == stream_name)
        assert "endDate" in schema["properties"]
        for record in first.records:
            Draft7Validator(schema, format_checker=FormatChecker()).validate(record.record.data)
        if stream_name == "GET_BRAND_ANALYTICS_SEARCH_TERMS_REPORT":
            assert {record.record.data["clickedAsin"] for record in first.records} == {"B123456789", "B987654321"}
            assert {record.record.data["searchTerm"] for record in first.records} == {"search term rank one"}
        if sync_mode == SyncMode.full_refresh:
            return
        assert first.most_recent_state.stream_state.__dict__ == {"endDate": "2024-06-01"}
        jobs.clear()
        with freezegun.freeze_time("2024-06-16T12:00:00Z"):
            second = read_output(config, stream_name, sync_mode, state=[first.state_messages[-1].state])
        resumed_weeks = [("2024-06-02", "2024-06-08"), ("2024-06-09", "2024-06-15")]
        assert sorted(jobs, key=lambda job: job["dataStartTime"]) == expected_jobs(stream_name, resumed_weeks)
        assert sorted(record.record.data["endDate"] for record in second.records) == [end for _, end in resumed_weeks for _ in range(2)]
        assert second.most_recent_state.stream_state.__dict__ == {"endDate": "2024-06-15"}


@pytest.mark.parametrize("stream_name,records_path", STREAMS)
@pytest.mark.parametrize(
    "end_date,expected_week_ends",
    [
        ("2024-05-22T12:00:00Z", ["2024-05-18"]),
        ("2024-05-25T00:00:00Z", ["2024-05-18"]),
        ("2024-05-25T12:00:00Z", ["2024-05-18"]),
        ("2024-05-25T23:59:58Z", ["2024-05-18"]),
        ("2024-05-25T23:59:59Z", ["2024-05-18", "2024-05-25"]),
        ("2024-06-20T12:00:00Z", ["2024-05-18", "2024-05-25", "2024-06-01"]),
    ],
)
@freezegun.freeze_time("2024-06-05T12:00:00Z")
def test_only_complete_weeks_and_empty_reports_retried(
    stream_name: str, records_path: str, end_date: str, expected_week_ends: list[str]
) -> None:
    config = ConfigBuilder().with_start_date(pendulum.datetime(2024, 5, 15)).with_end_date(pendulum.parse(end_date))
    config.with_period_in_days(1).with_report_stream_lookback_window_in_hours(10)
    with requests_mock.Mocker() as mocker:
        jobs = mock_reports(mocker, stream_name, records_path, empty=True)
        output = read_output(config, stream_name, SyncMode.incremental)
        assert sorted(job["dataEndTime"][:10] for job in jobs) == expected_week_ends
        assert output.records == []
        assert output.most_recent_state.stream_state.__dict__ == {"endDate": "2024-05-12"}
        jobs.clear()
        read_output(config, stream_name, SyncMode.incremental, state=[output.state_messages[-1].state])
        assert sorted(job["dataEndTime"][:10] for job in jobs) == expected_week_ends


@pytest.mark.parametrize("stream_name,records_path", STREAMS)
@freezegun.freeze_time("2024-06-02T12:00:00Z")
def test_stale_weekly_range_does_not_request_expired_history(stream_name: str, records_path: str) -> None:
    config = ConfigBuilder().with_start_date(pendulum.datetime(2017, 5, 15)).with_end_date(pendulum.datetime(2017, 5, 27, 23, 59, 59))
    with requests_mock.Mocker() as mocker:
        jobs = mock_reports(mocker, stream_name, records_path)
        output = read_output(config, stream_name, SyncMode.incremental)
        assert jobs == []
        assert output.records == []
        config.with_end_date(pendulum.datetime(2022, 6, 11, 23, 59, 59))
        output = read_output(config, stream_name, SyncMode.full_refresh)
        assert jobs == expected_jobs(stream_name, [("2022-06-05", "2022-06-11")])
        assert [record.record.data["endDate"] for record in output.records] == ["2022-06-11", "2022-06-11"]
