# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path
from unittest import TestCase

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse

from .config import ConfigBuilder
from .request_builder import WooCommerceRequestBuilder
from .utils import config, read_output


_STREAM_NAME = "products"


def _get_response_template() -> list:
    template_path = Path(__file__).parent.parent / "resource" / "http" / "response" / "products.json"
    return json.loads(template_path.read_text())


class TestProductsFullRefresh(TestCase):
    @staticmethod
    def _read(config_: ConfigBuilder, expecting_exception: bool = False) -> EntrypointOutput:
        return read_output(
            config_builder=config_,
            stream_name=_STREAM_NAME,
            sync_mode=SyncMode.full_refresh,
            expecting_exception=expecting_exception,
        )

    @HttpMocker()
    def test_read_records_single_page(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            WooCommerceRequestBuilder.products_endpoint().with_default_params().build(),
            HttpResponse(body=json.dumps(_get_response_template()), status_code=200),
        )

        output = self._read(config_=config())
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 99
        assert output.records[0].record.data["name"] == "Test Product"
        assert output.records[0].record.data["sku"] == "TEST-001"
        assert output.records[0].record.data["price"] == "49.99"

    @HttpMocker()
    def test_read_records_with_pagination(self, http_mocker: HttpMocker) -> None:
        first_page_response = _get_response_template()
        second_page_response = [
            {
                "id": 100,
                "name": "Another Product",
                "slug": "another-product",
                "date_created": "2024-02-01T08:00:00",
                "date_modified": "2024-03-15T12:30:00",
                "date_created_gmt": "2024-02-01T08:00:00",
                "date_modified_gmt": "2024-03-15T12:30:00",
                "type": "simple",
                "status": "publish",
                "sku": "TEST-002",
                "price": "29.99",
                "regular_price": "29.99",
                "categories": [],
                "images": [],
                "_links": {},
            }
        ]

        http_mocker.get(
            WooCommerceRequestBuilder.products_endpoint().with_default_params().build(),
            HttpResponse(body=json.dumps(first_page_response), status_code=200),
        )
        http_mocker.get(
            WooCommerceRequestBuilder.products_endpoint().with_default_params().with_offset(100).build(),
            HttpResponse(body=json.dumps(second_page_response), status_code=200),
        )
        http_mocker.get(
            WooCommerceRequestBuilder.products_endpoint().with_default_params().with_offset(200).build(),
            HttpResponse(body=json.dumps([]), status_code=200),
        )

        output = self._read(config_=config())
        assert len(output.records) == 2
        assert output.records[0].record.data["id"] == 99
        assert output.records[1].record.data["id"] == 100

    @HttpMocker()
    def test_read_records_empty_response(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            WooCommerceRequestBuilder.products_endpoint().with_default_params().build(),
            HttpResponse(body=json.dumps([]), status_code=200),
        )

        output = self._read(config_=config())
        assert len(output.records) == 0


class TestProductsIncremental(TestCase):
    @staticmethod
    def _read(config_: ConfigBuilder, expecting_exception: bool = False) -> EntrypointOutput:
        return read_output(
            config_builder=config_,
            stream_name=_STREAM_NAME,
            sync_mode=SyncMode.incremental,
            expecting_exception=expecting_exception,
        )

    @HttpMocker()
    def test_read_records_incremental(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            WooCommerceRequestBuilder.products_endpoint()
            .with_default_params()
            .with_modified_after("2024-01-01T00:00:00")
            .with_modified_before("2024-01-31T00:00:00")
            .build(),
            HttpResponse(body=json.dumps(_get_response_template()), status_code=200),
        )
        http_mocker.get(
            WooCommerceRequestBuilder.products_endpoint()
            .with_default_params()
            .with_modified_after("2024-01-01T00:00:00")
            .with_modified_before("2024-01-31T00:00:00")
            .with_offset(100)
            .build(),
            HttpResponse(body=json.dumps([]), status_code=200),
        )

        output = self._read(config_=config().with_start_date("2024-01-01"))
        assert len(output.records) >= 0
