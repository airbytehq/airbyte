# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from unittest import TestCase

import freezegun

from airbyte_cdk.test.mock_http import HttpMocker

from .request_builder import RequestBuilder
from .response_builder import (
    subscription_response,
    subscription_response_page1,
    subscription_response_page2,
)
from .utils import config, read_output


_STREAM_NAME = "subscription"


@freezegun.freeze_time("2024-01-15T12:00:00Z")
class TestSubscriptionStream(TestCase):
    """Tests for the subscription stream."""

    @HttpMocker()
    def test_read_records(self, http_mocker: HttpMocker) -> None:
        """Basic read test for subscription stream."""
        http_mocker.get(
            RequestBuilder.subscriptions_endpoint().with_any_query_params().build(),
            subscription_response(),
        )

        output = read_output(config_builder=config(), stream_name=_STREAM_NAME)
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "sub_001"

    @HttpMocker()
    def test_pagination_two_pages(self, http_mocker: HttpMocker) -> None:
        """Test pagination with 2 pages for subscription stream."""
        http_mocker.get(
            RequestBuilder.subscriptions_endpoint().with_any_query_params().build(),
            [
                subscription_response_page1(),
                subscription_response_page2(),
            ],
        )

        output = read_output(config_builder=config(), stream_name=_STREAM_NAME)
        assert len(output.records) == 2
