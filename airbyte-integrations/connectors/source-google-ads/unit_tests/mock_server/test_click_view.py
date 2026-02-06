# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.mock_server.config import ConfigBuilder
from unit_tests.mock_server.conftest import create_source
from unit_tests.mock_server.helpers import (
    API_BASE,
    build_click_view_query,
    build_stream_response,
    setup_full_refresh_parent_mocks,
)


_CUSTOMER_ID = "1234567890"
_STREAM_NAME = "click_view"
_FROZEN_TIME = "2024-01-15T00:00:00Z"

_CLICK_VIEW_RECORD = {
    "adGroup": {"name": "Test Ad Group", "id": "400001"},
    "clickView": {
        "gclid": "test_gclid_123",
        "adGroupAd": "customers/1234567890/adGroupAds/400001~500001",
        "keyword": "customers/1234567890/adGroupCriteria/400001~600001",
        "keywordInfo": {"matchType": "EXACT"},
        "resourceName": "customers/1234567890/clickViews/test_gclid_123",
    },
    "segments": {"date": "2024-01-01", "adNetworkType": "SEARCH"},
}


@freezegun.freeze_time(_FROZEN_TIME)
def test_click_view_first_sync():
    config = ConfigBuilder().with_start_date("2024-01-01").with_end_date("2024-01-01").build()
    with HttpMocker() as http_mocker:
        setup_full_refresh_parent_mocks(http_mocker)
        http_mocker.post(
            HttpRequest(
                url=f"{API_BASE}/customers/{_CUSTOMER_ID}/googleAds:searchStream",
                body=json.dumps({"query": build_click_view_query("2024-01-01")}),
            ),
            build_stream_response([_CLICK_VIEW_RECORD]),
        )

        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        source = create_source(config=config, catalog=catalog)
        output = read(source, config=config, catalog=catalog)

    assert len(output.records) == 1
    record = output.records[0].record.data
    assert record["click_view.gclid"] == "test_gclid_123"
    assert record["segments.date"] == "2024-01-01"


@freezegun.freeze_time(_FROZEN_TIME)
def test_click_view_with_state():
    config = ConfigBuilder().with_start_date("2024-01-01").with_end_date("2024-01-02").build()
    state = StateBuilder().with_stream_state(_STREAM_NAME, {"segments.date": "2024-01-02"}).build()
    with HttpMocker() as http_mocker:
        setup_full_refresh_parent_mocks(http_mocker)
        http_mocker.post(
            HttpRequest(
                url=f"{API_BASE}/customers/{_CUSTOMER_ID}/googleAds:searchStream",
                body=json.dumps({"query": build_click_view_query("2024-01-02")}),
            ),
            build_stream_response([_CLICK_VIEW_RECORD]),
        )

        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        source = create_source(config=config, catalog=catalog, state=state)
        output = read(source, config=config, catalog=catalog, state=state)

    assert len(output.records) == 1


@freezegun.freeze_time(_FROZEN_TIME)
def test_click_view_403_ignored():
    config = ConfigBuilder().with_start_date("2024-01-01").with_end_date("2024-01-01").build()
    with HttpMocker() as http_mocker:
        setup_full_refresh_parent_mocks(http_mocker)
        http_mocker.post(
            HttpRequest(
                url=f"{API_BASE}/customers/{_CUSTOMER_ID}/googleAds:searchStream",
                body=json.dumps({"query": build_click_view_query("2024-01-01")}),
            ),
            HttpResponse(
                body=json.dumps({"error": {"code": 403, "message": "Permission denied"}}),
                status_code=403,
            ),
        )

        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        source = create_source(config=config, catalog=catalog)
        output = read(source, config=config, catalog=catalog)

    assert len(output.records) == 0
