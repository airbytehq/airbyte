# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import gzip
from io import BytesIO
from zipfile import ZipFile

import pytest
from conftest import get_source
from freezegun import freeze_time
from requests_mock import Mocker

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.state_builder import StateBuilder


BULK_DOWNLOAD_URL = "https://bulk.api.bingads.microsoft.com/Bulk/v13/Campaigns/DownloadByAccountIds"
REPORT_SUBMIT_URL = "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Submit"
DOWNLOAD_URL = "https://bingadsappsstorageprod.blob.core.windows.net/download.csv"


@pytest.fixture
def lookback_account(requests_mock: Mocker, mock_auth_token: None, mock_user_query: None) -> None:
    requests_mock.post(
        "https://clientcenter.api.bingads.microsoft.com/CustomerManagement/v13/Accounts/Search",
        json={"Accounts": [{"Id": 1, "ParentCustomerId": 2, "LastModifiedTime": "2024-01-01T00:00:00"}]},
    )


def _read_incremental(stream_name: str, config: dict[str, str | int], cursor_field: str, cursor_value: str) -> EntrypointOutput:
    state = StateBuilder().with_stream_state(stream_name, {"1": {cursor_field: cursor_value}}).build()
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    return read(get_source(config, state), config, catalog, state)


@freeze_time("2024-02-26")
@pytest.mark.parametrize("lookback_window", [1, 30])
@pytest.mark.parametrize(
    "stream_name, download_entity, record_type",
    [
        ("labels", "Labels", "Label"),
        ("ad_group_labels", "AdGroupLabels", "Ad Group Label"),
        ("app_install_ad_labels", "AppInstallAdLabels", "App Install Ad Label"),
        ("app_install_ads", "AppInstallAds", "App Install Ad"),
        ("keywords", "Keywords", "Keyword"),
        ("keyword_labels", "KeywordLabels", "Keyword Label"),
        ("campaign_labels", "CampaignLabels", "Campaign Label"),
        ("budget", "Budgets", "Budget"),
    ],
)
def test_bulk_requests_resume_at_saved_cursor_without_lookback(
    requests_mock: Mocker,
    lookback_account: None,
    config: dict[str, str | int],
    stream_name: str,
    download_entity: str,
    record_type: str,
    lookback_window: int,
) -> None:
    config["lookback_window"] = lookback_window
    requests_mock.post(BULK_DOWNLOAD_URL, json={"DownloadRequestId": "download-id"})
    requests_mock.post(
        "https://bulk.api.bingads.microsoft.com/Bulk/v13/BulkDownloadStatus/Query",
        json={"RequestStatus": "Completed", "ResultFileUrl": DOWNLOAD_URL, "PercentComplete": 100},
    )
    csv = f"Type,Status,Id,Parent Id,Modified Time\n{record_type},Active,123,456,01/29/2024 12:55:12.028\n"
    requests_mock.get(DOWNLOAD_URL, content=gzip.compress(csv.encode("utf-8-sig")))

    output = _read_incremental(stream_name, config, "Modified Time", "2024-01-29T12:54:12.028+00:00")

    requests = [request.json() for request in requests_mock.request_history if request.url == BULK_DOWNLOAD_URL]
    assert len(requests) == 1
    assert requests[0]["DownloadEntities"] == [download_entity]
    assert requests[0]["LastSyncTimeInUTC"] == "2024-01-29T12:54:12.028+00:00"
    assert len(output.records) == 1
    assert output.records[0].record.data["Id"] == 123
    assert output.most_recent_state.stream_state.states[0]["cursor"] == {"Modified Time": "2024-01-29T12:55:12.028+0000"}


@freeze_time("2024-05-08")
@pytest.mark.parametrize(
    "reports_start_date, expected_start_day",
    [(None, 4), ("2024-01-01", 4), ("2024-05-05", 5)],
    ids=["no_start_date", "with_start_date", "bounded_by_start_date"],
)
@pytest.mark.parametrize(
    "stream_name, cursor_field, cursor_value, report_time, expected_record_time",
    [
        ("account_performance_report_daily", "TimePeriod", "2024-05-06", "2024-05-05", "2024-05-05"),
        (
            "account_performance_report_hourly",
            "TimePeriod",
            "2024-05-06T00:00:00+00:00",
            "2024-05-05|12",
            "2024-05-05T12:00:00+00:00",
        ),
        ("budget_summary_report", "Date", "2024-05-06", "05/05/2024", "2024-05-05"),
    ],
)
def test_report_requests_revisit_lookback_window(
    requests_mock: Mocker,
    lookback_account: None,
    config: dict[str, str | int],
    stream_name: str,
    cursor_field: str,
    cursor_value: str,
    report_time: str,
    expected_record_time: str,
    reports_start_date: str | None,
    expected_start_day: int,
) -> None:
    config["lookback_window"] = 2
    if reports_start_date is None:
        del config["reports_start_date"]
    else:
        config["reports_start_date"] = reports_start_date
    requests_mock.post(REPORT_SUBMIT_URL, json={"ReportRequestId": "report-id"})
    requests_mock.post(
        "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Poll",
        json={"ReportRequestStatus": {"Status": "Success", "ReportDownloadUrl": DOWNLOAD_URL}},
    )
    zipped_report = BytesIO()
    with ZipFile(zipped_report, "w") as archive:
        archive.writestr("report.csv", f"{cursor_field},AccountId\n{report_time},1\n")
    requests_mock.get(DOWNLOAD_URL, content=zipped_report.getvalue())

    output = _read_incremental(stream_name, config, cursor_field, cursor_value)

    requests = [request.json() for request in requests_mock.request_history if request.url == REPORT_SUBMIT_URL]
    assert len(requests) == 1
    assert requests[0]["ReportRequest"]["Time"]["CustomDateRangeStart"] == {"Day": expected_start_day, "Month": 5, "Year": 2024}
    assert len(output.records) == 1
    assert output.records[0].record.data[cursor_field] == expected_record_time
    assert output.most_recent_state.stream_state.states[0]["cursor"] == {cursor_field: cursor_value}
