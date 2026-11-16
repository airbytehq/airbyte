# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Tests for the spec the connector returns per Airbyte edition, and for sources that use an option the Cloud spec hides."""

import json
import logging
from copy import deepcopy
from typing import Any, Mapping

import jsonschema
import pytest
import yaml
from conftest import _YAML_FILE_PATH, get_source

from airbyte_cdk.models import Status, SyncMode
from airbyte_cdk.sources.declarative.spec import Spec
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS


LOGGER = logging.getLogger("airbyte")
MANIFEST_SPEC = yaml.safe_load(_YAML_FILE_PATH.read_text())["spec"]
VOICE_API = "https://example.zendesk.com/api/v2/channels/voice"
CONFIG_SHAPES = {
    "legacy_top_level_token": {
        "subdomain": "example",
        "start_date": "2024-01-01T00:00:00Z",
        "access_token": "token",
        "email": "a@example.com",
    },
    "api_token": {
        "subdomain": "example",
        "start_date": "2024-01-01T00:00:00Z",
        "credentials": {"auth_type": "api_token", "email": "a@example.com", "api_token": "token"},
    },
    "legacy_oauth": {
        "subdomain": "example",
        "start_date": "2024-01-01T00:00:00Z",
        "credentials": {"auth_type": "oauth2.0", "access_token": "token"},
    },
    "oauth_refresh": {
        "subdomain": "example",
        "start_date": "2024-01-01T00:00:00Z",
        "credentials": {
            "auth_type": "oauth2_refresh",
            "client_id": "client",
            "client_secret": "secret",
            "refresh_token": "refresh",
            "access_token": "token",
            "token_expiry_date": "2999-01-01T00:00:00Z",
        },
    },
}


def _set_edition(monkeypatch: pytest.MonkeyPatch, edition: str | None) -> None:
    if edition is None:
        monkeypatch.delenv("AIRBYTE_EDITION", raising=False)
    else:
        monkeypatch.setenv("AIRBYTE_EDITION", edition)


def _connection_specification() -> Mapping[str, Any]:
    return get_source({}).spec(LOGGER).connectionSpecification


def _hidden_auth_types(connection_specification: Mapping[str, Any]) -> set[str]:
    return {
        option["properties"]["auth_type"]["const"]
        for option in connection_specification["properties"]["credentials"]["oneOf"]
        if option.get("airbyte_hidden")
    }


def _auth_types(connection_specification: Mapping[str, Any]) -> list[str]:
    return [option["properties"]["auth_type"]["const"] for option in connection_specification["properties"]["credentials"]["oneOf"]]


@pytest.mark.parametrize("edition", ["CLOUD", "cloud"])
def test_cloud_spec_hides_api_token_and_legacy_oauth(monkeypatch: pytest.MonkeyPatch, edition: str) -> None:
    _set_edition(monkeypatch, edition)

    connection_specification = _connection_specification()

    assert _auth_types(connection_specification) == ["oauth2_refresh", "api_token", "oauth2.0"]
    assert _hidden_auth_types(connection_specification) == {"api_token", "oauth2.0"}


@pytest.mark.parametrize("edition", ["COMMUNITY", "ENTERPRISE", "", None])
def test_self_managed_spec_is_the_manifest_spec(monkeypatch: pytest.MonkeyPatch, edition: str | None) -> None:
    _set_edition(monkeypatch, edition)

    connection_specification = _connection_specification()

    assert connection_specification == MANIFEST_SPEC["connection_specification"]
    assert _hidden_auth_types(connection_specification) == set()


def test_cloud_spec_differs_from_the_manifest_spec_only_by_the_hidden_flag_and_the_description(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_edition(monkeypatch, "CLOUD")

    connection_specification = deepcopy(dict(_connection_specification()))
    credentials = connection_specification["properties"]["credentials"]
    for option in credentials["oneOf"]:
        option.pop("airbyte_hidden", None)
    cloud_description = credentials.pop("description")
    manifest_specification = deepcopy(MANIFEST_SPEC["connection_specification"])
    manifest_description = manifest_specification["properties"]["credentials"].pop("description")

    assert connection_specification == manifest_specification
    assert "API token" in manifest_description and "recommend" in manifest_description
    assert "recommend" not in cloud_description
    assert "April 30, 2027" in cloud_description


def test_advanced_auth_is_the_same_in_every_edition(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_edition(monkeypatch, "CLOUD")
    cloud_advanced_auth = get_source({}).spec(LOGGER).advanced_auth
    _set_edition(monkeypatch, "COMMUNITY")
    self_managed_advanced_auth = get_source({}).spec(LOGGER).advanced_auth

    assert cloud_advanced_auth == self_managed_advanced_auth
    assert cloud_advanced_auth.predicate_value == "oauth2_refresh"


def test_cloud_spec_leaves_the_declared_spec_untouched(monkeypatch: pytest.MonkeyPatch) -> None:
    from source_declarative_manifest.components import HideDeprecatedAuthOptionsInCloud

    _set_edition(monkeypatch, "CLOUD")
    declared = deepcopy(MANIFEST_SPEC["connection_specification"])
    spec_component = Spec(connection_specification=declared, parameters={}, config_transformations=[HideDeprecatedAuthOptionsInCloud()])

    specification = spec_component.generate_spec()

    assert _hidden_auth_types(specification.connectionSpecification) == {"api_token", "oauth2.0"}
    assert declared == MANIFEST_SPEC["connection_specification"]


def test_spec_without_the_marker_is_unchanged_in_cloud(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_edition(monkeypatch, "CLOUD")
    get_source({})  # loads components.py, which replaces Spec.generate_spec

    specification = Spec(connection_specification=deepcopy(MANIFEST_SPEC["connection_specification"]), parameters={}).generate_spec()

    assert _hidden_auth_types(specification.connectionSpecification) == set()


@pytest.mark.parametrize("config", CONFIG_SHAPES.values(), ids=CONFIG_SHAPES.keys())
def test_existing_config_shapes_are_valid_against_the_cloud_spec(monkeypatch: pytest.MonkeyPatch, config: Mapping[str, Any]) -> None:
    _set_edition(monkeypatch, "CLOUD")

    jsonschema.validate(config, _connection_specification())


@pytest.mark.parametrize("config", CONFIG_SHAPES.values(), ids=CONFIG_SHAPES.keys())
def test_existing_config_shapes_pass_check_discover_and_read_in_cloud(monkeypatch: pytest.MonkeyPatch, config: Mapping[str, Any]) -> None:
    _set_edition(monkeypatch, "CLOUD")

    with HttpMocker() as http_mocker:
        http_mocker.get(
            HttpRequest(url=f"{VOICE_API}/stats/account_overview", query_params=ANY_QUERY_PARAMS),
            HttpResponse(body=json.dumps({"account_overview": {"total_calls": 1}}), status_code=200),
        )
        http_mocker.get(
            HttpRequest(url=f"{VOICE_API}/addresses", query_params=ANY_QUERY_PARAMS),
            HttpResponse(body=json.dumps({"addresses": [{"id": 1, "name": "Main"}]}), status_code=200),
        )
        source = get_source(config)

        status = source.check(LOGGER, config)
        catalog = source.discover(LOGGER, config)
        output = read(source, config, CatalogBuilder().with_stream("addresses", SyncMode.full_refresh).build())

    assert status.status == Status.SUCCEEDED, status.message
    assert len(catalog.streams) == 13
    assert not output.errors
    assert [record.record.data["id"] for record in output.records] == [1]
