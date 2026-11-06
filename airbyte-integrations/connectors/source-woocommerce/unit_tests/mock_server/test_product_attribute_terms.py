# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

"""
Tests for the product_attribute_terms stream.

This stream is a substream of product_attributes. It fetches terms for each attribute.
The path is /products/attributes/{attribute_id}/terms.
"""

import json
from pathlib import Path
from unittest import TestCase

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse

from .config import ConfigBuilder
from .request_builder import WooCommerceRequestBuilder
from .utils import config, read_output


_STREAM_NAME = "product_attribute_terms"


def _get_response_template() -> list:
    template_path = Path(__file__).parent.parent / "resource" / "http" / "response" / "product_attribute_terms.json"
    return json.loads(template_path.read_text())


def _get_attributes_response_template() -> list:
    template_path = Path(__file__).parent.parent / "resource" / "http" / "response" / "product_attributes.json"
    return json.loads(template_path.read_text())


class TestProductAttributeTermsFullRefresh(TestCase):
    """
    Tests for the product_attribute_terms stream in full refresh mode.

    The product_attribute_terms stream is a substream of product_attributes.
    It uses SubstreamPartitionRouter to fetch terms for each attribute.
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
    def test_read_records_single_parent(self, http_mocker: HttpMocker) -> None:
        """Test reading attribute terms for a single parent attribute."""
        attributes_response = [_get_attributes_response_template()[0]]
        attribute_id = attributes_response[0]["id"]

        http_mocker.get(
            WooCommerceRequestBuilder.product_attributes_endpoint().with_default_params().build(),
            HttpResponse(body=json.dumps(attributes_response), status_code=200),
        )
        http_mocker.get(
            WooCommerceRequestBuilder.product_attribute_terms_endpoint(attribute_id).with_default_params().build(),
            HttpResponse(body=json.dumps(_get_response_template()), status_code=200),
        )

        output = self._read(config_=config())
        assert len(output.records) == 2
        assert output.records[0].record.data["id"] == 1
        assert output.records[0].record.data["name"] == "Red"

    @HttpMocker()
    def test_read_records_multiple_parents(self, http_mocker: HttpMocker) -> None:
        """
        Test reading attribute terms for multiple parent attributes.

        This tests the substream behavior with at least 2 parent records.
        """
        attributes_response = _get_attributes_response_template()

        terms_for_color = [
            {"id": 1, "name": "Red", "slug": "red", "description": "", "menu_order": 0, "count": 5},
            {"id": 2, "name": "Blue", "slug": "blue", "description": "", "menu_order": 1, "count": 3},
        ]
        terms_for_size = [
            {"id": 3, "name": "Small", "slug": "small", "description": "", "menu_order": 0, "count": 10},
            {"id": 4, "name": "Large", "slug": "large", "description": "", "menu_order": 1, "count": 8},
        ]

        http_mocker.get(
            WooCommerceRequestBuilder.product_attributes_endpoint().with_default_params().build(),
            HttpResponse(body=json.dumps(attributes_response), status_code=200),
        )
        http_mocker.get(
            WooCommerceRequestBuilder.product_attribute_terms_endpoint(1).with_default_params().build(),
            HttpResponse(body=json.dumps(terms_for_color), status_code=200),
        )
        http_mocker.get(
            WooCommerceRequestBuilder.product_attribute_terms_endpoint(2).with_default_params().build(),
            HttpResponse(body=json.dumps(terms_for_size), status_code=200),
        )

        output = self._read(config_=config())
        assert len(output.records) == 4
        names = [r.record.data["name"] for r in output.records]
        assert "Red" in names
        assert "Blue" in names
        assert "Small" in names
        assert "Large" in names

    @HttpMocker()
    def test_read_records_empty_parent(self, http_mocker: HttpMocker) -> None:
        """Test reading when there are no parent attributes."""
        http_mocker.get(
            WooCommerceRequestBuilder.product_attributes_endpoint().with_default_params().build(),
            HttpResponse(body=json.dumps([]), status_code=200),
        )

        output = self._read(config_=config())
        assert len(output.records) == 0

    @HttpMocker()
    def test_read_records_empty_terms(self, http_mocker: HttpMocker) -> None:
        """Test reading when parent attribute has no terms."""
        attributes_response = [_get_attributes_response_template()[0]]
        attribute_id = attributes_response[0]["id"]

        http_mocker.get(
            WooCommerceRequestBuilder.product_attributes_endpoint().with_default_params().build(),
            HttpResponse(body=json.dumps(attributes_response), status_code=200),
        )
        http_mocker.get(
            WooCommerceRequestBuilder.product_attribute_terms_endpoint(attribute_id).with_default_params().build(),
            HttpResponse(body=json.dumps([]), status_code=200),
        )

        output = self._read(config_=config())
        assert len(output.records) == 0

    @HttpMocker()
    def test_read_records_pagination(self, http_mocker: HttpMocker) -> None:
        """
        Test pagination for attribute terms.

        The connector uses OffsetIncrement pagination with page_size=100.
        """
        attributes_response = [_get_attributes_response_template()[0]]
        attribute_id = attributes_response[0]["id"]

        terms_template = {"id": 1, "name": "Term", "slug": "term", "description": "", "menu_order": 0, "count": 1}

        page1_terms = []
        for i in range(100):
            term = terms_template.copy()
            term["id"] = i + 1
            term["name"] = f"Term {i + 1}"
            page1_terms.append(term)

        page2_terms = []
        for i in range(50):
            term = terms_template.copy()
            term["id"] = 101 + i
            term["name"] = f"Term {101 + i}"
            page2_terms.append(term)

        http_mocker.get(
            WooCommerceRequestBuilder.product_attributes_endpoint().with_default_params().build(),
            HttpResponse(body=json.dumps(attributes_response), status_code=200),
        )
        http_mocker.get(
            WooCommerceRequestBuilder.product_attribute_terms_endpoint(attribute_id).with_default_params().build(),
            HttpResponse(body=json.dumps(page1_terms), status_code=200),
        )
        http_mocker.get(
            WooCommerceRequestBuilder.product_attribute_terms_endpoint(attribute_id).with_default_params().with_offset(100).build(),
            HttpResponse(body=json.dumps(page2_terms), status_code=200),
        )

        output = self._read(config_=config())
        assert len(output.records) == 150
