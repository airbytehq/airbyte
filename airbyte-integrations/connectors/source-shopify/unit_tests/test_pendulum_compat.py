#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import pytest
from freezegun import freeze_time
from source_shopify.shopify_graphql.bulk.tools import BulkTools
from source_shopify.streams.streams import Products, TransactionsGraphql


@pytest.mark.parametrize(
    "value,expected",
    [
        ("2024-01-01", "2024-01-01T00:00:00+00:00"),
        ("2024-01-01T00:00:00", "2024-01-01T00:00:00+00:00"),
        ("2024-01-01T00:00:00Z", "2024-01-01T00:00:00+00:00"),
        ("2024-01-01T05:00:00+05:00", "2024-01-01T05:00:00+05:00"),
        ("2024-01-01T00:00:00.123456Z", "2024-01-01T00:00:00.123456+00:00"),
        ("2023-01-01T15:00:00-07:00", "2023-01-01T15:00:00-07:00"),
    ],
)
def test_datetime_str_to_rfc3339(value, expected):
    assert BulkTools._datetime_str_to_rfc3339(value) == expected


@freeze_time("2024-01-01T00:10:00Z")
def test_job_elapsed_time_in_state_is_int(auth_config):
    manager = Products(auth_config).job_manager
    manager._job_created_at = "2024-01-01T00:00:00Z"

    elapsed_time = manager._job_elapsed_time_in_state

    assert elapsed_time == 600
    assert isinstance(elapsed_time, int)


def test_job_elapsed_time_in_state_without_creation_time_is_zero(auth_config):
    manager = Products(auth_config).job_manager

    assert manager._job_elapsed_time_in_state == 0


@freeze_time("2024-01-02T00:00:00Z")
def test_bulk_stream_slice_with_naive_start_date(auth_config):
    auth_config["start_date"] = "2024-01-01"
    stream = TransactionsGraphql(auth_config)
    stream.job_manager._job_size = 1000

    first_slice = next(stream.stream_slices())

    assert first_slice["start"] == "2024-01-01T00:00:00+00:00"
