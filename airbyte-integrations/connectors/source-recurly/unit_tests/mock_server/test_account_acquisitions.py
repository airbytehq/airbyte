# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest

from .contracts import StreamCase, dated_params
from .contracts import test_full_refresh as test_full_refresh
from .contracts import test_incremental_resume as test_incremental_resume


@pytest.fixture
def stream_case() -> StreamCase:
    return StreamCase(
        name="account_acquisitions",
        path="acquisitions",
        params=dated_params(),
        record={
            "id": "acquisition1",
            "object": "account_acquisition",
            "account": {"id": "account1", "code": "customer-1"},
            "cost": {"currency": "USD", "amount": 20.5},
            "channel": "paid_search",
            "subchannel": "search",
            "campaign": "winter",
            "acquired_at": "2025-01-01T10:00:00Z",
            "created_at": "2025-01-01T10:00:00Z",
            "updated_at": "2025-01-02T00:00:00Z",
        },
    )
