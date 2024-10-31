#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import os
from typing import Any, Dict

import pytest

os.environ["DEPLOYMENT_MODE"] = "testing"


@pytest.fixture
def init_kwargs() -> Dict[str, Any]:
    return {
        "url_base": "https://test.url",
        "replication_start_date": "2022-09-01T00:00:00Z",
        "marketplace_id": "market",
        "period_in_days": 90,
        "report_options": None,
        "replication_end_date": None,
    }


@pytest.fixture
def report_init_kwargs(init_kwargs) -> Dict[str, Any]:
    return {
        "stream_name": "GET_TEST_REPORT",
        **init_kwargs
    }


@pytest.fixture
def http_mocker() -> None:
    """This fixture is needed to pass http_mocker parameter from the @HttpMocker decorator to a test"""
