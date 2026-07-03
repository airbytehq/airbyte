# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import pytest
import requests_mock as rm
import yaml

from airbyte_cdk.models import SyncMode, Type
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder

from .conftest import _YAML_FILE_PATH


def _load_manifest():
    with open(_YAML_FILE_PATH) as f:
        return yaml.safe_load(f)


def test_ads_stream_has_no_record_filter():
    """The ads stream should not filter out records — the CDK handles missing cursor fields."""
    manifest = _load_manifest()
    ads_def = manifest["definitions"]["ads_stream"]
    record_selector = ads_def["retriever"]["record_selector"]
    assert "record_filter" not in record_selector, (
        "ads stream should not have a record_filter; the CDK now handles records with missing cursor fields gracefully"
    )


def test_ads_schema_modify_time_is_nullable():
    """modify_time must be nullable to accommodate Smart+ ads that lack this field."""
    manifest = _load_manifest()
    modify_time = manifest["definitions"]["schemas"]["ads"]["properties"]["modify_time"]
    field_type = modify_time["type"]
    assert isinstance(field_type, list) and "null" in field_type, (
        f"modify_time type should be nullable (e.g. ['null', 'string']), got {field_type}"
    )


@pytest.mark.parametrize(
    "records,expected_count",
    [
        pytest.param(
            [
                {"ad_id": "1", "modify_time": "2024-06-01 00:00:00", "advertiser_id": "12345"},
                {"ad_id": "2", "modify_time": None, "advertiser_id": "12345", "smart_plus_ad_id": "sp_1"},
                {"ad_id": "3", "modify_time": "2024-06-02 00:00:00", "advertiser_id": "12345"},
            ],
            3,
            id="smart_plus_ad_without_modify_time_is_included",
        ),
        pytest.param(
            [
                {"ad_id": "4", "modify_time": None, "advertiser_id": "12345", "smart_plus_ad_id": "sp_2"},
            ],
            1,
            id="only_smart_plus_ad_without_modify_time",
        ),
    ],
)
def test_ads_stream_emits_records_with_null_modify_time(records, expected_count):
    """Records with null modify_time (Smart+ ads) must not be dropped."""
    config = {
        "access_token": "TOKEN",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "environment": {"advertiser_id": "12345"},
    }

    catalog = CatalogBuilder().with_stream("ads", SyncMode.full_refresh).build()
    source = YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=[])

    with rm.Mocker() as m:
        m.get(
            "https://business-api.tiktok.com/open_api/v1.3/ad/get/",
            json={
                "code": 0,
                "message": "ok",
                "data": {
                    "list": records,
                    "page_info": {"page": 1, "page_size": 1000, "total_page": 1, "total_number": len(records)},
                },
            },
        )
        messages = list(source.read(logger=None, config=config, catalog=catalog, state=[]))

    record_messages = [msg for msg in messages if msg.type == Type.RECORD]
    assert len(record_messages) == expected_count, (
        f"Expected {expected_count} records but got {len(record_messages)}; records with null modify_time should not be filtered out"
    )
