# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import pytest
import requests_mock

from airbyte_cdk.test.utils.assertions import assert_good_read
from airbyte_cdk.test.utils.data import get_json_contents
from airbyte_protocol.models import SyncMode
from freezegun import freeze_time


from airbyte_cdk.test.utils.reading import read_records
from .common import common_params, config, source, endpoint_url


def modified_after() -> str:
    return "2017-01-01T00:00:00"


def modified_before() -> str:
    return "2017-01-30T23:59:59"


def date_range() -> str:
    # Create and encode date range
    return f"modified_after={modified_after()}&modified_before={modified_before()}".replace(":", "%3A")


def build_url(stream_name: str) -> str:
    return f"{endpoint_url(stream_name)}?{common_params()}&{date_range()}"


@freeze_time(modified_before())
@requests_mock.Mocker(kw="mock")
@pytest.mark.parametrize(
    "stream_name, json_response_file, num_records",
    [
        ("coupons", "coupons.json", 2),
        ("orders", "orders.json", 2),
        # ("customers", "customers.json", 2),
        ("products", "products.json", 2),
    ],
)
def test_read_simple_endpoints_successfully(stream_name, json_response_file, num_records, **kwargs) -> None:
    """Test basic read for  all streams that use date ranges and don't have parent streams."""

    # Register mock response
    kwargs["mock"].get(
        build_url(stream_name),
        text=get_json_contents(json_response_file, __file__)
    )

    # Read records
    output = read_records(source(), config(), stream_name, SyncMode.full_refresh)

    # Check read was successful
    assert_good_read(output, num_records)
