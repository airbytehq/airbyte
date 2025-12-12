# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from unittest import TestCase

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder

from .request_builder import RequestBuilder
from .response_builder import (
    configuration_incompatible_response,
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
        assert len(output.records) == 1
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
        assert len(output.records) == 2

    @HttpMocker()
    def test_both_transformations(self, http_mocker: HttpMocker) -> None:
        """
        Test that BOTH transformations work together:
        1. AddFields adds customer_id from parent stream slice
        2. CustomFieldTransformation converts cf_* fields to custom_fields array
        """
        # Mock parent customer stream
        http_mocker.get(
            RequestBuilder.customers_endpoint().with_any_query_params().build(),
            customer_response(),
        )

        # Mock contact substream (with cf_ fields)
        http_mocker.get(
            RequestBuilder.customer_contacts_endpoint("cust_001").with_any_query_params().build(),
            contact_response(),
        )

        output = read_output(config_builder=config(), stream_name=_STREAM_NAME)

        assert len(output.records) == 1
        record_data = output.records[0].record.data

        # ========== Test Transformation #1: AddFields ==========
        assert "customer_id" in record_data, "AddFields transformation should add customer_id field"
        assert record_data["customer_id"] == "cust_001", "customer_id should match parent stream's id"

        # ========== Test Transformation #2: CustomFieldTransformation ==========
        assert not any(key.startswith("cf_") for key in record_data.keys()), "cf_ fields should be removed from top level"
        assert "custom_fields" in record_data
        assert isinstance(record_data["custom_fields"], list)
        assert len(record_data["custom_fields"]) == 2

        custom_fields = {cf["name"]: cf["value"] for cf in record_data["custom_fields"]}
        assert len(custom_fields) == 2

    @HttpMocker()
    def test_error_configuration_incompatible_ignored(self, http_mocker: HttpMocker) -> None:
        """Test configuration_incompatible error is ignored for contact stream as configured in manifest."""
        # Mock parent stream (customer) to return successfully
        http_mocker.get(
            RequestBuilder.customers_endpoint().with_any_query_params().build(),
            customer_response(),
        )

        # Mock contact substream to return CONFIG_INCOMPATIBLE
        http_mocker.get(
            RequestBuilder.customer_contacts_endpoint("cust_001").with_any_query_params().build(),
            configuration_incompatible_response(),
        )

        output = read_output(config_builder=config(), stream_name=_STREAM_NAME)

        # Verify no records returned (error was ignored)
        assert len(output.records) == 0

        # Verify error message from manifest is logged
        assert output.is_in_logs("Stream is available only for Product Catalog 1.0")
