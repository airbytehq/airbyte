# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

"""
Tests for the shipping_zone_locations stream.

This stream is a substream of shipping_zones. It fetches locations for each zone.
The path is /shipping/zones/{zone_id}/locations.
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


_STREAM_NAME = "shipping_zone_locations"


def _get_response_template() -> list:
    template_path = Path(__file__).parent.parent / "resource" / "http" / "response" / "shipping_zone_locations.json"
    return json.loads(template_path.read_text())


def _get_zones_response_template() -> list:
    template_path = Path(__file__).parent.parent / "resource" / "http" / "response" / "shipping_zones.json"
    return json.loads(template_path.read_text())


class TestShippingZoneLocationsFullRefresh(TestCase):
    """
    Tests for the shipping_zone_locations stream in full refresh mode.

    The shipping_zone_locations stream is a substream of shipping_zones.
    It uses SubstreamPartitionRouter to fetch locations for each zone.
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
        """Test reading shipping zone locations for a single parent zone."""
        zones_response = [_get_zones_response_template()[0]]
        zone_id = zones_response[0]["id"]

        http_mocker.get(
            WooCommerceRequestBuilder.shipping_zones_endpoint().with_default_params().build(),
            HttpResponse(body=json.dumps(zones_response), status_code=200),
        )
        http_mocker.get(
            WooCommerceRequestBuilder.shipping_zone_locations_endpoint(zone_id).with_default_params().build(),
            HttpResponse(body=json.dumps(_get_response_template()), status_code=200),
        )

        output = self._read(config_=config())
        assert len(output.records) == 2
        assert output.records[0].record.data["code"] == "US"
        assert output.records[0].record.data["type"] == "country"

    @HttpMocker()
    def test_read_records_multiple_parents(self, http_mocker: HttpMocker) -> None:
        """
        Test reading shipping zone locations for multiple parent zones.

        This tests the substream behavior with at least 2 parent records.
        """
        zones_response = _get_zones_response_template()

        locations_for_zone_0 = [{"code": "WORLD", "type": "continent"}]
        locations_for_zone_1 = [
            {"code": "US", "type": "country"},
            {"code": "US:CA", "type": "state"},
        ]

        http_mocker.get(
            WooCommerceRequestBuilder.shipping_zones_endpoint().with_default_params().build(),
            HttpResponse(body=json.dumps(zones_response), status_code=200),
        )
        http_mocker.get(
            WooCommerceRequestBuilder.shipping_zone_locations_endpoint(0).with_default_params().build(),
            HttpResponse(body=json.dumps(locations_for_zone_0), status_code=200),
        )
        http_mocker.get(
            WooCommerceRequestBuilder.shipping_zone_locations_endpoint(1).with_default_params().build(),
            HttpResponse(body=json.dumps(locations_for_zone_1), status_code=200),
        )

        output = self._read(config_=config())
        assert len(output.records) == 3
        codes = [r.record.data["code"] for r in output.records]
        assert "WORLD" in codes
        assert "US" in codes
        assert "US:CA" in codes

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
    def test_read_records_empty_locations(self, http_mocker: HttpMocker) -> None:
        """Test reading when parent zone has no locations."""
        zones_response = [_get_zones_response_template()[0]]
        zone_id = zones_response[0]["id"]

        http_mocker.get(
            WooCommerceRequestBuilder.shipping_zones_endpoint().with_default_params().build(),
            HttpResponse(body=json.dumps(zones_response), status_code=200),
        )
        http_mocker.get(
            WooCommerceRequestBuilder.shipping_zone_locations_endpoint(zone_id).with_default_params().build(),
            HttpResponse(body=json.dumps([]), status_code=200),
        )

        output = self._read(config_=config())
        assert len(output.records) == 0

    @HttpMocker()
    def test_read_records_pagination(self, http_mocker: HttpMocker) -> None:
        """
        Test pagination for shipping zone locations.

        The connector uses OffsetIncrement pagination with page_size=100.
        """
        zones_response = [_get_zones_response_template()[1]]
        zone_id = zones_response[0]["id"]

        locations_template = {"code": "US", "type": "country"}

        page1_locations = []
        for i in range(100):
            loc = locations_template.copy()
            loc["code"] = f"LOC_{i + 1}"
            page1_locations.append(loc)

        page2_locations = []
        for i in range(50):
            loc = locations_template.copy()
            loc["code"] = f"LOC_{101 + i}"
            page2_locations.append(loc)

        http_mocker.get(
            WooCommerceRequestBuilder.shipping_zones_endpoint().with_default_params().build(),
            HttpResponse(body=json.dumps(zones_response), status_code=200),
        )
        http_mocker.get(
            WooCommerceRequestBuilder.shipping_zone_locations_endpoint(zone_id).with_default_params().build(),
            HttpResponse(body=json.dumps(page1_locations), status_code=200),
        )
        http_mocker.get(
            WooCommerceRequestBuilder.shipping_zone_locations_endpoint(zone_id).with_default_params().with_offset(100).build(),
            HttpResponse(body=json.dumps(page2_locations), status_code=200),
        )

        output = self._read(config_=config())
        assert len(output.records) == 150
