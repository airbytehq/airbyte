# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest

from .contracts import Parent, Partition, StreamCase
from .contracts import test_full_refresh as test_full_refresh


@pytest.fixture
def stream_case() -> StreamCase:
    return StreamCase(
        name="external_subscription_payment_phases",
        path="",
        params={"sort": "updated_at", "order": "asc", "limit": "200"},
        parents=(Parent("external_subscriptions", {"sort": "updated_at"}, [{"id": "external1"}, {"id": "external2"}]),),
        partitions=tuple(
            Partition(f"external_subscriptions/{parent}/external_payment_phases", {"external_subscription_id": parent})
            for parent in ("external1", "external2")
        ),
        record={
            "id": "phase1",
            "object": "external_payment_phase",
            "started_at": "2025-01-01T00:00:00Z",
            "ends_at": "2025-02-01T00:00:00Z",
            "starting_billing_period_index": 1,
            "ending_billing_period_index": 2,
            "offer_type": "FREE_TRIAL",
            "period_count": 1,
            "period_length": "P1M",
            "amount": "9.99",
            "currency": "USD",
            "created_at": "2025-01-01T10:00:00Z",
            "updated_at": "2025-01-02T00:00:00Z",
        },
    )
