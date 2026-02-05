#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import json
import logging
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pytest_lazy_fixtures import lf as lazy_fixture

from airbyte_cdk import AirbyteConnectionStatus, AirbyteEntrypoint, AirbyteTracedException
from airbyte_cdk.models import Status, SyncMode
from airbyte_cdk.sources.types import StreamSlice

from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read

from .conftest import find_stream, get_source


logger = logging.getLogger("airbyte")


@pytest.mark.parametrize(
    "site_urls",
    [["https://example1.com", "https://example2.com"], ["https://example.com"]],
)
@pytest.mark.parametrize("sync_mode", [SyncMode.full_refresh, SyncMode.incremental])
@pytest.mark.parametrize("data_state", ["all", "final"])
def test_slice(config_gen, site_urls, sync_mode, data_state):
    # config = {
    #     "start_date": "2021-09-01",
    #     "end_date": "2021-09-07",
    #     "site_urls": site_urls,
    # }
    config = config_gen(site_urls=site_urls, start_date="2021-09-01", end_date="2021-09-07")

    stream = find_stream("search_analytics_by_date", config)

    # search_types = stream.search_types
    search_types = ["web", "news", "image", "video", "discover", "googleNews"]
    stream_slice = stream.stream_slices(sync_mode=sync_mode)

    for site_url in site_urls:
        for search_type in search_types:
            for range_ in [
                {"start_time": "2021-09-01", "end_time": "2021-09-03"},
                {"start_time": "2021-09-04", "end_time": "2021-09-06"},
                {"start_time": "2021-09-07", "end_time": "2021-09-07"},
            ]:
                expected = StreamSlice(
                    cursor_slice={
                        "start_time": range_["start_time"],
                        "end_time": range_["end_time"],
                    },
                    partition={
                        "search_type": search_type,
                        "site_url": site_url,
                    },
                )
                assert next(stream_slice) == expected


def test_check_connection(config_gen, config, requests_mock):
    requests_mock.get("https://www.googleapis.com/webmasters/v3/sites/https%3A%2F%2Fexample.com%2F", json={})
    requests_mock.post("https://oauth2.googleapis.com/token", json={"access_token": "token", "expires_in": 10})

    source = get_source(config=config)

    mock_logger = MagicMock()

    assert source.check(logger=mock_logger, config=config_gen()) == AirbyteConnectionStatus(status=Status.SUCCEEDED)

    # test site_urls
    assert source.check(logger=mock_logger, config=config_gen(site_urls=["https://example.com/"])) == AirbyteConnectionStatus(
        status=Status.SUCCEEDED
    )


def test_config_migrations(config_gen):
    try:
        config_path = Path(__file__).parent / "test_configs" / "config.json"
        assert config_path.exists()

        with open(config_path, "r") as f:
            config = json.load(f)

        og_config = dict(config)

        get_source(config, config_path=str(config_path))

        with open(config_path, "r") as f:
            migrated_config = json.load(f)

        assert "custom_reports_array" in migrated_config
        assert migrated_config["custom_reports_array"] == [{"name": "config_migration_test", "dimensions": ["date", "country", "device"]}]
        assert "custom_reports_array" not in og_config
    finally:
        # Reset config
        with open(config_path, "w") as f:
            json.dump(
                config_gen(
                    custom_reports_array=...,
                    custom_reports='[{"name": "config_migration_test", "dimensions": ["date", "country", "device"]}]',
                ),
                f,
            )


def test_config_validations(config_gen):
    config_valid = config_gen()
    config_invalid_custom_reports_type = config_gen(custom_reports_array={}, custom_reports=...)
    config_invalid_custom_reports_dict_properties = config_gen(
        custom_reports_array=[{"dimensions": ["date", "country", "device"]}], custom_reports=...
    )

    assert get_source(config_valid).streams(config=config_valid)

    with pytest.raises(ValueError) as excinfo_invalid_custom_reports_type:
        get_source(config_invalid_custom_reports_type).streams(config=config_invalid_custom_reports_type)
    assert "JSON schema validation error: {} is not of type 'array'" in str(excinfo_invalid_custom_reports_type.value)

    with pytest.raises(ValueError) as excinfo_invalid_custom_reports_dict_properties:
        get_source(config_invalid_custom_reports_dict_properties).streams(config=config_invalid_custom_reports_dict_properties)
    assert "JSON schema validation error: 'name' is a required property" in str(excinfo_invalid_custom_reports_dict_properties.value)


