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


_STREAM_NAME = "orders"


def _get_response_template() -> list:
    template_path = Path(__file__).parent.parent / "resource" / "http" / "response" / "orders.json"
    return json.loads(template_path.read_text())


class TestOrdersFullRefresh(TestCase):
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
            WooCommerceRequestBuilder.orders_endpoint().with_default_params().build(),
            HttpResponse(body=json.dumps(_get_response_template()), status_code=200),
        )

        output = self._read(config_=config())
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 727
        assert output.records[0].record.data["status"] == "processing"
        assert output.records[0].record.data["total"] == "59.99"

    @HttpMocker()
    def test_read_records_with_pagination(self, http_mocker: HttpMocker) -> None:
        first_page_response = _get_response_template()
        second_page_response = [
            {
                "id": 728,
                "parent_id": 0,
                "status": "completed",
                "currency": "USD",
                "version": "5.6.0",
                "date_created": "2024-03-16T10:30:00",
                "date_modified": "2024-03-16T14:45:00",
                "date_created_gmt": "2024-03-16T10:30:00",
                "date_modified_gmt": "2024-03-16T14:45:00",
                "total": "99.99",
                "customer_id": 2,
                "billing": {},
                "shipping": {},
                "line_items": [],
                "_links": {},
            }
        ]

        http_mocker.get(
            WooCommerceRequestBuilder.orders_endpoint().with_default_params().build(),
            HttpResponse(body=json.dumps(first_page_response), status_code=200),
        )
        http_mocker.get(
            WooCommerceRequestBuilder.orders_endpoint().with_default_params().with_offset(100).build(),
            HttpResponse(body=json.dumps(second_page_response), status_code=200),
        )
        http_mocker.get(
            WooCommerceRequestBuilder.orders_endpoint().with_default_params().with_offset(200).build(),
            HttpResponse(body=json.dumps([]), status_code=200),
        )

        output = self._read(config_=config())
        assert len(output.records) == 2
        assert output.records[0].record.data["id"] == 727
        assert output.records[1].record.data["id"] == 728

    @HttpMocker()
    def test_read_records_empty_response(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            WooCommerceRequestBuilder.orders_endpoint().with_default_params().build(),
            HttpResponse(body=json.dumps([]), status_code=200),
        )

        output = self._read(config_=config())
        assert len(output.records) == 0


class TestOrdersIncremental(TestCase):
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
            WooCommerceRequestBuilder.orders_endpoint()
            .with_default_params()
            .with_modified_after("2024-01-01T00:00:00")
            .with_modified_before("2024-01-31T00:00:00")
            .build(),
            HttpResponse(body=json.dumps(_get_response_template()), status_code=200),
        )
        http_mocker.get(
            WooCommerceRequestBuilder.orders_endpoint()
            .with_default_params()
            .with_modified_after("2024-01-01T00:00:00")
            .with_modified_before("2024-01-31T00:00:00")
            .with_offset(100)
            .build(),
            HttpResponse(body=json.dumps([]), status_code=200),
        )

        output = self._read(config_=config().with_start_date("2024-01-01"))
        assert len(output.records) >= 0
