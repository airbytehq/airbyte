# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
The spec hides the `API Token` and `OAuth2.0 (Legacy)` authentication options from the setup form in every edition,
so a new source can only pick `OAuth2.0 with Refresh Token` there. Both options stay in the schema and nothing is
rejected at runtime: a source that already uses a hidden option keeps passing check, discover and read.
"""

import copy
import logging
from datetime import timedelta
from typing import Any, List, Mapping, Optional

import pytest
import yaml

from airbyte_cdk.models import Status, SyncMode
from airbyte_cdk.sources.utils.schema_helpers import check_config_against_spec_or_exit
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now

from .conftest import _YAML_FILE_PATH, get_source
from .mock_server.config import ConfigBuilder
from .mock_server.request_builder import ApiTokenAuthenticator, OAuthBearerAuthenticator, ZendeskSupportRequestBuilder
from .mock_server.response_builder import TagsRecordBuilder, TagsResponseBuilder
from .mock_server.utils import read_stream


_LOGGER = logging.getLogger("airbyte")
_EDITIONS = ["CLOUD", "COMMUNITY", "ENTERPRISE", None]
_HIDDEN_OPTIONS = {"api_token", "oauth2.0"}
_START_DATE = ab_datetime_now().subtract(timedelta(weeks=104))

_API_TOKEN_CONFIG = (
    ConfigBuilder()
    .with_subdomain("d3v-airbyte")
    .with_start_date(_START_DATE)
    .with_basic_auth_credentials("user@example.com", "password")
    .build()
)
_LEGACY_OAUTH_CONFIG = (
    ConfigBuilder().with_subdomain("d3v-airbyte").with_start_date(_START_DATE).with_oauth_credentials("legacy-token").build()
)
_OAUTH_REFRESH_CONFIG = (
    ConfigBuilder()
    .with_subdomain("d3v-airbyte")
    .with_start_date(_START_DATE)
    .with_oauth_refresh_credentials(
        client_id="client-id",
        client_secret="client-secret",
        refresh_token="refresh-token",
        access_token="access-token",
        token_expiry_date=ab_datetime_now().add(timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ"),
    )
    .build()
)
_CONFIGS_ON_HIDDEN_OPTIONS = [
    pytest.param(_API_TOKEN_CONFIG, ApiTokenAuthenticator("user@example.com", "password"), id="api_token"),
    pytest.param(_LEGACY_OAUTH_CONFIG, OAuthBearerAuthenticator("legacy-token"), id="oauth2.0"),
]


def _set_edition(monkeypatch: pytest.MonkeyPatch, edition: Optional[str]) -> None:
    if edition is None:
        monkeypatch.delenv("AIRBYTE_EDITION", raising=False)
    else:
        monkeypatch.setenv("AIRBYTE_EDITION", edition)


def _connection_specification() -> Mapping[str, Any]:
    # A new source per call: the CDK cannot generate the spec twice from one source.
    return get_source(config=copy.deepcopy(_API_TOKEN_CONFIG)).spec(_LOGGER).connectionSpecification


def _auth_options(connection_specification: Mapping[str, Any]) -> List[Mapping[str, Any]]:
    return connection_specification["properties"]["credentials"]["oneOf"]


def _option_name(option: Mapping[str, Any]) -> str:
    return option["properties"]["credentials"]["const"]


@pytest.mark.parametrize("edition", _EDITIONS)
def test_setup_form_offers_only_refresh_token_oauth(monkeypatch, edition):
    _set_edition(monkeypatch, edition)

    options = _auth_options(_connection_specification())

    # The setup form preselects the first option, so the visible one has to stay first.
    assert [_option_name(option) for option in options] == ["oauth2_refresh", "api_token", "oauth2.0"]
    assert {_option_name(option) for option in options if option.get("airbyte_hidden") is True} == _HIDDEN_OPTIONS
    assert [_option_name(option) for option in options if "airbyte_hidden" not in option] == ["oauth2_refresh"]


@pytest.mark.parametrize("edition", _EDITIONS)
def test_spec_is_the_manifest_spec_in_every_edition(monkeypatch, edition):
    _set_edition(monkeypatch, edition)

    assert _connection_specification() == yaml.safe_load(_YAML_FILE_PATH.read_text())["spec"]["connection_specification"]


def test_hidden_options_keep_their_fields_in_the_schema():
    """`airbyte_hidden` is a form hint. The hidden options must stay complete, or stored configs stop validating."""
    options = {_option_name(option): option for option in _auth_options(_connection_specification())}

    assert options["api_token"]["required"] == ["email", "api_token"]
    assert set(options["api_token"]["properties"]) == {"credentials", "email", "api_token"}
    assert options["oauth2.0"]["required"] == ["access_token"]
    assert set(options["oauth2.0"]["properties"]) == {"credentials", "access_token", "client_id", "client_secret"}


def test_credentials_description_does_not_recommend_an_api_token():
    description = _connection_specification()["properties"]["credentials"]["description"]

    assert "recommend" not in description
    assert "April 30, 2027" in description


def test_oauth_button_is_tied_to_the_visible_option():
    advanced_auth = get_source(config=copy.deepcopy(_API_TOKEN_CONFIG)).spec(_LOGGER).advanced_auth

    assert advanced_auth.predicate_key == ["credentials", "credentials"]
    assert advanced_auth.predicate_value == "oauth2_refresh"


@pytest.mark.parametrize(
    "config", [_API_TOKEN_CONFIG, _LEGACY_OAUTH_CONFIG, _OAUTH_REFRESH_CONFIG], ids=["api_token", "oauth2.0", "oauth2_refresh"]
)
def test_stored_config_validates_against_the_spec(config, tmp_path):
    source = get_source(config=copy.deepcopy(config))

    check_config_against_spec_or_exit(source.configure(config=copy.deepcopy(config), temp_dir=str(tmp_path)), source.spec(_LOGGER))


@pytest.mark.parametrize("config, authenticator", _CONFIGS_ON_HIDDEN_OPTIONS)
def test_source_on_a_hidden_option_passes_check(config, authenticator):
    with HttpMocker() as http_mocker:
        http_mocker.get(
            ZendeskSupportRequestBuilder.tags_endpoint(authenticator).with_page_size(100).build(),
            TagsResponseBuilder.tags_response().with_record(TagsRecordBuilder.tags_record()).build(),
        )
        config = copy.deepcopy(config)
        status = get_source(config=config).check(logger=_LOGGER, config=config)

    assert status.status == Status.SUCCEEDED, status.message


@pytest.mark.parametrize("config, authenticator", _CONFIGS_ON_HIDDEN_OPTIONS)
def test_source_on_a_hidden_option_passes_discover(config, authenticator):
    config = copy.deepcopy(config)

    catalog = get_source(config=config).discover(_LOGGER, config)

    assert "tags" in {stream.name for stream in catalog.streams}


@pytest.mark.parametrize("config, authenticator", _CONFIGS_ON_HIDDEN_OPTIONS)
def test_source_on_a_hidden_option_reads(config, authenticator):
    """`read_stream` goes through the entrypoint, which validates the config against the spec before reading."""
    with HttpMocker() as http_mocker:
        http_mocker.get(
            ZendeskSupportRequestBuilder.tags_endpoint(authenticator).with_page_size(100).build(),
            TagsResponseBuilder.tags_response().with_record(TagsRecordBuilder.tags_record()).build(),
        )
        output = read_stream("tags", SyncMode.full_refresh, copy.deepcopy(config))

    assert len(output.records) == 1
    assert not output.errors