@pytest.mark.parametrize(
    "test_config, expected",
    [
        (
            lazy_fixture("config"),
            (
                False,
                "Encountered an error while checking availability of stream sites. Error: 401 Client Error: None for url: https://oauth2.googleapis.com/token",
            ),
        ),
        (
            lazy_fixture("service_account_config"),
            (
                False,
                "Encountered an error while checking availability of stream sites. Error: Error while refreshing access token: Failed to sign token: Could not parse the provided public key.",
            ),
        ),
    ],
)
def test_unauthorized_creds_exceptions(test_config, expected, requests_mock):
    source = get_source(test_config)
    requests_mock.post("https://oauth2.googleapis.com/token", status_code=401, json={})
    actual = source.check_connection(logger, test_config)
    assert actual == expected


def test_streams(config):
    source = get_source(config)
    streams = source.streams(config)
    assert len(streams) == 16


def test_streams_without_custom_reports(config_gen):
    config = config_gen(custom_reports_array=..., custom_reports=...)
    source = get_source(config)
    streams = source.streams(config)
    assert len(streams) == 15


@pytest.mark.parametrize(
    "dimensions, expected_status, schema_props, primary_key",
    (
        (["impressions"], Status.FAILED, None, None),
        (
            ["date", "country", "device", "page", "query"],
            Status.SUCCEEDED,
            ["clicks", "ctr", "impressions", "position", "date", "site_url", "search_type", "country", "device", "page", "query"],
            ["date", "country", "device", "page", "query", "site_url", "search_type"],
        ),
        (
            [],
            Status.SUCCEEDED,
            ["clicks", "ctr", "impressions", "position", "date", "site_url", "search_type"],
            ["date", "site_url", "search_type"],
        ),
        (
            ["date"],
            Status.SUCCEEDED,
            ["clicks", "ctr", "impressions", "position", "date", "site_url", "search_type"],
            ["date", "site_url", "search_type"],
        ),
        (
            ["country", "device", "page", "query"],
            Status.SUCCEEDED,
            ["clicks", "ctr", "impressions", "position", "date", "site_url", "search_type", "country", "device", "page", "query"],
            ["date", "country", "device", "page", "query", "site_url", "search_type"],
        ),
        (
            ["country", "device", "page", "query", "date"],
            Status.SUCCEEDED,
            ["clicks", "ctr", "impressions", "position", "date", "site_url", "search_type", "country", "device", "page", "query"],
            ["date", "country", "device", "page", "query", "site_url", "search_type"],
        ),
    ),
)
def test_custom_streams(config_gen, requests_mock, dimensions, expected_status, schema_props, primary_key):
    requests_mock.get("https://www.googleapis.com/webmasters/v3/sites/https%3A%2F%2Fexample.com%2F", json={})
    requests_mock.get("https://www.googleapis.com/webmasters/v3/sites", json={"siteEntry": [{"siteUrl": "https://example.com/"}]})
    requests_mock.post("https://oauth2.googleapis.com/token", json={"access_token": "token", "expires_in": 10})
    custom_reports = [{"name": "custom", "dimensions": dimensions}]

    custom_report_config = config_gen(custom_reports_array=custom_reports, custom_reports=...)
    mock_logger = MagicMock()
    status = get_source(custom_report_config).check(config=custom_report_config, logger=mock_logger).status
    assert status is expected_status
    if status is Status.FAILED:
        return
    stream = find_stream("custom", custom_report_config)
    schema = stream.get_json_schema()
    assert set(schema["properties"]) == set(schema_props)
    assert set(stream.primary_key) == set(primary_key)


# --- Phase 0: Spec Field Tests (Change 1) ---


def test_spec_field_title_is_search_console_properties(config):
    source = get_source(config)
    spec = source.spec(logger=MagicMock())
    site_urls_spec = spec.connectionSpecification["properties"]["site_urls"]
    assert site_urls_spec["title"] == "Search Console Properties"


def test_spec_field_description_contains_format_guidance(config):
    source = get_source(config)
    spec = source.spec(logger=MagicMock())
    site_urls_spec = spec.connectionSpecification["properties"]["site_urls"]
    assert "sc-domain:" in site_urls_spec["description"]
    assert "https://" in site_urls_spec["description"]
    assert "Search Console" in site_urls_spec["title"]


# --- Phase 0: sites_list Stream Tests (Change 3) ---


def test_sites_list_in_stream_names(config):
    source = get_source(config)
    streams = source.streams(config)
    stream_names = [s.name for s in streams]
    assert "sites_list" in stream_names


def test_sites_list_stream_reads_records(config_gen, requests_mock):
    config = config_gen()
    requests_mock.get(
        "https://www.googleapis.com/webmasters/v3/sites",
        json={
            "siteEntry": [
                {"siteUrl": "https://example.com/", "permissionLevel": "siteOwner"},
                {"siteUrl": "sc-domain:example.com", "permissionLevel": "siteFullUser"},
            ]
        },
    )
    requests_mock.post(
        "https://oauth2.googleapis.com/token",
        json={"access_token": "token", "expires_in": 3600},
    )

    source = get_source(config=config)
    catalog = CatalogBuilder().with_stream("sites_list", SyncMode.full_refresh).build()
    output = read(source, config=config, catalog=catalog)

    assert len(output.records) == 2
    assert output.records[0].record.data["siteUrl"] == "https://example.com/"
    assert output.records[0].record.data["permissionLevel"] == "siteOwner"
    assert output.records[1].record.data["siteUrl"] == "sc-domain:example.com"


