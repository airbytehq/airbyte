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


_STREAM_NAME = "product_categories"


def _get_response_template() -> list:
    template_path = Path(__file__).parent.parent / "resource" / "http" / "response" / "product_categories.json"
    return json.loads(template_path.read_text())


class TestProductCategoriesFullRefresh(TestCase):
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
            WooCommerceRequestBuilder.product_categories_endpoint().with_default_params().build(),
            HttpResponse(body=json.dumps(_get_response_template()), status_code=200),
        )

        output = self._read(config_=config())
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 15
        assert output.records[0].record.data["name"] == "Electronics"
        assert output.records[0].record.data["slug"] == "electronics"

    @HttpMocker()
    def test_read_records_with_pagination(self, http_mocker: HttpMocker) -> None:
        first_page_response = _get_response_template()
        second_page_response = [
            {
                "id": 16,
                "name": "Clothing",
                "slug": "clothing",
                "parent": 0,
                "description": "Clothing and apparel",
                "display": "default",
                "image": None,
                "menu_order": 1,
                "count": 50,
                "_links": {},
            }
        ]

        http_mocker.get(
            WooCommerceRequestBuilder.product_categories_endpoint().with_default_params().build(),
            HttpResponse(body=json.dumps(first_page_response), status_code=200),
        )
        http_mocker.get(
            WooCommerceRequestBuilder.product_categories_endpoint().with_default_params().with_offset(100).build(),
            HttpResponse(body=json.dumps(second_page_response), status_code=200),
        )
        http_mocker.get(
            WooCommerceRequestBuilder.product_categories_endpoint().with_default_params().with_offset(200).build(),
            HttpResponse(body=json.dumps([]), status_code=200),
        )

        output = self._read(config_=config())
        assert len(output.records) == 2
        assert output.records[0].record.data["id"] == 15
        assert output.records[1].record.data["id"] == 16

    @HttpMocker()
    def test_read_records_empty_response(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            WooCommerceRequestBuilder.product_categories_endpoint().with_default_params().build(),
            HttpResponse(body=json.dumps([]), status_code=200),
        )

        output = self._read(config_=config())
        assert len(output.records) == 0
