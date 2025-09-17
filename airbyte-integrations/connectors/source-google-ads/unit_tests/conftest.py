#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys
from pathlib import Path

import pytest
from source_google_ads import SourceGoogleAds
from source_google_ads.models import CustomerModel

from airbyte_cdk import YamlDeclarativeSource
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.state_builder import StateBuilder


# TODO: uncomment once migrated to manifest-only
# def _get_manifest_path() -> Path:
#     source_declarative_manifest_path = Path("/airbyte/integration_code/source_declarative_manifest")
#     if source_declarative_manifest_path.exists():
#         return source_declarative_manifest_path
#     return Path(__file__).parent.parent


# _SOURCE_FOLDER_PATH = _get_manifest_path()
# _YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"

# sys.path.append(str(_SOURCE_FOLDER_PATH))  # to allow loading custom components


# def get_source(config, state=None) -> YamlDeclarativeSource:
#     catalog = CatalogBuilder().build()
#     state = StateBuilder().build() if not state else state
#     return YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)


# def find_stream(stream_name, config, state=None):
#     state = StateBuilder().build() if not state else state
#     streams = get_source(config, state).streams(config=config)
#     for stream in streams:
#         if stream.name == stream_name:
#             return stream
#     raise ValueError(f"Stream {stream_name} not found")


@pytest.fixture(name="config")
def test_config():
    config = {
        "credentials": {
            "developer_token": "test_token",
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "refresh_token": "test_refresh_token",
        },
        "customer_id": "123",
        "start_date": "2021-01-01",
        "conversion_window_days": 14,
        "custom_queries_array": [
            {
                "query": "SELECT campaign.accessible_bidding_strategy, segments.ad_destination_type, campaign.start_date, campaign.end_date FROM campaign",
                "primary_key": None,
                "cursor_field": "campaign.start_date",
                "table_name": "happytable",
            },
            {
                "query": "SELECT segments.ad_destination_type, segments.ad_network_type, segments.day_of_week, customer.auto_tagging_enabled, customer.id, metrics.conversions, campaign.start_date FROM campaign",
                "primary_key": "customer.id",
                "cursor_field": None,
                "table_name": "unhappytable",
            },
            {
                "query": "SELECT ad_group.targeting_setting.target_restrictions FROM ad_group",
                "primary_key": "customer.id",
                "cursor_field": None,
                "table_name": "ad_group_custom",
            },
        ],
    }
    return config


@pytest.fixture(autouse=True)
def mock_oauth_call(requests_mock):
    yield requests_mock.post(
        "https://accounts.google.com/o/oauth2/token",
        json={"access_token": "access_token", "refresh_token": "refresh_token", "expires_in": 0},
    )


@pytest.fixture
def customers(config):
    return [CustomerModel(id=_id, time_zone="local", is_manager_account=False) for _id in config["customer_id"].split(",")]


@pytest.fixture
def additional_customers(config, customers):
    return customers + [CustomerModel(id="789", time_zone="local", is_manager_account=False)]


@pytest.fixture
def customers_manager(config):
    return [CustomerModel(id=_id, time_zone="local", is_manager_account=True) for _id in config["customer_id"].split(",")]


def find_stream(stream_name, config, state=None):
    streams = SourceGoogleAds(config, None, state).streams(config=config)
    for stream in streams:
        if stream.name == stream_name:
            return stream
    raise ValueError(f"Stream {stream_name} not found")


def read_full_refresh(stream_instance: Stream):
    res = []
    schema = stream_instance.get_json_schema()
    slices = stream_instance.stream_slices(sync_mode=SyncMode.full_refresh)
    for slice in slices:
        records = stream_instance.read_records(stream_slice=slice, sync_mode=SyncMode.full_refresh)
        for record in records:
            stream_instance.transformer.transform(record, schema)
            res.append(record)
    return res
