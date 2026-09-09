#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#
import json
import logging
import re

import pytest
import yaml
from conftest import _YAML_FILE_PATH, get_source

from airbyte_cdk.models import SyncMode, Type
from airbyte_cdk.test.catalog_builder import CatalogBuilder


DEFAULT_START_DATE = "2010-01-01T00:00:00Z"


def _spec_start_date_property():
    manifest = yaml.safe_load(_YAML_FILE_PATH.read_text())
    return manifest["spec"]["connection_specification"]["properties"]["replication_start_date"]


def test_replication_start_date_is_optional_with_default():
    manifest = yaml.safe_load(_YAML_FILE_PATH.read_text())
    spec = manifest["spec"]["connection_specification"]
    assert spec["required"] == ["api_token"]
    assert spec["properties"]["replication_start_date"]["default"] == DEFAULT_START_DATE


@pytest.mark.parametrize(
    "value, expected",
    [
        ("2017-01-25T00:00:00Z", True),
        ("2017-01-25 00:00:00Z", True),
        ("2017-01-25", True),
        ("2017/01/25", False),
        ("25-01-2017", False),
    ],
)
def test_replication_start_date_pattern(value, expected):
    pattern = _spec_start_date_property()["pattern"]
    assert bool(re.match(pattern, value)) is expected


def test_missing_start_date_falls_back_to_default(requests_mock):
    requests_mock.get(
        re.compile(r"https://api\.pipedrive\.com/v1/recents.*"),
        json={"data": [], "additional_data": {"pagination": {"next_start": None}}},
    )
    source = get_source({"api_token": "token"})
    catalog = CatalogBuilder().with_stream("deals", SyncMode.full_refresh).build()
    list(source.read(logging.getLogger("airbyte"), source._config, catalog))
    assert requests_mock.last_request.qs["since_timestamp"] == ["2010-01-01 00:00:00"]


def test_legacy_authorization_config_is_migrated(capsys):
    source = get_source({"authorization": {"auth_type": "Token", "api_token": "legacy-token"}})
    assert source._config["api_token"] == "legacy-token"
    control_messages = [json.loads(line) for line in capsys.readouterr().out.splitlines() if '"CONTROL"' in line]
    assert len(control_messages) == 1
    assert control_messages[0]["type"] == Type.CONTROL.value
    assert control_messages[0]["control"]["connectorConfig"]["config"]["api_token"] == "legacy-token"


def test_current_config_is_not_migrated(capsys):
    source = get_source({"api_token": "current-token", "replication_start_date": "2017-01-25T00:00:00Z"})
    assert source._config["api_token"] == "current-token"
    assert "CONTROL" not in capsys.readouterr().out
