# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest

from .contracts import StreamCase
from .contracts import test_full_refresh as test_full_refresh


@pytest.fixture
def stream_case() -> StreamCase:
    return StreamCase(
        name="gift_cards",
        path="gift_cards",
        params={},
        record={
            "id": "gift1",
            "object": "gift_card",
            "gifter_account_id": "account1",
            "recipient_account_id": None,
            "redemption_code": "TEST-GIFT-123",
            "balance": 50.5,
            "unit_amount": 100,
            "currency": "USD",
            "product_code": "holiday-gift",
            "created_at": "2025-01-01T10:00:00Z",
            "updated_at": "2025-01-02T00:00:00Z",
            "redeemed_at": None,
        },
    )
