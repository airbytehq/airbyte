#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import sys
import zipfile
from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.state_builder import StateBuilder


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]


def _get_manifest_path() -> Path:
    source_declarative_manifest_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if source_declarative_manifest_path.exists():
        return source_declarative_manifest_path
    return Path(__file__).parent.parent


_SOURCE_FOLDER_PATH = _get_manifest_path()
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"
sys.path.append(str(_SOURCE_FOLDER_PATH))  # to allow loading custom components


@pytest.fixture(autouse=True)
def patch_time(mocker):
    mocker.patch("time.sleep")


@pytest.fixture(name="config")
def config_fixture():
    """Generates streams settings from a config file"""
    return {
        "tenant_id": "common",
        "developer_token": "fake_developer_token",
        "refresh_token": "fake_refresh_token",
        "client_id": "fake_client_id",
        "reports_start_date": "2020-01-01",
        "lookback_window": 0,
    }


@pytest.fixture(name="config_without_start_date")
def config_without_start_date_fixture():
    """Generates streams settings from a config file"""
    return {
        "tenant_id": "common",
        "developer_token": "fake_developer_token",
        "refresh_token": "fake_refresh_token",
        "client_id": "fake_client_id",
        "lookback_window": 0,
    }


@pytest.fixture(name="config_with_account_names")
def config_with_account_names_fixture():
    """Generates streams settings from a config file"""
    return {
        "tenant_id": "common",
        "developer_token": "fake_developer_token",
        "refresh_token": "fake_refresh_token",
        "client_id": "fake_client_id",
        "reports_start_date": "2020-01-01",
        "account_names": [{"operator": "Equals", "name": "airbyte"}, {"operator": "Contains", "name": "demo"}],
        "lookback_window": 0,
    }


@pytest.fixture(name="config_with_custom_reports")
def config_with_custom_reports_fixture():
    """Generates streams settings with custom reports from a config file"""
    return {
        "tenant_id": "common",
        "developer_token": "fake_developer_token",
        "refresh_token": "fake_refresh_token",
        "client_id": "fake_client_id",
        "reports_start_date": "2020-01-01",
        "lookback_window": 0,
        "custom_reports": [
            {
                "name": "my test custom report",
                "reporting_object": "DSAAutoTargetPerformanceReport",
                "report_columns": [
                    "AbsoluteTopImpressionRatePercent",
                    "AccountId",
                    "AccountName",
                    "AccountNumber",
                    "AccountStatus",
                    "AdDistribution",
                    "AdGroupId",
                    "AdGroupName",
                    "AdGroupStatus",
                    "AdId",
                    "AllConversionRate",
                    "AllConversions",
                    "AllConversionsQualified",
                    "AllCostPerConversion",
                    "AllReturnOnAdSpend",
                    "AllRevenue",
                ],
                "report_aggregation": "Weekly",
            }
        ],
    }


@pytest.fixture(name="logger_mock")
def logger_mock_fixture():
    return MagicMock()


@pytest.fixture(name="mock_auth_token")
def mock_auth_token_fixture(requests_mock):
    requests_mock.post(
        "https://login.microsoftonline.com/common/oauth2/v2.0/token",
        status_code=200,
        json={"access_token": "test", "expires_in": "900", "refresh_token": "test"},
    )


@pytest.fixture(name="mock_user_query")
def mock_user_query_fixture(requests_mock):
    requests_mock.post(
        "https://clientcenter.api.bingads.microsoft.com/CustomerManagement/v13/User/Query",
        status_code=200,
        json={"User": {"Id": 1}},
    )


@pytest.fixture(name="mock_account_query")
def mock_account_query_fixture(requests_mock):
    requests_mock.post(
        "https://clientcenter.api.bingads.microsoft.com/CustomerManagement/v13/Accounts/Search",
        status_code=200,
        json={
            "Accounts": [
                {"Id": 1, "LastModifiedTime": "2022-02-02T22:22:22"},
                {"Id": 2, "LastModifiedTime": "2022-02-02T22:22:22"},
                {"Id": 3, "LastModifiedTime": "2022-02-02T22:22:22"},
            ]
        },
    )


def get_source(config, state=None) -> YamlDeclarativeSource:
    catalog = CatalogBuilder().build()
    state = StateBuilder().build() if not state else state
    return YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)


def find_stream(stream_name, config, state=None):
    state = StateBuilder().build() if not state else state
    streams = get_source(config, state).streams(config=config)
    for stream in streams:
        if stream.name == stream_name:
            return stream
    raise ValueError(f"Stream {stream_name} not found")


def create_zip_from_csv(filename: str) -> bytes:
    """
    Creates a zip file containing a CSV file from the resource/response folder.
    The CSV is stored directly in the zip without additional gzip compression.

    Args:
        filename: The name of the CSV file without extension

    Returns:
        The zip file content as bytes
    """
    # Build path to the CSV file in resource/response folder
    csv_path = Path(__file__).parent / f"resource/response/{filename}.csv"

    # Read the CSV content
    with open(csv_path, "r") as csv_file:
        csv_content = csv_file.read()

    # Create a zip file containing the CSV file directly (without gzip compression)
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w") as zip_file:
        zip_file.writestr(f"{filename}.csv", csv_content)

    return zip_buffer.getvalue()
