# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

"""
Tests for the shipping_zone_methods stream.

This stream is a substream of shipping_zones. It fetches methods for each zone.
The path is /shipping/zones/{zone_id}/methods.
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


_STREAM_NAME = "shipping_zone_methods"


def _get_response_template() -> list:
    template_path = Path(__file__).parent.parent / "resource" / "http" / "response" / "shipping_zone_methods.json"
    return json.loads(template_path.read_text())


def _get_zones_response_template() -> list:
    template_path = Path(__file__).parent.parent / "resource" / "http" / "response" / "shipping_zones.json"
    return json.loads(template_path.read_text())


class TestShippingZoneMethodsFullRefresh(TestCase):
    """
    Tests for the shipping_zone_methods stream in full refresh mode.

    The shipping_zone_methods stream is a substream of shipping_zones.
    It uses SubstreamPartitionRouter to fetch methods for each zone.
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
        """Test reading shipping zone methods for a single parent zone."""
        zones_response = [_get_zones_response_template()[1]]
        zone_id = zones_response[0]["id"]

        http_mocker.get(
            WooCommerceRequestBuilder.shipping_zones_endpoint().with_default_params().build(),
            HttpResponse(body=json.dumps(zones_response), status_code=200),
        )
        http_mocker.get(
            WooCommerceRequestBuilder.shipping_zone_methods_endpoint(zone_id).with_default_params().build(),
            HttpResponse(body=json.dumps(_get_response_template()), status_code=200),
        )

        output = self._read(config_=config())
        assert len(output.records) == 1
        assert output.records[0].record.data["instance_id"] == 1
        assert output.records[0].record.data["method_id"] == "flat_rate"

    @HttpMocker()
    def test_read_records_multiple_parents(self, http_mocker: HttpMocker) -> None:
        """
        Test reading shipping zone methods for multiple parent zones.

        This tests the substream behavior with at least 2 parent records.
        """
        zones_response = _get_zones_response_template()

        methods_for_zone_0 = [{"instance_id": 1, "method_id": "free_shipping", "title": "Free Shipping", "enabled": True}]
        methods_for_zone_1 = [
            {"instance_id": 2, "method_id": "flat_rate", "title": "Flat Rate", "enabled": True},
            {"instance_id": 3, "method_id": "local_pickup", "title": "Local Pickup", "enabled": True},
        ]

        http_mocker.get(
            WooCommerceRequestBuilder.shipping_zones_endpoint().with_default_params().build(),
            HttpResponse(body=json.dumps(zones_response), status_code=200),
        )
        http_mocker.get(
            WooCommerceRequestBuilder.shipping_zone_methods_endpoint(0).with_default_params().build(),
            HttpResponse(body=json.dumps(methods_for_zone_0), status_code=200),
        )
        http_mocker.get(
            WooCommerceRequestBuilder.shipping_zone_methods_endpoint(1).with_default_params().build(),
            HttpResponse(body=json.dumps(methods_for_zone_1), status_code=200),
        )

        output = self._read(config_=config())
        assert len(output.records) == 3
        method_ids = [r.record.data["method_id"] for r in output.records]
        assert "free_shipping" in method_ids
        assert "flat_rate" in method_ids
        assert "local_pickup" in method_ids

    @HttpMocker()
    def test_read_records_empty_parent(self, http_mocker: HttpMocker) -> None:
        """Test reading when there are no parent zones."""
        http_mocker.get(
            WooCommerceRequestBuilder.shipping_zones_endpoint().with_default_params().build(),
            HttpResponse(body=json.dumps([]), status_code=200),
        )

        output = self._read(config_=config())
        assert len(output.records) == 0

    @HttpMocker()
    def test_read_records_empty_methods(self, http_mocker: HttpMocker) -> None:
        """Test reading when parent zone has no methods."""
        zones_response = [_get_zones_response_template()[1]]
        zone_id = zones_response[0]["id"]

        http_mocker.get(
            WooCommerceRequestBuilder.shipping_zones_endpoint().with_default_params().build(),
            HttpResponse(body=json.dumps(zones_response), status_code=200),
        )
        http_mocker.get(
            WooCommerceRequestBuilder.shipping_zone_methods_endpoint(zone_id).with_default_params().build(),
            HttpResponse(body=json.dumps([]), status_code=200),
        )

        output = self._read(config_=config())
        assert len(output.records) == 0

    @HttpMocker()
    def test_read_records_pagination(self, http_mocker: HttpMocker) -> None:
        """
        Test pagination for shipping zone methods.

        The connector uses OffsetIncrement pagination with page_size=100.
        """
        zones_response = [_get_zones_response_template()[1]]
        zone_id = zones_response[0]["id"]

        methods_template = {"instance_id": 1, "method_id": "flat_rate", "title": "Flat Rate", "enabled": True}

        page1_methods = []
        for i in range(100):
            method = methods_template.copy()
            method["instance_id"] = i + 1
            page1_methods.append(method)

        page2_methods = []
        for i in range(50):
            method = methods_template.copy()
            method["instance_id"] = 101 + i
            page2_methods.append(method)

        http_mocker.get(
            WooCommerceRequestBuilder.shipping_zones_endpoint().with_default_params().build(),
            HttpResponse(body=json.dumps(zones_response), status_code=200),
        )
        http_mocker.get(
            WooCommerceRequestBuilder.shipping_zone_methods_endpoint(zone_id).with_default_params().build(),
            HttpResponse(body=json.dumps(page1_methods), status_code=200),
        )
        http_mocker.get(
            WooCommerceRequestBuilder.shipping_zone_methods_endpoint(zone_id).with_default_params().with_offset(100).build(),
            HttpResponse(body=json.dumps(page2_methods), status_code=200),
        )

        output = self._read(config_=config())
        assert len(output.records) == 150
