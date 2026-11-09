# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest

from .contracts import StreamCase
from .contracts import test_full_refresh as test_full_refresh


@pytest.fixture
def stream_case() -> StreamCase:
    return StreamCase(
        name="external_subscriptions",
        path="external_subscriptions",
        params={"sort": "updated_at"},
        record={
            "id": "external1",
            "object": "external_subscription",
            "account": {"id": "account1", "code": "customer-1"},
            "external_id": "store-subscription-1",
            "app_identifier": "com.example.test",
            "quantity": 1,
            "state": "active",
            "auto_renew": True,
            "in_grace_period": False,
            "test": True,
            "external_payment_phases": [{"id": "phase1", "amount": "9.99", "currency": "USD"}],
            "created_at": "2025-01-01T10:00:00Z",
            "updated_at": "2025-01-02T00:00:00Z",
        },
    )
