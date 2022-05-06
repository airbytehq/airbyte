#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import pendulum
import pytest
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import ConfiguredAirbyteCatalog, Type
from source_google_ads.source import SourceGoogleAds


@pytest.fixture
def configured_catalog():
    return {
        "streams": [
            {
                "stream": {
                    "name": "ad_group_ad_report",
                    "json_schema": {},
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "source_defined_cursor": True,
                    "default_cursor_field": ["segments.date"],
                },
                "sync_mode": "incremental",
                "destination_sync_mode": "overwrite",
                "cursor_field": ["segments.date"],
            }
        ]
    }


GAP_DAYS = 14


def test_incremental_sync(config, configured_catalog):
    today = pendulum.now().date()
    start_date = today.subtract(months=1)
    config["start_date"] = start_date.to_date_string()

    google_ads_client = SourceGoogleAds()
    records = list(google_ads_client.read(AirbyteLogger(), config, ConfiguredAirbyteCatalog.parse_obj(configured_catalog)))
    latest_state = None
    for record in records[::-1]:
        if record and record.type == Type.STATE:
            latest_state = record.state.data["ad_group_ad_report"][config["customer_id"]]["segments.date"]
            break

    for message in records:
        if not message or message.type != Type.RECORD:
            continue
        cursor_value = message.record.data["segments.date"]
        assert cursor_value <= latest_state
        assert cursor_value >= start_date.subtract(days=GAP_DAYS).to_date_string()

    #  next sync
    records = list(
        google_ads_client.read(
            AirbyteLogger(),
            config,
            ConfiguredAirbyteCatalog.parse_obj(configured_catalog),
            {"ad_group_ad_report": {"segments.date": latest_state}},
        )
    )

    for record in records:
        if record.type == Type.RECORD:
            assert record.record.data["segments.date"] >= pendulum.parse(latest_state).subtract(days=GAP_DAYS).to_date_string()
        if record.type == Type.STATE:
            assert record.state.data["ad_group_ad_report"][config["customer_id"]]["segments.date"] >= latest_state


def test_abnormally_large_state(config, configured_catalog):
    google_ads_client = SourceGoogleAds()
    records = google_ads_client.read(
        AirbyteLogger(),
        config,
        ConfiguredAirbyteCatalog.parse_obj(configured_catalog),
        {"ad_group_ad_report": {"segments.date": "2222-06-04"}},
    )

    no_data_records = True
    state_records = False
    for record in records:
        if record and record.type == Type.STATE:
            state_records = True
        if record and record.type == Type.RECORD:
            no_data_records = False

    assert no_data_records
    assert state_records
