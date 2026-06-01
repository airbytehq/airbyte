# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.mock_server.config import ConfigBuilder
from unit_tests.mock_server.conftest import create_source
from unit_tests.mock_server.helpers import (
    API_BASE,
    build_full_refresh_query,
    build_stream_response,
    setup_full_refresh_parent_mocks,
)


_CUSTOMER_ID = "1234567890"

_STREAM_RECORDS = {
    "label": {
        "customer": {"id": _CUSTOMER_ID},
        "label": {
            "id": "100001",
            "name": "Test Label",
            "resourceName": "customers/1234567890/labels/100001",
            "status": "ENABLED",
            "textLabel": {
                "backgroundColor": "#ffffff",
                "description": "desc",
            },
        },
    },
    "audience": {
        "customer": {"id": _CUSTOMER_ID},
        "audience": {
            "id": "200001",
            "name": "Test Audience",
            "description": "desc",
            "resourceName": "customers/1234567890/audiences/200001",
            "status": "ENABLED",
        },
    },
    "customer_label": {
        "customerLabel": {
            "resourceName": "customers/1234567890/customerLabels/300001",
            "customer": "customers/1234567890",
            "label": "customers/1234567890/labels/100001",
        },
        "customer": {"id": _CUSTOMER_ID},
    },
    "ad_group_label": {
        "adGroup": {"id": "400001", "resourceName": "customers/1234567890/adGroups/400001"},
        "label": {"id": "100001", "name": "Test Label"},
        "adGroupLabel": {"resourceName": "customers/1234567890/adGroupLabels/400001~100001"},
    },
    "ad_group_ad_label": {
        "adGroup": {"id": "400001"},
        "adGroupAd": {
            "ad": {
                "id": "500001",
                "resourceName": "customers/1234567890/ads/500001",
            },
        },
        "adGroupAdLabel": {"resourceName": "customers/1234567890/adGroupAdLabels/400001~500001~100001"},
        "label": {"name": "Test Label"},
    },
    "ad_group_criterion_label": {
        "adGroup": {"id": "400001"},
        "label": {"id": "100001"},
        "adGroupCriterionLabel": {
            "adGroupCriterion": "customers/1234567890/adGroupCriteria/400001~600001",
            "label": "customers/1234567890/labels/100001",
            "resourceName": "customers/1234567890/adGroupCriterionLabels/400001~600001~100001",
        },
    },
    "campaign_label": {
        "campaign": {"id": "700001", "resourceName": "customers/1234567890/campaigns/700001"},
        "label": {"id": "100001", "name": "Test Label"},
        "campaignLabel": {"resourceName": "customers/1234567890/campaignLabels/700001~100001"},
    },
    "user_interest": {
        "userInterest": {
            "name": "Test Interest",
            "resourceName": "customers/1234567890/userInterests/800001",
            "taxonomyType": "AFFINITY",
            "userInterestId": "800001",
            "launchedToAll": True,
        },
    },
}

_KEY_FIELD_CHECKS = {
    "label": ("label.id", 100001),
    "audience": ("audience.id", 200001),
    "customer_label": ("customer_label.resource_name", "customers/1234567890/customerLabels/300001"),
    "ad_group_label": ("ad_group.id", 400001),
    "ad_group_ad_label": ("ad_group.id", 400001),
    "ad_group_criterion_label": ("ad_group.id", 400001),
    "campaign_label": ("campaign.id", 700001),
    "user_interest": ("user_interest.name", "Test Interest"),
}

FULL_REFRESH_STREAMS = [
    "label",
    "audience",
    "customer_label",
    "ad_group_label",
    "ad_group_ad_label",
    "ad_group_criterion_label",
    "campaign_label",
    "user_interest",
]


@pytest.mark.parametrize(
    "stream_name",
    [pytest.param(s, id=s) for s in FULL_REFRESH_STREAMS],
)
def test_full_refresh_read(stream_name):
    config = ConfigBuilder().build()
    with HttpMocker() as http_mocker:
        setup_full_refresh_parent_mocks(http_mocker)
        http_mocker.post(
            HttpRequest(
                url=f"{API_BASE}/customers/{_CUSTOMER_ID}/googleAds:searchStream",
                body=json.dumps({"query": build_full_refresh_query(stream_name)}),
            ),
            build_stream_response([_STREAM_RECORDS[stream_name]]),
        )

        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
        source = create_source(config=config, catalog=catalog)
        output = read(source, config=config, catalog=catalog)

    assert len(output.records) == 1
    record = output.records[0].record.data
    key_field, expected_value = _KEY_FIELD_CHECKS[stream_name]
    assert record[key_field] == expected_value


@pytest.mark.parametrize(
    "stream_name",
    [pytest.param(s, id=s) for s in FULL_REFRESH_STREAMS],
)
def test_full_refresh_empty(stream_name):
    config = ConfigBuilder().build()
    with HttpMocker() as http_mocker:
        setup_full_refresh_parent_mocks(http_mocker)
        http_mocker.post(
            HttpRequest(
                url=f"{API_BASE}/customers/{_CUSTOMER_ID}/googleAds:searchStream",
                body=json.dumps({"query": build_full_refresh_query(stream_name)}),
            ),
            build_stream_response([]),
        )

        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
        source = create_source(config=config, catalog=catalog)
        output = read(source, config=config, catalog=catalog)

    assert len(output.records) == 0


@pytest.mark.parametrize(
    "stream_name",
    [pytest.param(s, id=s) for s in FULL_REFRESH_STREAMS],
)
def test_full_refresh_403_ignored(stream_name):
    config = ConfigBuilder().build()
    with HttpMocker() as http_mocker:
        setup_full_refresh_parent_mocks(http_mocker)
        http_mocker.post(
            HttpRequest(
                url=f"{API_BASE}/customers/{_CUSTOMER_ID}/googleAds:searchStream",
                body=json.dumps({"query": build_full_refresh_query(stream_name)}),
            ),
            HttpResponse(
                body=json.dumps({"error": {"code": 403, "message": "Permission denied"}}),
                status_code=403,
            ),
        )

        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
        source = create_source(config=config, catalog=catalog)
        output = read(source, config=config, catalog=catalog)

    assert len(output.records) == 0
