# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from unittest import TestCase

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker

from .request_builder import RequestBuilder
from .response_builder import invoice_response
from .utils import config, read_output


_STREAM_NAME = "invoice"


@freezegun.freeze_time("2024-01-15T12:00:00Z")
class TestInvoiceStream(TestCase):
    """Tests for the invoice stream."""

    @HttpMocker()
    def test_read_records(self, http_mocker: HttpMocker) -> None:
        """Basic read test for invoice stream."""
        http_mocker.get(
            RequestBuilder.invoices_endpoint().with_any_query_params().build(),
            invoice_response(),
        )

        output = read_output(config_builder=config(), stream_name=_STREAM_NAME)
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "inv_001"

    @HttpMocker()
    def test_incremental_emits_state(self, http_mocker: HttpMocker) -> None:
        """Test that incremental sync emits state message for invoice."""
        http_mocker.get(
            RequestBuilder.invoices_endpoint().with_any_query_params().build(),
            invoice_response(),
        )

        output = read_output(config_builder=config(), stream_name=_STREAM_NAME, sync_mode=SyncMode.incremental)
        assert len(output.records) >= 1
        assert len(output.state_messages) >= 1
