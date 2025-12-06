# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from unittest import TestCase

import freezegun

from airbyte_cdk.test.mock_http import HttpMocker

from .request_builder import RequestBuilder
from .response_builder import coupon_response
from .utils import config, read_output


_STREAM_NAME = "coupon"


@freezegun.freeze_time("2024-01-15T12:00:00Z")
class TestCouponStream(TestCase):
    """Tests for the coupon stream."""

    @HttpMocker()
    def test_read_records(self, http_mocker: HttpMocker) -> None:
        """Basic read test for coupon stream."""
        http_mocker.get(
            RequestBuilder.coupons_endpoint().with_any_query_params().build(),
            coupon_response(),
        )

        output = read_output(config_builder=config(), stream_name=_STREAM_NAME)
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "coupon_001"
