# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import csv
import gzip
from io import StringIO

import pytest
from conftest import get_source
from freezegun import freeze_time
from jsonschema import Draft7Validator, FormatChecker
from requests_mock import Mocker

from airbyte_cdk.models import AirbyteRecordMessage, AirbyteStateMessage, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, discover, read


BULK_URL = "https://bulk.api.bingads.microsoft.com/Bulk/v13/Campaigns/DownloadByAccountIds"
STATUS_URL = "https://bulk.api.bingads.microsoft.com/Bulk/v13/BulkDownloadStatus/Query"
STREAMS = [
    ("campaigns_bulk", "Campaigns", "Campaign"),
    ("ad_groups_bulk", "AdGroups", "Ad Group"),
    ("ads_bulk", "Ads", "Responsive Search Ad"),
]
ACCOUNTS = [1, 2]


@pytest.fixture
def bulk_accounts(requests_mock: Mocker, mock_auth_token: None, mock_user_query: None) -> None:
    requests_mock.post(
        "https://clientcenter.api.bingads.microsoft.com/CustomerManagement/v13/Accounts/Search",
        json={"Accounts": [{"Id": account, "ParentCustomerId": 10, "LastModifiedTime": "2024-01-01T00:00:00"} for account in ACCOUNTS]},
    )


def _mock_downloads(requests_mock: Mocker, record_type: str, times: list[str], first_id: int = 100, include_errors: bool = False) -> None:
    requests_mock.post(BULK_URL, json={"DownloadRequestId": "download-id"})
    requests_mock.post(
        STATUS_URL,
        json={"RequestStatus": "Completed", "ResultFileUrl": "https://example.com/bulk.csv", "PercentComplete": 100},
    )
    data = StringIO()
    writer = csv.writer(data)
    extra_fields = {
        "Campaign": {"Campaign": "Example campaign", "Campaign Type": "Search", "Budget": "12.50"},
        "Ad Group": {"Campaign": "Example campaign", "Ad Group": "Example group", "Cpc Bid": "1.25"},
        "Responsive Search Ad": {"Campaign": "Example campaign", "Ad Group": "Example group", "Final Url": "https://example.com"},
    }[record_type]
    if include_errors:
        extra_fields.update({"Error": "", "Error Number": ""})
    writer.writerow(["Type", "Status", "Id", "Parent Id", "Modified Time", *extra_fields])
    writer.writerow(["Format Version", "", "", "", "", *["" for _ in extra_fields]])
    writer.writerow(["Account", "Active", "1", "", "", *["" for _ in extra_fields]])
    for index, time in enumerate(times):
        writer.writerow([record_type, "Deleted" if index == 0 else "Active", index + first_id, 50, time, *extra_fields.values()])
    if include_errors:
        error = {"Error": "CampaignServiceEditorialValidationError", "Error Number": "1042"}
        writer.writerow([f"{record_type} Error", "", first_id, 50, "", *[error.get(field, "") for field in extra_fields]])
    requests_mock.get("https://example.com/bulk.csv", content=gzip.compress(data.getvalue().encode("utf-8-sig")))


def _read(
    stream_name: str,
    config: dict,
    sync_mode: SyncMode,
    state: list[AirbyteStateMessage] | None = None,
) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, sync_mode).build()
    return read(get_source(config, state), config, catalog, state)


def _assert_requests(requests_mock: Mocker, entity: str, last_sync: str | None) -> None:
    bodies = [request.json() for request in requests_mock.request_history if request.url == BULK_URL]
    expected = []
    for account in ACCOUNTS:
        body = {
            "AccountIds": [str(account)],
            "DataScope": "EntityData",
            "DownloadEntities": [entity],
            "DownloadFileType": "Csv",
            "FormatVersion": "6.0",
            "CompressionType": "GZip",
        }
        if last_sync:
            body["LastSyncTimeInUTC"] = last_sync
        expected.append(body)
    assert sorted(bodies, key=lambda body: body["AccountIds"]) == expected
    assert len([request for request in requests_mock.request_history if request.url == STATUS_URL]) == 2
    assert len([request for request in requests_mock.request_history if request.url == "https://example.com/bulk.csv"]) == 2


def _records(output: EntrypointOutput) -> list[AirbyteRecordMessage]:
    records = []
    for message in output.records:
        assert message.record is not None
        records.append(message.record)
    return records


def _states(output: EntrypointOutput) -> list[AirbyteStateMessage]:
    states = []
    for message in output.state_messages:
        assert message.state is not None
        states.append(message.state)
    return states


def _assert_records_and_state(output: EntrypointOutput, cursor: str, first_id: int = 100) -> None:
    assert not output.errors
    assert sorted((record.data["Account Id"], record.data["Id"]) for record in _records(output)) == [
        (account, record_id) for account in ACCOUNTS for record_id in [first_id, first_id + 1]
    ]
    state = output.most_recent_state
    assert state is not None
    assert state.stream_state is not None
    partitions = vars(state.stream_state)["states"]
    assert sorted(partitions, key=lambda state: state["partition"]["account_id"]) == [
        {"partition": {"account_id": str(account)}, "cursor": {"Modified Time": cursor}} for account in ACCOUNTS
    ]


