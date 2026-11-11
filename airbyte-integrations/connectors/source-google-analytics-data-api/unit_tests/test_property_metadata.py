#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from pathlib import Path

import pytest
import requests_mock
import yaml

from airbyte_cdk.legacy.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource


def _get_source(manifest_path: Path, config: dict) -> ManifestDeclarativeSource:
    return ManifestDeclarativeSource(yaml.safe_load(manifest_path.read_text()), config=config)


def _get_config() -> dict:
    return {
        "credentials": {
            "auth_type": "Client",
            "client_id": "client-id",
            "client_secret": "client-secret",
            "refresh_token": "refresh-token",
        },
        "property_ids": ["123", "456"],
        "custom_reports_array": [],
    }


def _mock_token(requests_mock: requests_mock.Mocker) -> None:
    requests_mock.post(
        "https://www.googleapis.com/oauth2/v4/token",
        json={"access_token": "access-token", "expires_in": 3600, "token_type": "Bearer"},
    )


def test_property_metadata_reads_properties(requests_mock: requests_mock.Mocker, manifest_path: Path) -> None:
    config = _get_config()
    _mock_token(requests_mock)
    property_responses = {
        "123": {
            "name": "properties/123",
            "propertyType": "PROPERTY_TYPE_ORDINARY",
            "parent": "accounts/1",
            "createTime": "2024-01-01T00:00:00Z",
            "updateTime": "2024-01-02T00:00:00Z",
            "displayName": "First property",
            "industryCategory": "TECHNOLOGY",
            "timeZone": "America/Los_Angeles",
            "currencyCode": "USD",
            "serviceLevel": "GOOGLE_ANALYTICS_STANDARD",
            "account": "accounts/1",
        },
        "456": {
            "name": "properties/456",
            "propertyType": "PROPERTY_TYPE_ROLLUP",
            "parent": "properties/123",
            "createTime": "2024-02-01T00:00:00Z",
            "updateTime": "2024-02-02T00:00:00Z",
            "displayName": "Second property",
            "industryCategory": "BUSINESS_AND_INDUSTRIAL_MARKETS",
            "timeZone": "Europe/London",
            "currencyCode": "GBP",
            "serviceLevel": "GOOGLE_ANALYTICS_360",
            "account": "accounts/2",
        },
    }
    for property_id, response in property_responses.items():
        requests_mock.get(f"https://analyticsadmin.googleapis.com/v1beta/properties/{property_id}", json=response)

    source = _get_source(manifest_path, config)
    property_metadata = next(stream for stream in source.streams(config) if stream.name == "property_metadata")
    records = [record for partition in property_metadata.generate_partitions() for record in partition.read()]

    requested_fields = {
        "createTime",
        "currencyCode",
        "displayName",
        "industryCategory",
        "name",
        "parent",
        "propertyType",
        "timeZone",
        "updateTime",
    }
    assert [record["property_id"] for record in records] == ["123", "456"]
    assert requested_fields <= records[0].keys()
    assert requested_fields <= records[1].keys()
    assert [record["displayName"] for record in records] == ["First property", "Second property"]
    assert records[0]["createTime"] == "2024-01-01T00:00:00Z"
    assert records[1]["currencyCode"] == "GBP"
    admin_requests = [request.url for request in requests_mock.request_history if "analyticsadmin.googleapis.com" in request.url]
    assert admin_requests == [
        "https://analyticsadmin.googleapis.com/v1beta/properties/123",
        "https://analyticsadmin.googleapis.com/v1beta/properties/456",
    ]


@pytest.mark.parametrize(
    "single_stream_per_report",
    [
        pytest.param(False, id="one_stream_per_property"),
        pytest.param(True, id="one_stream_per_report"),
    ],
)
def test_property_metadata_coexists_with_dynamic_report_streams(
    requests_mock: requests_mock.Mocker, manifest_path: Path, single_stream_per_report: bool
) -> None:
    config = _get_config()
    config["property_ids"] = ["123"]
    config["custom_reports_array"] = [
        {
            "name": "metadata_coexistence_report",
            "dimensions": ["date"],
            "metrics": ["activeUsers"],
        }
    ]
    if single_stream_per_report:
        config["single_stream_per_report"] = True
    _mock_token(requests_mock)
    for property_id in ("123", "456"):
        requests_mock.get(
            f"https://analyticsdata.googleapis.com/v1beta/properties/{property_id}/metadata",
            json={"metrics": [{"apiName": "activeUsers", "type": "TYPE_INTEGER"}]},
        )

    source = _get_source(manifest_path, config)
    stream_names = [stream.name for stream in source.streams(config)]

    assert "property_metadata" in stream_names
    # Consolidated report streams carry a `Consolidated` suffix so they never collide with the
    # per-property stream names. `property_metadata` is static and named the same either way.
    expected_report = "metadata_coexistence_reportConsolidated" if single_stream_per_report else "metadata_coexistence_report"
    assert expected_report in stream_names
    assert len(stream_names) > 1
    assert len(stream_names) == len(set(stream_names))
