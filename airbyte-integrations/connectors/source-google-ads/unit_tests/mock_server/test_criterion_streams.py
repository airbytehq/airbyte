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
    "ad_group_criterion": {
        "adGroup": {"id": "400001"},
        "adGroupCriterion": {
            "resourceName": "customers/1234567890/adGroupCriteria/400001~600001",
            "adGroup": "customers/1234567890/adGroups/400001",
            "criterionId": "600001",
        },
        "changeStatus": {"lastChangeDateTime": "2024-01-05 12:00:00"},
    },
    "ad_listing_group_criterion": {
        "adGroup": {"id": "400001"},
        "adGroupCriterion": {
            "resourceName": "customers/1234567890/adGroupCriteria/400001~600002",
            "criterionId": "600002",
        },
        "changeStatus": {"lastChangeDateTime": "2024-01-05 12:00:00"},
    },
    "campaign_criterion": {
        "campaign": {"id": "700001"},
        "campaignCriterion": {
            "resourceName": "customers/1234567890/campaignCriteria/700001~600003",
            "campaign": "customers/1234567890/campaigns/700001",
        },
        "changeStatus": {"lastChangeDateTime": "2024-01-05 12:00:00"},
    },
}

_KEY_FIELD_CHECKS = {
    "ad_group_criterion": ("ad_group.id", 400001),
    "ad_listing_group_criterion": ("ad_group.id", 400001),
    "campaign_criterion": ("campaign.id", 700001),
}

CRITERION_STREAMS = [
    "ad_group_criterion",
    "ad_listing_group_criterion",
    "campaign_criterion",
]


@pytest.mark.parametrize(
    "stream_name",
    [pytest.param(s, id=s) for s in CRITERION_STREAMS],
)
def test_criterion_full_refresh(stream_name):
    config = ConfigBuilder().with_start_date("2024-01-01").with_end_date("2024-01-14").build()
    with HttpMocker() as http_mocker:
        setup_full_refresh_parent_mocks(http_mocker)
        http_mocker.post(
            HttpRequest(
                url=f"{API_BASE}/customers/{_CUSTOMER_ID}/googleAds:searchStream",
                body=json.dumps({"query": build_full_refresh_query(stream_name, exclude_transformation_fields=True)}),
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
    [pytest.param(s, id=s) for s in CRITERION_STREAMS],
)
def test_criterion_403_ignored(stream_name):
    config = ConfigBuilder().with_start_date("2024-01-01").with_end_date("2024-01-14").build()
    with HttpMocker() as http_mocker:
        setup_full_refresh_parent_mocks(http_mocker)
        http_mocker.post(
            HttpRequest(
                url=f"{API_BASE}/customers/{_CUSTOMER_ID}/googleAds:searchStream",
                body=json.dumps({"query": build_full_refresh_query(stream_name, exclude_transformation_fields=True)}),
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
