# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Tests for the authentication options the spec offers in the setup form, and for sources that use a hidden option."""

import json
import logging
from typing import Any, Mapping

import jsonschema
import pytest
import yaml
from conftest import _YAML_FILE_PATH, get_source

from airbyte_cdk.models import Status, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS


LOGGER = logging.getLogger("airbyte")
MANIFEST = yaml.safe_load(_YAML_FILE_PATH.read_text())
MANIFEST_SPEC = MANIFEST["spec"]
MANIFEST_STREAMS = MANIFEST["streams"]
VOICE_API = "https://example.zendesk.com/api/v2/channels/voice"
EDITIONS = ["CLOUD", "COMMUNITY", "ENTERPRISE", None]
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


@pytest.mark.parametrize("edition", EDITIONS)
def test_setup_form_offers_only_refresh_token_oauth(monkeypatch: pytest.MonkeyPatch, edition: str | None) -> None:
    _set_edition(monkeypatch, edition)

    connection_specification = _connection_specification()

    assert _auth_types(connection_specification) == ["oauth2_refresh", "api_token", "oauth2.0"]
    assert _hidden_auth_types(connection_specification) == {"api_token", "oauth2.0"}


@pytest.mark.parametrize("edition", EDITIONS)
def test_spec_is_the_manifest_spec_in_every_edition(monkeypatch: pytest.MonkeyPatch, edition: str | None) -> None:
    _set_edition(monkeypatch, edition)

    assert _connection_specification() == MANIFEST_SPEC["connection_specification"]


def test_credentials_description_does_not_recommend_an_api_token() -> None:
    description = _connection_specification()["properties"]["credentials"]["description"]

    assert "recommend" not in description
    assert "April 30, 2027" in description


def test_oauth_button_is_tied_to_the_visible_option() -> None:
    advanced_auth = get_source({}).spec(LOGGER).advanced_auth

    assert advanced_auth.predicate_key == ["credentials", "auth_type"]
    assert advanced_auth.predicate_value == "oauth2_refresh"


@pytest.mark.parametrize("config", CONFIG_SHAPES.values(), ids=CONFIG_SHAPES.keys())
def test_existing_config_shapes_are_valid_against_the_spec(config: Mapping[str, Any]) -> None:
    jsonschema.validate(config, _connection_specification())


@pytest.mark.parametrize("config", CONFIG_SHAPES.values(), ids=CONFIG_SHAPES.keys())
def test_existing_config_shapes_pass_check_discover_and_read(config: Mapping[str, Any]) -> None:
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
    assert len(catalog.streams) == len(MANIFEST_STREAMS)
    assert not output.errors
    assert [record.record.data["id"] for record in output.records] == [1]