@pytest.mark.parametrize("stream_name, entity, record_type", STREAMS)
def test_bulk_entities_resume_and_fall_back_after_30_days(
    requests_mock: Mocker, bulk_accounts: None, config: dict, stream_name: str, entity: str, record_type: str
) -> None:
    config["lookback_window"] = 30
    config["reports_start_date"] = "2024-02-25"
    with freeze_time("2024-02-26"):
        _mock_downloads(requests_mock, record_type, ["02/24/2024 12:00:00.000", "02/25/2024 12:00:00.000"])
        first = _read(stream_name, config, SyncMode.incremental)
        _assert_requests(requests_mock, entity, None)
        _assert_records_and_state(first, "2024-02-25T12:00:00.000+0000")

    requests_mock.reset_mock()
    config["reports_start_date"] = "2024-02-27"
    with freeze_time("2024-02-27"):
        # Bulk deltas are inclusive: the saved cursor record can overlap the previous read.
        _mock_downloads(requests_mock, record_type, ["02/25/2024 12:00:00.000", "02/26/2024 12:00:00.000"], first_id=101)
        second = _read(stream_name, config, SyncMode.incremental, _states(first))
        _assert_requests(requests_mock, entity, "2024-02-25T12:00:00.000+00:00")
        _assert_records_and_state(second, "2024-02-26T12:00:00.000+0000", first_id=101)

    requests_mock.reset_mock()
    with freeze_time("2024-04-01"):
        _mock_downloads(requests_mock, record_type, ["03/30/2024 12:00:00.000", "03/31/2024 12:00:00.000"])
        third = _read(stream_name, config, SyncMode.incremental, _states(second))
        _assert_requests(requests_mock, entity, None)
        _assert_records_and_state(third, "2024-03-31T12:00:00.000+0000")


@freeze_time("2024-02-26")
@pytest.mark.parametrize("stream_name, entity, record_type", STREAMS)
@pytest.mark.parametrize("sync_mode", [SyncMode.full_refresh, SyncMode.incremental])
def test_bulk_entities_skip_error_rows(
    requests_mock: Mocker, bulk_accounts: None, config: dict, stream_name: str, entity: str, record_type: str, sync_mode: SyncMode
) -> None:
    _mock_downloads(requests_mock, record_type, ["02/24/2024 12:00:00.000", "02/25/2024 12:00:00.000"], include_errors=True)
    output = _read(stream_name, config, sync_mode)
    _assert_requests(requests_mock, entity, None)
    assert not output.errors
    records = _records(output)
    assert sorted((record.data["Account Id"], record.data["Id"]) for record in records) == [(1, 100), (1, 101), (2, 100), (2, 101)]
    assert all(record.data["Type"] == record_type for record in records)
    assert sorted(record.data["Status"] for record in records) == ["Active", "Active", "Deleted", "Deleted"]
    if sync_mode == SyncMode.incremental:
        _assert_records_and_state(output, "2024-02-25T12:00:00.000+0000")


@freeze_time("2024-02-26")
@pytest.mark.parametrize("stream_name, entity, record_type", STREAMS)
def test_bulk_entities_full_refresh_matches_discovered_schema(
    requests_mock: Mocker, bulk_accounts: None, config: dict, stream_name: str, entity: str, record_type: str
) -> None:
    _mock_downloads(requests_mock, record_type, ["02/24/2024 12:00:00.000", "02/25/2024 12:00:00.000"])
    output = _read(stream_name, config, SyncMode.full_refresh)
    _assert_requests(requests_mock, entity, None)
    assert not output.errors
    records = _records(output)
    assert sorted((record.data["Account Id"], record.data["Id"]) for record in records) == [(1, 100), (1, 101), (2, 100), (2, 101)]
    discovery = discover(get_source(config), config).catalog
    assert discovery.catalog is not None
    catalog = discovery.catalog
    stream = next(stream for stream in catalog.streams if stream.name == stream_name)
    assert stream.default_cursor_field == ["Modified Time"]
    assert stream.source_defined_primary_key == [["Id"]]
    assert SyncMode.incremental in stream.supported_sync_modes
    validator = Draft7Validator(stream.json_schema, format_checker=FormatChecker())
    for message in records:
        record = message.data
        assert record["Type"] == record_type
        assert record["Status"] in ["Active", "Deleted"]
        assert record["Parent Id"] == 50
        assert record["Modified Time"] in ["2024-02-24T12:00:00.000+00:00", "2024-02-25T12:00:00.000+00:00"]
        assert set(record) <= set(stream.json_schema["properties"])
        validator.validate(record)
    if record_type == "Campaign":
        assert records[0].data["Budget"] == 12.5
    elif record_type == "Ad Group":
        assert records[0].data["Cpc Bid"] == 1.25
