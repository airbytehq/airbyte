# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from http import HTTPStatus
from unittest import TestCase
from unittest.mock import patch

import freezegun

from airbyte_cdk.test.mock_http import HttpMocker

from .request_builder import RequestBuilder
from .response_builder import (
    configuration_incompatible_response,
    customer_response,
    empty_response,
    error_response,
    quote_response,
    retry_after_response,
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
        assert output.errors == []
        assert output.is_in_logs("Stream is available only for Product Catalog 1.0")

    @HttpMocker()
    def test_contact_configuration_incompatible_ignored(self, http_mocker: HttpMocker) -> None:
        """Test configuration_incompatible error is ignored for contact."""
        http_mocker.get(
            RequestBuilder.customers_endpoint().with_any_query_params().build(),
            customer_response(),
        )
        http_mocker.get(
            RequestBuilder.customer_contacts_endpoint("cust_001").with_any_query_params().build(),
            configuration_incompatible_response(),
        )

        output = read_output(config_builder=config(), stream_name="contact")
        assert output.records == []
        assert output.errors == []
        assert output.is_in_logs("Stream is available only for Product Catalog 1.0")

    @HttpMocker()
    def test_subscription_configuration_incompatible_ignored(self, http_mocker: HttpMocker) -> None:
        """Test configuration_incompatible error is ignored for subscription."""
        http_mocker.get(
            RequestBuilder.subscriptions_endpoint().with_any_query_params().build(),
            configuration_incompatible_response(),
        )

        output = read_output(config_builder=config(), stream_name="subscription")
        assert output.records == []
        assert output.errors == []
        assert output.is_in_logs("Stream is available only for Product Catalog 1.0")

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
        assert output.errors == []
        assert output.is_in_logs("Entity unavailable. Customer may have been deleted.")

    @HttpMocker()
    def test_subscription_404_ignored(self, http_mocker: HttpMocker) -> None:
        """Test 404 error is ignored for subscription."""
        http_mocker.get(
            RequestBuilder.subscriptions_endpoint().with_any_query_params().build(),
            error_response(HTTPStatus.NOT_FOUND),
        )

        output = read_output(config_builder=config(), stream_name="subscription")
        assert output.records == []
        assert output.errors == []
        assert output.is_in_logs("Entity unavailable. Subscription may have been deleted.")

    @HttpMocker()
    def test_quote_line_group_404_ignored(self, http_mocker: HttpMocker) -> None:
        """Test 404 error is ignored for quote_line_group."""
        http_mocker.get(
            RequestBuilder.quotes_endpoint().with_any_query_params().build(),
            quote_response(),
        )
        http_mocker.get(
            RequestBuilder.quote_line_groups_endpoint("quote_001").with_any_query_params().build(),
            error_response(HTTPStatus.NOT_FOUND),
        )

        output = read_output(config_builder=config(), stream_name="quote_line_group")
        assert output.records == []
        assert output.errors == []
        assert output.is_in_logs("Entity unavailable. Quote may have been deleted.")

    @HttpMocker()
    def test_customer_404_fails(self, http_mocker: HttpMocker) -> None:
        """Test a 404 on customer is not ignored by its error handler."""
        http_mocker.get(
            RequestBuilder.customers_endpoint().with_any_query_params().build(),
            error_response(HTTPStatus.NOT_FOUND),
        )

        output = read_output(config_builder=config(), stream_name="customer", expecting_exception=True)
        assert output.errors

    @HttpMocker()
    def test_retry_after_header_is_honored(self, http_mocker: HttpMocker) -> None:
        """Test Retry-After is used as the retry backoff."""
        http_mocker.get(
            RequestBuilder.customers_endpoint().with_any_query_params().build(),
            [retry_after_response(), customer_response()],
        )

        with patch("time.sleep") as sleep:
            output = read_output(config_builder=config(), stream_name="customer")

        assert len(output.records) == 1
        assert output.errors == []
        sleep.assert_any_call(2)

    @HttpMocker()
    def test_retries_up_to_ten_times(self, http_mocker: HttpMocker) -> None:
        """Test the shared handler retries 10 times before returning records."""
        http_mocker.get(
            RequestBuilder.customers_endpoint().with_any_query_params().build(),
            [retry_after_response() for _ in range(10)] + [customer_response()],
        )

        with patch("time.sleep"):
            output = read_output(config_builder=config(), stream_name="customer")

        assert len(output.records) == 1
        assert output.errors == []


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
