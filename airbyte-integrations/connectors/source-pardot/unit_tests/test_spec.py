# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging
from collections.abc import Mapping
from typing import Any

import pytest
from conftest import get_source
from mock_server.config import ConfigBuilder


@pytest.fixture(scope="module")
def properties() -> Mapping[str, Any]:
    spec = get_source(ConfigBuilder().build()).spec(logging.getLogger("airbyte"))
    return spec.connectionSpecification["properties"]


def test_api_host_lists_exactly_the_two_account_engagement_hosts(properties: Mapping[str, Any]) -> None:
    assert properties["pardot_api_host"]["enum"] == ["pi.pardot.com", "pi.demo.pardot.com"]
    assert properties["pardot_api_host"]["order"] == 7
