#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from conftest import find_stream
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.types import StreamSlice
from airbyte_cdk.test.state_builder import StateBuilder


@freeze_time("2025-01-01")
def test_bulk_stream_stream_slices(mock_auth_token, mock_user_query, mock_account_query, config, requests_mock):
    stream = find_stream("app_install_ads", config)
    requests_mock.post(
        "https://bulk.api.bingads.microsoft.com/Bulk/v13/Campaigns/DownloadByAccountIds",
        status_code=200,
        json={},
    )
    requests_mock.post(
        "https://bulk.api.bingads.microsoft.com/Bulk/v13/BulkDownloadStatus/Query",
        status_code=200,
        json={
            "RequestStatus": "Completed",
            "ResultFileUrl": "https://bulk.api.bingads.microsoft.com/path/to/bulk/resultquery/url",
            "PercentComplete": 100,
            "ForwardCompatibilityMap": [],
            "Errors": None,
        },
    )
    slices = list(stream.stream_slices(sync_mode=SyncMode.full_refresh))
    assert slices == [
        {"account_id": "1", "start_time": "2020-01-01T00:00:00.000+0000", "end_time": "2025-01-01T00:00:00.000+0000"},
        {"account_id": "2", "start_time": "2020-01-01T00:00:00.000+0000", "end_time": "2025-01-01T00:00:00.000+0000"},
        {"account_id": "3", "start_time": "2020-01-01T00:00:00.000+0000", "end_time": "2025-01-01T00:00:00.000+0000"},
    ]


def test_bulk_stream_transform(mock_auth_token, mock_user_query, mock_account_query, config):
    record = {
        "Ad Group": "Ad Group",
        "App Id": "App Id",
        "Campaign": "Campaign",
        "Custom Parameter": "Custom Parameter",
        "Modified Time": "04/27/2023 18:00:14.970",
    }
    stream = find_stream("app_install_ads", config)
    stream_slice = StreamSlice(
        partition={"account_id": "1"},
        cursor_slice={"start_time": "2020-01-01T00:00:00.000+0000", "end_time": "2025-01-01T00:00:00.000+0000"},
        extra_fields={"ParentCustomerId": "Parent_Customer_Id"},
    )
    transformed_record = list(
        stream.retriever.record_selector.filter_and_transform(
            all_data=[record], stream_state={}, stream_slice=stream_slice, records_schema={}
        )
    )[0]
    assert dict(sorted(transformed_record.items())) == dict(
        sorted(
            {
                "Ad Group": "Ad Group",
                "App Id": "App Id",
                "Campaign": "Campaign",
                "Custom Parameter": "Custom Parameter",
                "Modified Time": "2023-04-27T18:00:14.970+00:00",
                "Account Id": 1,
            }.items()
        )
    )


@freeze_time("2023-11-01T12:00:00.000+00:00")
@pytest.mark.parametrize(
    "stream_state, config_start_date, expected_start_date",
    [
        (
            {"1": {"Modified Time": "2023-10-15T12:00:00.000+00:00"}},
            "2020-01-01",
            "2023-10-15T12:00:00.000+0000",
        ),
        ({"2": {"Modified Time": "2023-10-15T12:00:00.000+00:00"}}, "2020-01-01", "2023-10-15T12:00:00.000+0000"),
        ({}, "2020-01-01", None),
        ({}, "2023-10-21", None),
    ],
    ids=["state_within_30_days", "state_within_30_days_another_account_id", "empty_state", "empty_state_start_date_within_30"],
)
def test_bulk_stream_start_date(
    mock_auth_token, mock_user_query, mock_account_query, requests_mock, config, stream_state, config_start_date, expected_start_date
):
    config["reports_start_date"] = config_start_date if config_start_date is not None else None
    state = StateBuilder().with_stream_state("app_install_ads", stream_state).build()
    stream = find_stream("app_install_ads", config, state)
    requests_mock.post(
        "https://bulk.api.bingads.microsoft.com/Bulk/v13/Campaigns/DownloadByAccountIds",
        status_code=200,
        json={},
    )
    requests_mock.post(
        "https://bulk.api.bingads.microsoft.com/Bulk/v13/BulkDownloadStatus/Query",
        status_code=200,
        json={
            "RequestStatus": "Completed",
            "ResultFileUrl": "https://bulk.api.bingads.microsoft.com/path/to/bulk/resultquery/url",
            "PercentComplete": 100,
            "ForwardCompatibilityMap": [],
            "Errors": None,
        },
    )
    slices = list(stream.stream_slices(sync_mode=SyncMode.incremental))
    assert slices
    if stream_state:
        account_id_from_state = list(stream_state.keys())[0]
        account_id_from_state_present_in_slices = False
        for slice in slices:
            if slice["account_id"] == account_id_from_state:
                account_id_from_state_present_in_slices = True
                assert slice["start_time"] == expected_start_date
        assert account_id_from_state_present_in_slices
    else:
        assert slices == [
            {"account_id": "1", "start_time": f"{config_start_date}T00:00:00.000+0000", "end_time": "2023-11-01T12:00:00.000+0000"},
            {"account_id": "2", "start_time": f"{config_start_date}T00:00:00.000+0000", "end_time": "2023-11-01T12:00:00.000+0000"},
            {"account_id": "3", "start_time": f"{config_start_date}T00:00:00.000+0000", "end_time": "2023-11-01T12:00:00.000+0000"},
        ]
