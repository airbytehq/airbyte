# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

"""
Tests for the system_status_tools stream.

This stream is a full refresh stream with OffsetIncrement pagination.
It is also used as the check stream for connection validation.
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


_STREAM_NAME = "system_status_tools"


def _get_response_template() -> list:
    template_path = Path(__file__).parent.parent / "resource" / "http" / "response" / "system_status_tools.json"
    return json.loads(template_path.read_text())


class TestSystemStatusToolsFullRefresh(TestCase):
    """
    Tests for the system_status_tools stream in full refresh mode.

    The system_status_tools stream is a full refresh stream with OffsetIncrement pagination.
    It is also used as the check stream for connection validation.
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
    def test_read_records_single_page(self, http_mocker: HttpMocker) -> None:
        """Test reading a single page of system status tools."""
        http_mocker.get(
            WooCommerceRequestBuilder.system_status_tools_endpoint().with_default_params().build(),
            HttpResponse(body=json.dumps(_get_response_template()), status_code=200),
        )

        output = self._read(config_=config())
        assert len(output.records) == 2
        assert output.records[0].record.data["id"] == "clear_transients"
        assert output.records[0].record.data["name"] == "WooCommerce transients"
        assert output.records[1].record.data["id"] == "clear_expired_transients"

    @HttpMocker()
    def test_read_records_empty_response(self, http_mocker: HttpMocker) -> None:
        """Test reading when there are no system status tools."""
        http_mocker.get(
            WooCommerceRequestBuilder.system_status_tools_endpoint().with_default_params().build(),
            HttpResponse(body=json.dumps([]), status_code=200),
        )

        output = self._read(config_=config())
        assert len(output.records) == 0

    @HttpMocker()
    def test_read_records_pagination(self, http_mocker: HttpMocker) -> None:
        """
        Test pagination with 2 pages.

        The connector uses OffsetIncrement pagination with page_size=100.
        It fetches the next page only if the current page returns exactly 100 records.
        """
        template = _get_response_template()[0]

        page1_records = []
        for i in range(100):
            record = template.copy()
            record["id"] = f"tool_{i + 1}"
            page1_records.append(record)

        page2_records = []
        for i in range(50):
            record = template.copy()
            record["id"] = f"tool_{101 + i}"
            page2_records.append(record)

        http_mocker.get(
            WooCommerceRequestBuilder.system_status_tools_endpoint().with_default_params().build(),
            HttpResponse(body=json.dumps(page1_records), status_code=200),
        )
        http_mocker.get(
            WooCommerceRequestBuilder.system_status_tools_endpoint().with_default_params().with_offset(100).build(),
            HttpResponse(body=json.dumps(page2_records), status_code=200),
        )

        output = self._read(config_=config())
        assert len(output.records) == 150
        assert output.records[0].record.data["id"] == "tool_1"
        assert output.records[99].record.data["id"] == "tool_100"
        assert output.records[100].record.data["id"] == "tool_101"
