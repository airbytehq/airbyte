# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

"""
Tests for the coupons stream.

This stream uses server-side incremental sync with modified_after/modified_before
parameters and 30-day (P30D) date slicing.
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


_STREAM_NAME = "coupons"


def _get_response_template() -> list:
    template_path = Path(__file__).parent.parent / "resource" / "http" / "response" / "coupons.json"
    return json.loads(template_path.read_text())


class TestCouponsFullRefresh(TestCase):
    """Tests for the coupons stream in full refresh mode."""

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
        """Test reading coupons in full refresh mode."""
        http_mocker.get(
            WooCommerceRequestBuilder.coupons_endpoint().with_default_params().build(),
            HttpResponse(body=json.dumps(_get_response_template()), status_code=200),
        )

        output = self._read(config_=config())
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 720
        assert output.records[0].record.data["code"] == "summer2024"

    @HttpMocker()
    def test_read_records_empty_response(self, http_mocker: HttpMocker) -> None:
        """Test reading when there are no coupons."""
        http_mocker.get(
            WooCommerceRequestBuilder.coupons_endpoint().with_default_params().build(),
            HttpResponse(body=json.dumps([]), status_code=200),
        )

        output = self._read(config_=config())
        assert len(output.records) == 0


class TestCouponsIncremental(TestCase):
    """Tests for the coupons stream in incremental mode."""

    @staticmethod
    def _read(config_: ConfigBuilder, expecting_exception: bool = False) -> EntrypointOutput:
        return read_output(
            config_builder=config_,
            stream_name=_STREAM_NAME,
            sync_mode=SyncMode.incremental,
            expecting_exception=expecting_exception,
        )

    @HttpMocker()
    @freezegun.freeze_time("2024-01-15T12:00:00Z")
    def test_read_records_single_slice(self, http_mocker: HttpMocker) -> None:
        """Test reading coupons with a single date slice."""
        http_mocker.get(
            WooCommerceRequestBuilder.coupons_endpoint()
            .with_default_params()
            .with_modified_after("2024-01-01T00:00:00")
            .with_modified_before("2024-01-15T12:00:00")
            .build(),
            HttpResponse(body=json.dumps(_get_response_template()), status_code=200),
        )

        output = self._read(config_=config().with_start_date("2024-01-01"))

        # Assert on record content
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 720
        assert output.records[0].record.data["code"] == "summer2024"

        # Assert on state - should be updated with the timestamp of the latest record
        assert len(output.state_messages) > 0
        latest_state = output.state_messages[-1].state.stream.stream_state
        assert (
            latest_state.__dict__["date_modified_gmt"] == "2024-01-10T10:30:00"
        ), "State should be updated to the date_modified_gmt timestamp of the latest record"

    @HttpMocker()
    @freezegun.freeze_time("2024-01-15T12:00:00Z")
    def test_read_records_empty_response(self, http_mocker: HttpMocker) -> None:
        """Test reading when there are no coupons in the date range."""
        http_mocker.get(
            WooCommerceRequestBuilder.coupons_endpoint()
            .with_default_params()
            .with_modified_after("2024-01-01T00:00:00")
            .with_modified_before("2024-01-15T12:00:00")
            .build(),
            HttpResponse(body=json.dumps([]), status_code=200),
        )

        output = self._read(config_=config().with_start_date("2024-01-01"))
        assert len(output.records) == 0
