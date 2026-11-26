# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import logging
from collections.abc import Mapping
from itertools import product
from typing import Any
from urllib.parse import urlsplit

import pytest
from conftest import ALLOWED_HOSTS, get_source, resolved_manifest
from mock_server.config import ConfigBuilder

from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.models.declarative_component_schema import ConcurrencyLevel as ConcurrencyLevelModel
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory


@pytest.fixture(scope="module")
def properties() -> Mapping[str, Any]:
    spec = get_source(ConfigBuilder().build()).spec(logging.getLogger("airbyte"))
    return spec.connectionSpecification["properties"]


def test_api_host_lists_exactly_the_two_account_engagement_hosts(properties: Mapping[str, Any]) -> None:
    assert properties["pardot_api_host"]["enum"] == ["pi.pardot.com", "pi.demo.pardot.com"]
    assert properties["pardot_api_host"]["order"] == 7


def test_number_of_workers_is_two_to_five_and_three_by_default(properties: Mapping[str, Any]) -> None:
    num_workers = properties["num_workers"]

    assert (num_workers["type"], num_workers["default"], num_workers["minimum"], num_workers["maximum"]) == ("integer", 3, 2, 5)


def test_page_size_is_no_longer_in_the_spec(properties: Mapping[str, Any]) -> None:
    assert "v5_page_size" not in properties


def test_a_saved_config_loses_the_fields_that_no_longer_exist(capsys: pytest.CaptureFixture[str]) -> None:
    config = ConfigBuilder().build()
    capsys.readouterr()

    get_source({**config, "v5_page_size": 1000, "page_size": 1000, "split_up_interval": "day"})

    # The platform saves the config that the connector sends back in this message.
    messages = [json.loads(line) for line in capsys.readouterr().out.splitlines() if line.startswith("{")]
    saved = [message["control"]["connectorConfig"]["config"] for message in messages if message.get("type") == "CONTROL"]
    assert saved == [config]


@pytest.mark.parametrize(("num_workers", "expected"), [(None, 3), (2, 2), (5, 5), (9, 5)])
def test_number_of_workers_follows_the_config(num_workers: int | None, expected: int) -> None:
    config = ConfigBuilder().build()
    if num_workers is not None:
        config["num_workers"] = num_workers
    concurrency_level = ModelToComponentFactory().create_component(
        ConcurrencyLevelModel, resolved_manifest()["concurrency_level"], config=config
    )

    assert concurrency_level.get_concurrency_level() == expected


def test_allowed_hosts_are_exactly_the_hosts_the_connector_can_call(properties: Mapping[str, Any]) -> None:
    base_requester = resolved_manifest()["definitions"]["base_requester"]
    templates = [base_requester["url_base"], base_requester["authenticator"]["token_refresh_endpoint"]]
    hosts = set()
    for is_sandbox, api_host in product([False, True], [None, *properties["pardot_api_host"]["enum"]]):
        config = {"is_sandbox": is_sandbox, **({"pardot_api_host": api_host} if api_host else {})}
        hosts |= {urlsplit(InterpolatedString.create(template, parameters={}).eval(config)).hostname for template in templates}

    assert hosts == ALLOWED_HOSTS
