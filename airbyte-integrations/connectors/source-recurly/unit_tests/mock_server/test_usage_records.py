# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest

from .contracts import Parent, Partition, StreamCase
from .contracts import test_full_refresh as test_full_refresh


@pytest.fixture
def stream_case() -> StreamCase:
    subscriptions = [
        {
            "id": "sub1",
            "add_ons": [
                {"id": "subscription-addon1", "subscription_id": "sub1", "add_on": {"id": "addon1"}},
                {"id": "subscription-addon2", "subscription_id": "sub1", "add_on": {"id": "addon2"}},
            ],
        },
        {"id": "sub2", "add_ons": [{"id": "subscription-addon3", "subscription_id": "sub2", "add_on": {"id": "addon3"}}]},
        {"id": "empty-sub", "add_ons": []},
    ]
    return StreamCase(
        name="usage_records",
        path="",
        params={"billing_status": "all", "sort": "usage_timestamp", "order": "asc", "limit": "200"},
        parents=(Parent("subscriptions", {"sort": "updated_at", "order": "asc", "limit": "200"}, subscriptions),),
        partitions=tuple(
            Partition(f"subscriptions/{sub}/add_ons/{addon}/usage", {"subscription_id": sub, "add_on_id": addon})
            for sub, addon in (("sub1", "addon1"), ("sub1", "addon2"), ("sub2", "addon3"))
        ),
        record={
            "id": "usage1",
            "object": "usage",
            "merchant_tag": "meter-reading-1",
            "amount": 12.5,
            "usage_type": "price",
            "unit_amount": 0.5,
            "unit_amount_decimal": "0.5",
            "measured_unit_id": "unit1",
            "usage_timestamp": "2025-01-01T10:00:00Z",
            "recording_timestamp": "2025-01-01T11:00:00Z",
            "billed_at": "2025-01-02T00:00:00Z",
            "created_at": "2025-01-01T11:00:00Z",
            "updated_at": "2025-01-02T00:00:00Z",
        },
    )
