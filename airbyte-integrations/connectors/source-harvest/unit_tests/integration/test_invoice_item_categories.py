# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

from unit_tests.conftest import get_source, get_resource_path
from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from integration.config import ConfigBuilder
from integration.request_builder import HarvestRequestBuilder

_STREAM_NAME = "invoice_item_categories"
_ACCOUNT_ID = "123456"
_API_TOKEN = "test_token_abc123"


class TestInvoiceItemCategoriesStream(TestCase):
    @HttpMocker()
    def test_full_refresh(self, http_mocker: HttpMocker) -> None:
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token(_API_TOKEN).build()
        with open(get_resource_path("http/response/invoice_item_categories.json")) as f:
            response_data = json.load(f)
        http_mocker.get(
            HarvestRequestBuilder.invoice_item_categories_endpoint(_ACCOUNT_ID, _API_TOKEN).with_per_page(50).with_updated_since("2021-01-01T00:00:00Z").build(),
            HttpResponse(body=json.dumps(response_data), status_code=200)
        )
        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 1
        assert all(record.record.stream == _STREAM_NAME for record in output.records)

    @HttpMocker()
    def test_empty_results(self, http_mocker: HttpMocker) -> None:
        config = ConfigBuilder().with_account_id(_ACCOUNT_ID).with_api_token(_API_TOKEN).build()
        http_mocker.get(
            HarvestRequestBuilder.invoice_item_categories_endpoint(_ACCOUNT_ID, _API_TOKEN).with_per_page(50).with_updated_since("2021-01-01T00:00:00Z").build(),
            HttpResponse(body=json.dumps({"invoice_item_categories": [], "per_page": 50, "total_pages": 0, "total_entries": 0, "page": 1, "links": {}}), status_code=200)
        )
        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)
        assert len(output.records) == 0
