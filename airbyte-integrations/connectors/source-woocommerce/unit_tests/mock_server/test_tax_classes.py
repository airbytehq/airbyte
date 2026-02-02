# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

"""
Tests for the tax_classes stream.

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


_STREAM_NAME = "tax_classes"


def _get_response_template() -> list:
    template_path = Path(__file__).parent.parent / "resource" / "http" / "response" / "tax_classes.json"
    return json.loads(template_path.read_text())


class TestTaxClassesFullRefresh(TestCase):
    """Tests for the tax_classes stream in full refresh mode."""

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
        """Test reading tax classes."""
        http_mocker.get(
            WooCommerceRequestBuilder.tax_classes_endpoint().with_default_params().build(),
            HttpResponse(body=json.dumps(_get_response_template()), status_code=200),
        )

        output = self._read(config_=config())
        assert len(output.records) == 3
        assert output.records[0].record.data["slug"] == "standard"
        assert output.records[1].record.data["slug"] == "reduced-rate"
        assert output.records[2].record.data["slug"] == "zero-rate"

    @HttpMocker()
    def test_read_records_empty_response(self, http_mocker: HttpMocker) -> None:
        """Test reading when there are no tax classes."""
        http_mocker.get(
            WooCommerceRequestBuilder.tax_classes_endpoint().with_default_params().build(),
            HttpResponse(body=json.dumps([]), status_code=200),
        )

        output = self._read(config_=config())
        assert len(output.records) == 0
