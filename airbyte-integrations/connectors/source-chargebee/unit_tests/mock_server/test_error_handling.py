# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from http import HTTPStatus
from unittest import TestCase

import freezegun

from airbyte_cdk.test.mock_http import HttpMocker

from .request_builder import RequestBuilder
from .response_builder import (
    configuration_incompatible_response,
    customer_response,
    empty_response,
    error_response,
)
from .utils import config, read_output


@freezegun.freeze_time("2024-01-15T12:00:00Z")
class TestErrorHandling(TestCase):
    """Tests for error handling."""

    @HttpMocker()
    def test_error_configuration_incompatible_ignored(self, http_mocker: HttpMocker) -> None:
        """Test configuration_incompatible error is ignored as configured in manifest."""
        http_mocker.get(
            RequestBuilder.customers_endpoint().with_any_query_params().build(),
            configuration_incompatible_response(),
        )

        output = read_output(config_builder=config(), stream_name="customer")
        assert len(output.records) == 0

    @HttpMocker()
    def test_contact_404_ignored(self, http_mocker: HttpMocker) -> None:
        """Test 404 error is ignored for contact stream as configured in manifest."""
        http_mocker.get(
            RequestBuilder.customers_endpoint().with_any_query_params().build(),
            customer_response(),
        )
        http_mocker.get(
            RequestBuilder.customer_contacts_endpoint("cust_001").with_any_query_params().build(),
            error_response(HTTPStatus.NOT_FOUND),
        )

        output = read_output(config_builder=config(), stream_name="contact")
        assert len(output.records) == 0


@freezegun.freeze_time("2024-01-15T12:00:00Z")
class TestEmptyResponse(TestCase):
    """Tests for empty response handling."""

    @HttpMocker()
    def test_empty_response(self, http_mocker: HttpMocker) -> None:
        """Test handling of empty response."""
        http_mocker.get(
            RequestBuilder.customers_endpoint().with_any_query_params().build(),
            empty_response(),
        )

        output = read_output(config_builder=config(), stream_name="customer")
        assert len(output.records) == 0
