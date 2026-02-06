# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json

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

_STREAM_NAME = "label"
_CUSTOMER_ID = "1234567890"


def test_label_full_refresh():
    config = ConfigBuilder().build()
    with HttpMocker() as http_mocker:
        setup_full_refresh_parent_mocks(http_mocker)
        http_mocker.post(
            HttpRequest(
                url=f"{API_BASE}/customers/{_CUSTOMER_ID}/googleAds:searchStream",
                body=json.dumps({"query": build_full_refresh_query(_STREAM_NAME)}),
            ),
            build_stream_response(
                [
                    {
                        "customer": {"id": "1234567890"},
                        "label": {
                            "id": "100001",
                            "name": "Test Label",
                            "resourceName": "customers/1234567890/labels/100001",
                            "status": "ENABLED",
                            "textLabel": {
                                "backgroundColor": "#ffffff",
                                "description": "A test label",
                            },
                        },
                    }
                ]
            ),
        )

        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        source = create_source(config=config, catalog=catalog)
        output = read(source, config=config, catalog=catalog)

    assert len(output.records) == 1
    record = output.records[0].record.data
    assert record["label.id"] == 100001
    assert record["label.name"] == "Test Label"
    assert record["label.status"] == "ENABLED"
    assert record["label.text_label.background_color"] == "#ffffff"
    assert record["customer.id"] == 1234567890


def test_label_full_refresh_empty():
    config = ConfigBuilder().build()
    with HttpMocker() as http_mocker:
        setup_full_refresh_parent_mocks(http_mocker)
        http_mocker.post(
            HttpRequest(
                url=f"{API_BASE}/customers/{_CUSTOMER_ID}/googleAds:searchStream",
                body=json.dumps({"query": build_full_refresh_query(_STREAM_NAME)}),
            ),
            build_stream_response([]),
        )

        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        source = create_source(config=config, catalog=catalog)
        output = read(source, config=config, catalog=catalog)

    assert len(output.records) == 0


def test_label_403_ignored():
    config = ConfigBuilder().build()
    with HttpMocker() as http_mocker:
        setup_full_refresh_parent_mocks(http_mocker)
        http_mocker.post(
            HttpRequest(
                url=f"{API_BASE}/customers/{_CUSTOMER_ID}/googleAds:searchStream",
                body=json.dumps({"query": build_full_refresh_query(_STREAM_NAME)}),
            ),
            HttpResponse(
                body=json.dumps({"error": {"code": 403, "message": "Permission denied"}}),
                status_code=403,
            ),
        )

        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        source = create_source(config=config, catalog=catalog)
        output = read(source, config=config, catalog=catalog)

    assert len(output.records) == 0
