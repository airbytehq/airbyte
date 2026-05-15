# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.mock_server.config import ConfigBuilder
from unit_tests.mock_server.conftest import create_source
from unit_tests.mock_server.helpers import (
    API_BASE,
    build_incremental_query,
    build_stream_response,
    setup_full_refresh_parent_mocks,
)


_CUSTOMER_ID = "1234567890"

_STREAM_RECORDS = {
    "ad_group": {
        "campaign": {"id": "700001"},
        "adGroup": {
            "id": "400001",
            "name": "Test Ad Group",
            "status": "ENABLED",
            "campaign": "customers/1234567890/campaigns/700001",
        },
        "segments": {"date": "2024-01-01"},
        "metrics": {"costMicros": "1000000"},
    },
    "ad_group_ad": {
        "adGroup": {"id": "400001"},
        "adGroupAd": {
            "ad": {
                "id": "500001",
                "name": "Test Ad",
                "resourceName": "customers/1234567890/ads/500001",
            },
            "status": "ENABLED",
        },
        "segments": {"date": "2024-01-01"},
        "metrics": {"costMicros": "500000"},
    },
    "customer": {
        "customer": {
            "id": _CUSTOMER_ID,
            "descriptiveName": "Test Customer",
            "autoTaggingEnabled": True,
        },
        "segments": {"date": "2024-01-01"},
        "metrics": {"costMicros": "2000000"},
    },
    "campaign_bidding_strategy": {
        "customer": {"id": _CUSTOMER_ID},
        "campaign": {"id": "700001"},
        "biddingStrategy": {
            "name": "Test Bidding Strategy",
            "currencyCode": "USD",
            "campaignCount": "1",
        },
        "segments": {"date": "2024-01-01"},
    },
    "ad_group_bidding_strategy": {
        "adGroup": {"id": "400001"},
        "biddingStrategy": {
            "name": "Test Bidding Strategy",
            "currencyCode": "USD",
            "campaignCount": "1",
        },
        "segments": {"date": "2024-01-01"},
    },
    "campaign_budget": {
        "customer": {"id": _CUSTOMER_ID},
        "campaign": {"id": "700001"},
        "campaignBudget": {
            "amountMicros": "50000000",
            "deliveryMethod": "STANDARD",
            "resourceName": "customers/1234567890/campaignBudgets/800001",
        },
        "segments": {"date": "2024-01-01"},
    },
}

_KEY_FIELD_CHECKS = {
    "ad_group": ("ad_group.id", 400001),
    "ad_group_ad": ("ad_group.id", 400001),
    "customer": ("customer.id", int(_CUSTOMER_ID)),
    "campaign_bidding_strategy": ("campaign.id", 700001),
    "ad_group_bidding_strategy": ("ad_group.id", 400001),
    "campaign_budget": ("campaign.id", 700001),
}

INCREMENTAL_STREAMS = [
    "ad_group",
    "ad_group_ad",
    "customer",
    "campaign_bidding_strategy",
    "ad_group_bidding_strategy",
    "campaign_budget",
]


@pytest.mark.parametrize(
    "stream_name",
    [pytest.param(s, id=s) for s in INCREMENTAL_STREAMS],
)
def test_incremental_first_sync(stream_name):
    config = ConfigBuilder().with_start_date("2024-01-01").with_end_date("2024-01-14").build()
    with HttpMocker() as http_mocker:
        setup_full_refresh_parent_mocks(http_mocker)
        http_mocker.post(
            HttpRequest(
                url=f"{API_BASE}/customers/{_CUSTOMER_ID}/googleAds:searchStream",
                body=json.dumps({"query": build_incremental_query(stream_name, "2024-01-01", "2024-01-14")}),
            ),
            build_stream_response([_STREAM_RECORDS[stream_name]]),
        )

        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
        source = create_source(config=config, catalog=catalog)
        output = read(source, config=config, catalog=catalog)

    assert len(output.records) == 1
    record = output.records[0].record.data
    key_field, expected_value = _KEY_FIELD_CHECKS[stream_name]
    assert record[key_field] == expected_value


@pytest.mark.parametrize(
    "stream_name",
    [pytest.param(s, id=s) for s in INCREMENTAL_STREAMS],
)
def test_incremental_with_state(stream_name):
    config = ConfigBuilder().with_start_date("2024-01-01").with_end_date("2024-01-14").build()
    state = StateBuilder().with_stream_state(stream_name, {"segments.date": "2024-01-10"}).build()
    with HttpMocker() as http_mocker:
        setup_full_refresh_parent_mocks(http_mocker)
        http_mocker.post(
            HttpRequest(
                url=f"{API_BASE}/customers/{_CUSTOMER_ID}/googleAds:searchStream",
                body=json.dumps({"query": build_incremental_query(stream_name, "2024-01-01", "2024-01-14")}),
            ),
            build_stream_response([_STREAM_RECORDS[stream_name]]),
        )

        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
        source = create_source(config=config, catalog=catalog, state=state)
        output = read(source, config=config, catalog=catalog, state=state)

    assert len(output.records) == 1


@pytest.mark.parametrize(
    "stream_name",
    [pytest.param(s, id=s) for s in INCREMENTAL_STREAMS],
)
def test_incremental_empty(stream_name):
    config = ConfigBuilder().with_start_date("2024-01-01").with_end_date("2024-01-14").build()
    with HttpMocker() as http_mocker:
        setup_full_refresh_parent_mocks(http_mocker)
        http_mocker.post(
            HttpRequest(
                url=f"{API_BASE}/customers/{_CUSTOMER_ID}/googleAds:searchStream",
                body=json.dumps({"query": build_incremental_query(stream_name, "2024-01-01", "2024-01-14")}),
            ),
            build_stream_response([]),
        )

        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
        source = create_source(config=config, catalog=catalog)
        output = read(source, config=config, catalog=catalog)

    assert len(output.records) == 0


@pytest.mark.parametrize(
    "stream_name",
    [pytest.param(s, id=s) for s in INCREMENTAL_STREAMS],
)
def test_incremental_403_ignored(stream_name):
    config = ConfigBuilder().with_start_date("2024-01-01").with_end_date("2024-01-14").build()
    with HttpMocker() as http_mocker:
        setup_full_refresh_parent_mocks(http_mocker)
        http_mocker.post(
            HttpRequest(
                url=f"{API_BASE}/customers/{_CUSTOMER_ID}/googleAds:searchStream",
                body=json.dumps({"query": build_incremental_query(stream_name, "2024-01-01", "2024-01-14")}),
            ),
            HttpResponse(
                body=json.dumps({"error": {"code": 403, "message": "Permission denied"}}),
                status_code=403,
            ),
        )

        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
        source = create_source(config=config, catalog=catalog)
        output = read(source, config=config, catalog=catalog)

    assert len(output.records) == 0
