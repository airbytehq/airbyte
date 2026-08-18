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
    setup_incremental_non_manager_parent_mocks,
)


_CUSTOMER_ID = "1234567890"

_STREAM_RECORDS = {
    "campaign": {
        "campaign": {
            "id": "700001",
            "name": "Test Campaign",
            "status": "ENABLED",
            "advertisingChannelType": "SEARCH",
            "resourceName": "customers/1234567890/campaigns/700001",
        },
        "segments": {"date": "2024-01-01"},
        "metrics": {"costMicros": "1000000"},
    },
    "account_performance_report": {
        "customer": {
            "currencyCode": "USD",
            "descriptiveName": "Test Account",
            "timeZone": "America/New_York",
            "id": _CUSTOMER_ID,
        },
        "segments": {"date": "2024-01-01"},
        "metrics": {"clicks": "100", "impressions": "1000"},
    },
    "ad_group_ad_legacy": {
        "adGroup": {"id": "400001"},
        "adGroupAd": {
            "ad": {
                "id": "500001",
                "resourceName": "customers/1234567890/ads/500001",
            },
        },
        "customer": {
            "currencyCode": "USD",
            "descriptiveName": "Test Account",
            "timeZone": "America/New_York",
        },
        "segments": {"date": "2024-01-01"},
        "metrics": {"costMicros": "500000"},
    },
    "display_keyword_view": {
        "customer": {
            "currencyCode": "USD",
            "descriptiveName": "Test Account",
            "timeZone": "America/New_York",
        },
        "segments": {"date": "2024-01-01"},
        "metrics": {"clicks": "50", "impressions": "500"},
    },
    "geographic_view": {
        "customer": {"id": _CUSTOMER_ID, "descriptiveName": "Test Account"},
        "geographicView": {
            "countryCriterionId": "2840",
            "locationType": "AREA_OF_INTEREST",
        },
        "adGroup": {"id": "400001"},
        "segments": {"date": "2024-01-01"},
    },
    "keyword_view": {
        "customer": {"id": _CUSTOMER_ID, "descriptiveName": "Test Account"},
        "campaign": {"id": "700001"},
        "adGroup": {"id": "400001"},
        "adGroupCriterion": {"type": "KEYWORD"},
        "segments": {"date": "2024-01-01"},
        "metrics": {"clicks": "25"},
    },
    "shopping_performance_view": {
        "customer": {"descriptiveName": "Test Account"},
        "adGroup": {"id": "400001", "name": "Test Ad Group", "status": "ENABLED"},
        "segments": {"date": "2024-01-01", "adNetworkType": "SEARCH"},
    },
    "topic_view": {
        "topicView": {"resourceName": "customers/1234567890/topicViews/400001~600001"},
        "customer": {
            "currencyCode": "USD",
            "descriptiveName": "Test Account",
            "timeZone": "America/New_York",
        },
        "segments": {"date": "2024-01-01"},
        "metrics": {"clicks": "10"},
    },
    "user_location_view": {
        "segments": {
            "date": "2024-01-01",
            "dayOfWeek": "MONDAY",
            "month": "2024-01-01",
            "week": "2024-01-01",
            "quarter": "2024-01-01",
        },
        "metrics": {"clicks": "15"},
    },
}

_KEY_FIELD_CHECKS = {
    "campaign": ("campaign.id", 700001),
    "account_performance_report": ("customer.descriptive_name", "Test Account"),
    "ad_group_ad_legacy": ("ad_group.id", 400001),
    "display_keyword_view": ("customer.descriptive_name", "Test Account"),
    "geographic_view": ("customer.id", int(_CUSTOMER_ID)),
    "keyword_view": ("customer.id", int(_CUSTOMER_ID)),
    "shopping_performance_view": ("customer.descriptive_name", "Test Account"),
    "topic_view": ("topic_view.resource_name", "customers/1234567890/topicViews/400001~600001"),
    "user_location_view": ("segments.date", "2024-01-01"),
}

INCREMENTAL_NON_MANAGER_STREAMS = [
    "campaign",
    "account_performance_report",
    "ad_group_ad_legacy",
    "display_keyword_view",
    "geographic_view",
    "keyword_view",
    "shopping_performance_view",
    "topic_view",
    "user_location_view",
]


@pytest.mark.parametrize(
    "stream_name",
    [pytest.param(s, id=s) for s in INCREMENTAL_NON_MANAGER_STREAMS],
)
def test_non_manager_first_sync(stream_name):
    config = ConfigBuilder().with_start_date("2024-01-01").with_end_date("2024-01-14").build()
    with HttpMocker() as http_mocker:
        setup_incremental_non_manager_parent_mocks(http_mocker)
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
    [pytest.param(s, id=s) for s in INCREMENTAL_NON_MANAGER_STREAMS],
)
def test_non_manager_with_state(stream_name):
    config = ConfigBuilder().with_start_date("2024-01-01").with_end_date("2024-01-14").build()
    state = StateBuilder().with_stream_state(stream_name, {"segments.date": "2024-01-10"}).build()
    with HttpMocker() as http_mocker:
        setup_incremental_non_manager_parent_mocks(http_mocker)
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
    [pytest.param(s, id=s) for s in INCREMENTAL_NON_MANAGER_STREAMS],
)
def test_non_manager_403_ignored(stream_name):
    config = ConfigBuilder().with_start_date("2024-01-01").with_end_date("2024-01-14").build()
    with HttpMocker() as http_mocker:
        setup_incremental_non_manager_parent_mocks(http_mocker)
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
