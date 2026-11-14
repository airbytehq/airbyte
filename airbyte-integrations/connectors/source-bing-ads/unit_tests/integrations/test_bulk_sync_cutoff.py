# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import gzip

import pytest
from conftest import get_source
from freezegun import freeze_time
from requests_mock import Mocker

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


BULK_DOWNLOAD_URL = "https://bulk.api.bingads.microsoft.com/Bulk/v13/Campaigns/DownloadByAccountIds"
DOWNLOAD_URL = "https://bingadsappsstorageprod.blob.core.windows.net/download.csv"


@freeze_time("2026-09-26T23:22:00Z")
@pytest.mark.parametrize(
    "cursor, expected_last_sync_time",
    [
        ("2026-08-27T00:16:01.170+0000", None),
        ("2026-08-27T23:21:59.999+0000", None),
        ("2026-08-27T23:22:00.000+0000", None),
        ("2026-08-27T23:26:59.999+0000", None),
        ("2026-08-27T23:27:00.000+0000", "2026-08-27T23:27:00.000+00:00"),
        ("2026-08-27T23:27:00.001+0000", "2026-08-27T23:27:00.001+00:00"),
        ("2026-08-28T01:26:59.999+0200", None),
    ],
    ids=[
        "reported-boundary-day",
        "over-30-days",
        "exactly-30-days",
        "within-safety-margin",
        "five-minute-margin",
        "inside-cutoff",
        "timezone-offset",
    ],
)
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
def test_bulk_requests_only_send_last_sync_time_within_safe_cutoff(
    requests_mock: Mocker,
    mock_auth_token: None,
    mock_user_query: None,
    config: dict[str, str | int],
    stream_name: str,
    download_entity: str,
    record_type: str,
    cursor: str,
    expected_last_sync_time: str | None,
) -> None:
    requests_mock.post(
        "https://clientcenter.api.bingads.microsoft.com/CustomerManagement/v13/Accounts/Search",
        json={"Accounts": [{"Id": account_id, "ParentCustomerId": 3, "LastModifiedTime": "2026-09-26T23:00:00"} for account_id in (1, 2)]},
    )
    requests_mock.post(BULK_DOWNLOAD_URL, json={"DownloadRequestId": "download-id"})
    requests_mock.post(
        "https://bulk.api.bingads.microsoft.com/Bulk/v13/BulkDownloadStatus/Query",
        json={"RequestStatus": "Completed", "ResultFileUrl": DOWNLOAD_URL, "PercentComplete": 100},
    )
    csv = f"Type,Status,Id,Parent Id,Modified Time\n{record_type},Active,123,456,09/26/2026 23:00:00.000\n"
    requests_mock.get(DOWNLOAD_URL, content=gzip.compress(csv.encode("utf-8-sig")))
    state = (
        StateBuilder()
        .with_stream_state(stream_name, {"1": {"Modified Time": cursor}, "2": {"Modified Time": "2026-09-01T12:00:00.000+0000"}})
        .build()
    )
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()

    output = read(get_source(config, state), config, catalog, state)

    requests = [request for request in requests_mock.request_history if request.url == BULK_DOWNLOAD_URL]
    assert len(requests) == 2
    bodies = {request.json()["AccountIds"][0]: request.json() for request in requests}
    for account_id, last_sync_time in (("1", expected_last_sync_time), ("2", "2026-09-01T12:00:00.000+00:00")):
        expected_body = {
            "AccountIds": [account_id],
            "DataScope": "EntityData",
            "DownloadEntities": [download_entity],
            "DownloadFileType": "Csv",
            "FormatVersion": "6.0",
            "CompressionType": "GZip",
        }
        if last_sync_time is not None:
            expected_body["LastSyncTimeInUTC"] = last_sync_time
        assert bodies[account_id] == expected_body
    assert all(request.method == "POST" and not request.qs for request in requests)
    assert sorted((record.record.data["Account Id"], record.record.data["Id"]) for record in output.records) == [(1, 123), (2, 123)]
    assert {
        str(partition["partition"]["account_id"]): partition["cursor"] for partition in output.most_recent_state.stream_state.states
    } == {"1": {"Modified Time": "2026-09-26T23:00:00.000+0000"}, "2": {"Modified Time": "2026-09-26T23:00:00.000+0000"}}
