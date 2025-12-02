# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from unittest import TestCase

import freezegun

from airbyte_cdk.test.mock_http import HttpMocker

from .request_builder import RequestBuilder
from .response_builder import (
    contact_response,
    customer_response,
    customer_response_multiple,
)
from .utils import config, read_output


_STREAM_NAME = "contact"


@freezegun.freeze_time("2024-01-15T12:00:00Z")
class TestContactStream(TestCase):
    """Tests for the contact stream (substream of customer)."""

    @HttpMocker()
    def test_read_records(self, http_mocker: HttpMocker) -> None:
        """Basic read test for contact stream (substream of customer)."""
        http_mocker.get(
            RequestBuilder.customers_endpoint().with_any_query_params().build(),
            customer_response(),
        )
        http_mocker.get(
            RequestBuilder.customer_contacts_endpoint("cust_001").with_any_query_params().build(),
            contact_response(),
        )

        output = read_output(config_builder=config(), stream_name=_STREAM_NAME)
        assert len(output.records) >= 1
        assert output.records[0].record.data["id"] == "contact_001"

    @HttpMocker()
    def test_with_multiple_parents(self, http_mocker: HttpMocker) -> None:
        """Test contact substream with multiple parent customers."""
        http_mocker.get(
            RequestBuilder.customers_endpoint().with_any_query_params().build(),
            customer_response_multiple(),
        )
        http_mocker.get(
            RequestBuilder.customer_contacts_endpoint("cust_001").with_any_query_params().build(),
            contact_response(),
        )
        http_mocker.get(
            RequestBuilder.customer_contacts_endpoint("cust_002").with_any_query_params().build(),
            contact_response(),
        )

        output = read_output(config_builder=config(), stream_name=_STREAM_NAME)
        assert len(output.records) >= 2
