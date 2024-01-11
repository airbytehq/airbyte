#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, Dict

import pytest


@pytest.fixture
def report_init_kwargs() -> Dict[str, Any]:
    return {
        "url_base": "https://test.url",
        "replication_start_date": "2022-09-01T00:00:00Z",
        "marketplace_id": "market",
        "period_in_days": 90,
        "report_options": None,
        "replication_end_date": None,
    }