def test_sites_list_stream_empty_response(config_gen, requests_mock):
    config = config_gen()
    requests_mock.get(
        "https://www.googleapis.com/webmasters/v3/sites",
        json={"siteEntry": []},
    )
    requests_mock.post(
        "https://oauth2.googleapis.com/token",
        json={"access_token": "token", "expires_in": 3600},
    )

    source = get_source(config=config)
    catalog = CatalogBuilder().with_stream("sites_list", SyncMode.full_refresh).build()
    output = read(source, config=config, catalog=catalog)

    assert len(output.records) == 0


# --- Phase 0: Enhanced Error Message Tests (Change 2) ---


def test_check_enhanced_error_invalid_url_with_suggestions(config_gen, requests_mock):
    config = config_gen(site_urls=["https://wrong-site.com/"])
    requests_mock.get(
        "https://www.googleapis.com/webmasters/v3/sites/https%3A%2F%2Fwrong-site.com%2F",
        status_code=403,
        json={"error": {"message": "User does not have sufficient permission"}},
    )
    requests_mock.get(
        "https://www.googleapis.com/webmasters/v3/sites",
        json={
            "siteEntry": [
                {"siteUrl": "https://example.com/", "permissionLevel": "siteOwner"},
                {"siteUrl": "sc-domain:example.com", "permissionLevel": "siteFullUser"},
            ]
        },
    )
    requests_mock.post(
        "https://oauth2.googleapis.com/token",
        json={"access_token": "token", "expires_in": 3600},
    )

    source = get_source(config=config)
    result = source.check(logger=MagicMock(), config=config)

    assert result.status == Status.FAILED
    assert "https://example.com/" in result.message
    assert "sc-domain:example.com" in result.message
    assert "Choose the property that matches" in result.message
    assert "Original error:" in result.message


def test_check_enhanced_error_empty_sites_list(config_gen, requests_mock):
    config = config_gen(site_urls=["https://no-access.com/"])
    requests_mock.get(
        "https://www.googleapis.com/webmasters/v3/sites/https%3A%2F%2Fno-access.com%2F",
        status_code=403,
        json={"error": {"message": "User does not have sufficient permission"}},
    )
    requests_mock.get(
        "https://www.googleapis.com/webmasters/v3/sites",
        json={"siteEntry": []},
    )
    requests_mock.post(
        "https://oauth2.googleapis.com/token",
        json={"access_token": "token", "expires_in": 3600},
    )

    source = get_source(config=config)
    result = source.check(logger=MagicMock(), config=config)

    assert result.status == Status.FAILED
    assert "No Search Console properties were found" in result.message
    assert "Original error:" in result.message


def test_check_enhanced_error_sites_list_auth_failure(config_gen, requests_mock):
    """When GET /sites returns 401, the fallback message provides static format guidance."""
    config = config_gen(site_urls=["https://wrong-site.com/"])
    requests_mock.get(
        "https://www.googleapis.com/webmasters/v3/sites/https%3A%2F%2Fwrong-site.com%2F",
        status_code=403,
        json={"error": {"message": "Forbidden"}},
    )
    requests_mock.get(
        "https://www.googleapis.com/webmasters/v3/sites",
        status_code=401,
        json={"error": {"message": "Invalid credentials"}},
    )
    requests_mock.post(
        "https://oauth2.googleapis.com/token",
        json={"access_token": "token", "expires_in": 3600},
    )

    source = get_source(config=config)
    result = source.check(logger=MagicMock(), config=config)

    assert result.status == Status.FAILED
    # Fallback message contains static format examples
    assert "sc-domain:example.com" in result.message
    assert "https://example.com/" in result.message
    assert "Original error:" in result.message


def test_check_backward_compatibility_valid_config(config_gen, config, requests_mock):
    requests_mock.get(
        "https://www.googleapis.com/webmasters/v3/sites/https%3A%2F%2Fexample.com%2F",
        json={"siteUrl": "https://example.com/", "permissionLevel": "siteOwner"},
    )
    requests_mock.post(
        "https://oauth2.googleapis.com/token",
        json={"access_token": "token", "expires_in": 3600},
    )

    source = get_source(config=config)
    result = source.check(logger=MagicMock(), config=config_gen())

    assert result == AirbyteConnectionStatus(status=Status.SUCCEEDED)
