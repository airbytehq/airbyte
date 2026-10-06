# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

"""
Tests for the shipping_zones stream.

This is a simple full refresh stream without incremental sync.
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


_STREAM_NAME = "shipping_zones"


def _get_response_template() -> list:
    template_path = Path(__file__).parent.parent / "resource" / "http" / "response" / "shipping_zones.json"
    return json.loads(template_path.read_text())


class TestShippingZonesFullRefresh(TestCase):
    """Tests for the shipping_zones stream in full refresh mode."""

    @staticmethod
    def _read(config_: ConfigBuilder, expecting_exception: bool = False) -> EntrypointOutput:
        return read_output(
            config_builder=config_,
            stream_name=_STREAM_NAME,
            sync_mode=SyncMode.full_refresh,
            expecting_exception=expecting_exception,
        )

    @HttpMocker()
    def test_read_records(self, http_mocker: HttpMocker) -> None:
        """Test reading shipping zones."""
        http_mocker.get(
            WooCommerceRequestBuilder.shipping_zones_endpoint().with_default_params().build(),
            HttpResponse(body=json.dumps(_get_response_template()), status_code=200),
        )

        output = self._read(config_=config())
        assert len(output.records) == 2
        assert output.records[0].record.data["id"] == 0
        assert output.records[1].record.data["id"] == 1
        assert output.records[1].record.data["name"] == "US"

    @HttpMocker()
    def test_read_records_empty_response(self, http_mocker: HttpMocker) -> None:
        """Test reading when there are no shipping zones."""
        http_mocker.get(
            WooCommerceRequestBuilder.shipping_zones_endpoint().with_default_params().build(),
            HttpResponse(body=json.dumps([]), status_code=200),
        )

        output = self._read(config_=config())
        assert len(output.records) == 0
