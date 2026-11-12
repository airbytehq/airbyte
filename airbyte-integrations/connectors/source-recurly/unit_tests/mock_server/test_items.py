# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest

from .contracts import StreamCase, dated_params
from .contracts import test_full_refresh as test_full_refresh
from .contracts import test_incremental_resume as test_incremental_resume


@pytest.fixture
def stream_case() -> StreamCase:
    return StreamCase(
        name="items",
        path="items",
        params=dated_params(),
        record={
            "id": "item1",
            "object": "item",
            "code": "support-hours",
            "state": "active",
            "name": "Support hours",
            "description": "Hourly support",
            "tax_exempt": False,
            "currencies": [{"currency": "USD", "unit_amount": 25.5}],
            "created_at": "2025-01-01T10:00:00Z",
            "updated_at": "2025-01-02T00:00:00Z",
            "deleted_at": None,
        },
    )
