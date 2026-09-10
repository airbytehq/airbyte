#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#
import json
import re

import pytest
import yaml
from conftest import _YAML_FILE_PATH, get_source

from airbyte_cdk.models import FailureType, SyncMode, Type
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


DEFAULT_START_DATE = "2010-01-01T00:00:00Z"
_RECENTS_URL = re.compile(r"https://api\.pipedrive\.com/v1/recents.*")
_EMPTY_PAGE = {"data": [], "additional_data": {"pagination": {"next_start": None}}}


def _spec_start_date_property():
    manifest = yaml.safe_load(_YAML_FILE_PATH.read_text())
    return manifest["spec"]["connection_specification"]["properties"]["replication_start_date"]


def _read_deals(config):
    catalog = CatalogBuilder().with_stream("deals", SyncMode.full_refresh).build()
    return read(get_source(config), config, catalog)


def test_replication_start_date_is_optional_with_default():
    manifest = yaml.safe_load(_YAML_FILE_PATH.read_text())
    spec = manifest["spec"]["connection_specification"]
    assert spec["required"] == ["credentials"]
    assert spec["properties"]["replication_start_date"]["default"] == DEFAULT_START_DATE


@pytest.mark.parametrize(
    "value, expected",
    [
        ("2017-01-25T00:00:00Z", True),
        ("2017-01-25 00:00:00Z", True),
        ("2017-01-25", True),
        ("2017-01-25T00:00:00+00:00", True),
        ("2017-01-25T00:00:00.000Z", True),
        ("2017-01-25T00:00:00+02:00", True),
        ("2017/01/25", False),
        ("25-01-2017", False),
        ("", False),
    ],
)
def test_replication_start_date_pattern(value, expected):
    pattern = _spec_start_date_property()["pattern"]
    assert bool(re.match(pattern, value)) is expected


@pytest.mark.parametrize(
    "start_date, expected_since_timestamp",
    [
        pytest.param(None, "2010-01-01 00:00:00", id="missing_uses_default"),
        pytest.param("2017-01-25T00:00:00Z", "2017-01-25 00:00:00", id="iso_z"),
        pytest.param("2017-01-25 00:00:00Z", "2017-01-25 00:00:00", id="space_separator"),
        pytest.param("2017-01-25", "2017-01-25 00:00:00", id="date_only"),
        pytest.param("2017-01-25T00:00:00+02:00", "2017-01-24 22:00:00", id="utc_offset"),
        pytest.param("2017-01-25T00:00:00.000Z", "2017-01-25 00:00:00", id="fractional_seconds"),
    ],
)
def test_start_date_reaches_the_api_as_since_timestamp(requests_mock, start_date, expected_since_timestamp):
    requests_mock.get(_RECENTS_URL, json=_EMPTY_PAGE)
    config = {"api_token": "token"}
    if start_date is not None:
        config["replication_start_date"] = start_date

    output = _read_deals(config)

    assert output.errors == []
    assert requests_mock.last_request.qs["since_timestamp"] == [expected_since_timestamp]


def test_malformed_start_date_fails_config_validation(requests_mock):
    requests_mock.get(_RECENTS_URL, json=_EMPTY_PAGE)

    output = _read_deals({"api_token": "token", "replication_start_date": "2017/01/25"})

    assert not requests_mock.called
    assert len(output.errors) == 1
    error = output.errors[0].trace.error
    assert error.failure_type == FailureType.config_error
    assert "does not match" in error.message


def test_legacy_authorization_config_is_migrated(capsys):
    source = get_source({"authorization": {"auth_type": "Token", "api_token": "legacy-token"}})
    assert source._config["api_token"] == "legacy-token"
    control_messages = [json.loads(line) for line in capsys.readouterr().out.splitlines() if '"CONTROL"' in line]
    assert len(control_messages) == 1
    assert control_messages[0]["type"] == Type.CONTROL.value
    assert control_messages[0]["control"]["connectorConfig"]["config"]["api_token"] == "legacy-token"


def test_current_config_is_not_migrated(capsys):
    config = {
        "credentials": {"auth_type": "api_token", "api_token": "current-token"},
        "replication_start_date": "2017-01-25T00:00:00Z",
    }
    source = get_source(config)
    assert source._config["credentials"]["api_token"] == "current-token"
    assert "CONTROL" not in capsys.readouterr().out
