# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

"""
Tests for the product_variations stream.

This stream is a substream of products. It fetches variations for each product.
The path is /products/{product_id}/variations.
"""

import json
from pathlib import Path
from unittest import TestCase

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse

from .config import ConfigBuilder
from .request_builder import WooCommerceRequestBuilder
from .utils import config, read_output


_STREAM_NAME = "product_variations"


def _get_response_template() -> list:
    template_path = Path(__file__).parent.parent / "resource" / "http" / "response" / "product_variations.json"
    return json.loads(template_path.read_text())


def _get_products_response_template() -> list:
    template_path = Path(__file__).parent.parent / "resource" / "http" / "response" / "products.json"
    return json.loads(template_path.read_text())


class TestProductVariationsFullRefresh(TestCase):
    """
    Tests for the product_variations stream in full refresh mode.

    The product_variations stream is a substream of products.
    It uses SubstreamPartitionRouter to fetch variations for each product.
    """

    @staticmethod
    def _read(config_: ConfigBuilder, expecting_exception: bool = False) -> EntrypointOutput:
        return read_output(
            config_builder=config_,
            stream_name=_STREAM_NAME,
            sync_mode=SyncMode.full_refresh,
            expecting_exception=expecting_exception,
        )

    @HttpMocker()
    @freezegun.freeze_time("2024-01-15T12:00:00Z")
    def test_read_records_single_parent(self, http_mocker: HttpMocker) -> None:
        """Test reading product variations for a single parent product."""
        products_response = _get_products_response_template()
        product_id = products_response[0]["id"]

        http_mocker.get(
            WooCommerceRequestBuilder.products_endpoint()
            .with_default_params()
            .with_modified_after("2024-01-01T00:00:00")
            .with_modified_before("2024-01-15T12:00:00")
            .build(),
            HttpResponse(body=json.dumps(products_response), status_code=200),
        )
        http_mocker.get(
            WooCommerceRequestBuilder.product_variations_endpoint(product_id).with_default_params().build(),
            HttpResponse(body=json.dumps(_get_response_template()), status_code=200),
        )

        output = self._read(config_=config().with_start_date("2024-01-01"))
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 101
        assert output.records[0].record.data["sku"] == "TEST-001-RED"

    @HttpMocker()
    @freezegun.freeze_time("2024-01-15T12:00:00Z")
    def test_read_records_multiple_parents(self, http_mocker: HttpMocker) -> None:
        """
        Test reading product variations for multiple parent products.

        This tests the substream behavior with at least 2 parent records.
        """
        products_template = _get_products_response_template()[0]
        products_response = [
            {**products_template, "id": 99},
            {**products_template, "id": 100},
        ]

        variations_for_99 = [
            {
                "id": 101,
                "sku": "PROD-99-VAR-1",
                "price": "49.99",
                "date_created_gmt": "2024-01-10T08:00:00",
                "date_modified_gmt": "2024-01-10T08:00:00",
            }
        ]
        variations_for_100 = [
            {
                "id": 102,
                "sku": "PROD-100-VAR-1",
                "price": "59.99",
                "date_created_gmt": "2024-01-10T08:00:00",
                "date_modified_gmt": "2024-01-10T08:00:00",
            }
        ]

        http_mocker.get(
            WooCommerceRequestBuilder.products_endpoint()
            .with_default_params()
            .with_modified_after("2024-01-01T00:00:00")
            .with_modified_before("2024-01-15T12:00:00")
            .build(),
            HttpResponse(body=json.dumps(products_response), status_code=200),
        )
        http_mocker.get(
            WooCommerceRequestBuilder.product_variations_endpoint(99).with_default_params().build(),
            HttpResponse(body=json.dumps(variations_for_99), status_code=200),
        )
        http_mocker.get(
            WooCommerceRequestBuilder.product_variations_endpoint(100).with_default_params().build(),
            HttpResponse(body=json.dumps(variations_for_100), status_code=200),
        )

        output = self._read(config_=config().with_start_date("2024-01-01"))
        assert len(output.records) == 2
        skus = [r.record.data["sku"] for r in output.records]
        assert "PROD-99-VAR-1" in skus
        assert "PROD-100-VAR-1" in skus

    @HttpMocker()
    @freezegun.freeze_time("2024-01-15T12:00:00Z")
    def test_read_records_empty_parent(self, http_mocker: HttpMocker) -> None:
        """Test reading when there are no parent products."""
        http_mocker.get(
            WooCommerceRequestBuilder.products_endpoint()
            .with_default_params()
            .with_modified_after("2024-01-01T00:00:00")
            .with_modified_before("2024-01-15T12:00:00")
            .build(),
            HttpResponse(body=json.dumps([]), status_code=200),
        )

        output = self._read(config_=config().with_start_date("2024-01-01"))
        assert len(output.records) == 0

    @HttpMocker()
    @freezegun.freeze_time("2024-01-15T12:00:00Z")
    def test_read_records_empty_variations(self, http_mocker: HttpMocker) -> None:
        """Test reading when parent product has no variations."""
        products_response = _get_products_response_template()
        product_id = products_response[0]["id"]

        http_mocker.get(
            WooCommerceRequestBuilder.products_endpoint()
            .with_default_params()
            .with_modified_after("2024-01-01T00:00:00")
            .with_modified_before("2024-01-15T12:00:00")
            .build(),
            HttpResponse(body=json.dumps(products_response), status_code=200),
        )
        http_mocker.get(
            WooCommerceRequestBuilder.product_variations_endpoint(product_id).with_default_params().build(),
            HttpResponse(body=json.dumps([]), status_code=200),
        )

        output = self._read(config_=config().with_start_date("2024-01-01"))
        assert len(output.records) == 0

    @HttpMocker()
    @freezegun.freeze_time("2024-01-15T12:00:00Z")
    def test_read_records_pagination(self, http_mocker: HttpMocker) -> None:
        """
        Test pagination for product variations.

        The connector uses OffsetIncrement pagination with page_size=100.
        """
        products_response = _get_products_response_template()
        product_id = products_response[0]["id"]

        variations_template = {
            "id": 1,
            "sku": "VAR",
            "price": "49.99",
            "date_created_gmt": "2024-01-10T08:00:00",
            "date_modified_gmt": "2024-01-10T08:00:00",
        }

        page1_variations = []
        for i in range(100):
            var = variations_template.copy()
            var["id"] = i + 1
            page1_variations.append(var)

        page2_variations = []
        for i in range(50):
            var = variations_template.copy()
            var["id"] = 101 + i
            page2_variations.append(var)

        http_mocker.get(
            WooCommerceRequestBuilder.products_endpoint()
            .with_default_params()
            .with_modified_after("2024-01-01T00:00:00")
            .with_modified_before("2024-01-15T12:00:00")
            .build(),
            HttpResponse(body=json.dumps(products_response), status_code=200),
        )
        http_mocker.get(
            WooCommerceRequestBuilder.product_variations_endpoint(product_id).with_default_params().build(),
            HttpResponse(body=json.dumps(page1_variations), status_code=200),
        )
        http_mocker.get(
            WooCommerceRequestBuilder.product_variations_endpoint(product_id).with_default_params().with_offset(100).build(),
            HttpResponse(body=json.dumps(page2_variations), status_code=200),
        )

        output = self._read(config_=config().with_start_date("2024-01-01"))
        assert len(output.records) == 150
