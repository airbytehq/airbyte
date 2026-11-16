# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
The Cloud spec hides the `API Token` and `OAuth2.0 (Legacy)` authentication options from the setup form, so a new
Cloud source can only pick `OAuth2.0 with Refresh Token`. The self-managed spec is unchanged, and nothing is rejected
at runtime: a source that already uses a hidden option keeps passing check, discover and read.
"""

import copy
import importlib.util
import json
import logging
import os
import subprocess
import sys
from datetime import timedelta
from typing import Any, List, Mapping, Optional

import pytest
import yaml

from airbyte_cdk.models import Status, SyncMode
from airbyte_cdk.sources.declarative.spec.spec import Spec
from airbyte_cdk.sources.utils.schema_helpers import check_config_against_spec_or_exit
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now

from .conftest import _SOURCE_FOLDER_PATH, _YAML_FILE_PATH, get_source
from .mock_server.config import ConfigBuilder
from .mock_server.request_builder import ApiTokenAuthenticator, OAuthBearerAuthenticator, ZendeskSupportRequestBuilder
from .mock_server.response_builder import TagsRecordBuilder, TagsResponseBuilder
from .mock_server.utils import read_stream


_EDITION = "AIRBYTE_EDITION"
_HIDDEN_IN_CLOUD = {"api_token", "oauth2.0"}
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
        monkeypatch.delenv(_EDITION, raising=False)
    else:
        monkeypatch.setenv(_EDITION, edition)


def _connection_specification(config: Optional[Mapping[str, Any]] = None) -> Mapping[str, Any]:
    return get_source(config=copy.deepcopy(dict(config or _API_TOKEN_CONFIG))).spec(logging.getLogger("airbyte")).connectionSpecification


def _auth_options(connection_specification: Mapping[str, Any]) -> List[Mapping[str, Any]]:
    return connection_specification["properties"]["credentials"]["oneOf"]


def _option_name(option: Mapping[str, Any]) -> str:
    return option["properties"]["credentials"]["const"]


def _manifest_connection_specification() -> Mapping[str, Any]:
    return yaml.safe_load(_YAML_FILE_PATH.read_text())["spec"]["connection_specification"]


@pytest.mark.parametrize("edition", [None, "", "COMMUNITY", "ENTERPRISE"])
def test_self_managed_spec_is_the_manifest_spec(monkeypatch, edition):
    _set_edition(monkeypatch, edition)

    connection_specification = _connection_specification()

    assert connection_specification == _manifest_connection_specification()
    assert [_option_name(option) for option in _auth_options(connection_specification)] == ["oauth2_refresh", "api_token", "oauth2.0"]
    assert not any("airbyte_hidden" in option for option in _auth_options(connection_specification))


@pytest.mark.parametrize("edition", ["CLOUD", "cloud"])
def test_cloud_spec_hides_api_token_and_legacy_oauth(monkeypatch, edition):
    _set_edition(monkeypatch, edition)

    options = _auth_options(_connection_specification())

    assert {_option_name(option) for option in options if option.get("airbyte_hidden") is True} == _HIDDEN_IN_CLOUD
    assert [_option_name(option) for option in options if "airbyte_hidden" not in option] == ["oauth2_refresh"]
    # The setup form preselects the first option, so it has to be the visible one.
    assert _option_name(options[0]) == "oauth2_refresh"


def test_cloud_spec_keeps_every_option_in_the_schema(monkeypatch):
    """Hiding is a form hint. Apart from it and the field description, the Cloud spec is the self-managed spec."""
    _set_edition(monkeypatch, "CLOUD")
    cloud = copy.deepcopy(dict(_connection_specification()))
    _set_edition(monkeypatch, "COMMUNITY")
    self_managed = copy.deepcopy(dict(_connection_specification()))

    assert cloud["properties"]["credentials"]["description"] != self_managed["properties"]["credentials"]["description"]
    assert "April 30, 2027" in cloud["properties"]["credentials"]["description"]

    for option in _auth_options(cloud):
        option.pop("airbyte_hidden", None)
    cloud["properties"]["credentials"]["description"] = self_managed["properties"]["credentials"]["description"]
    assert cloud == self_managed


def test_cloud_spec_leaves_the_oauth_flow_on_the_visible_option(monkeypatch):
    _set_edition(monkeypatch, "CLOUD")

    spec = get_source(config=copy.deepcopy(_API_TOKEN_CONFIG)).spec(logging.getLogger("airbyte"))

    assert spec.advanced_auth.predicate_key == ["credentials", "credentials"]
    assert spec.advanced_auth.predicate_value == "oauth2_refresh"


@pytest.mark.parametrize(
    "config", [_API_TOKEN_CONFIG, _LEGACY_OAUTH_CONFIG, _OAUTH_REFRESH_CONFIG], ids=["api_token", "oauth2.0", "oauth2_refresh"]
)
def test_stored_config_validates_against_the_cloud_spec(monkeypatch, config, tmp_path):
    _set_edition(monkeypatch, "CLOUD")
    source = get_source(config=copy.deepcopy(config))

    check_config_against_spec_or_exit(
        source.configure(config=copy.deepcopy(config), temp_dir=str(tmp_path)), source.spec(logging.getLogger("airbyte"))
    )


def test_spec_hook_leaves_the_config_alone(monkeypatch, tmp_path):
    _set_edition(monkeypatch, "CLOUD")
    source = get_source(config=copy.deepcopy(_API_TOKEN_CONFIG))

    assert source.configure(config=copy.deepcopy(_API_TOKEN_CONFIG), temp_dir=str(tmp_path)) == _API_TOKEN_CONFIG


@pytest.mark.parametrize("config, authenticator", _CONFIGS_ON_HIDDEN_OPTIONS)
def test_source_on_a_hidden_option_passes_check_in_cloud(monkeypatch, config, authenticator):
    _set_edition(monkeypatch, "CLOUD")

    with HttpMocker() as http_mocker:
        http_mocker.get(
            ZendeskSupportRequestBuilder.tags_endpoint(authenticator).with_page_size(100).build(),
            TagsResponseBuilder.tags_response().with_record(TagsRecordBuilder.tags_record()).build(),
        )
        config = copy.deepcopy(config)
        status = get_source(config=config).check(logger=logging.getLogger("airbyte"), config=config)

    assert status.status == Status.SUCCEEDED, status.message


@pytest.mark.parametrize("config, authenticator", _CONFIGS_ON_HIDDEN_OPTIONS)
def test_source_on_a_hidden_option_passes_discover_in_cloud(monkeypatch, config, authenticator):
    _set_edition(monkeypatch, "CLOUD")
    config = copy.deepcopy(config)

    catalog = get_source(config=config).discover(logging.getLogger("airbyte"), config)

    assert "tags" in {stream.name for stream in catalog.streams}


@pytest.mark.parametrize("config, authenticator", _CONFIGS_ON_HIDDEN_OPTIONS)
def test_source_on_a_hidden_option_reads_in_cloud(monkeypatch, config, authenticator):
    """`read_stream` goes through the entrypoint, which validates the config against the spec before reading."""
    _set_edition(monkeypatch, "CLOUD")

    with HttpMocker() as http_mocker:
        http_mocker.get(
            ZendeskSupportRequestBuilder.tags_endpoint(authenticator).with_page_size(100).build(),
            TagsResponseBuilder.tags_response().with_record(TagsRecordBuilder.tags_record()).build(),
        )
        output = read_stream("tags", SyncMode.full_refresh, copy.deepcopy(config))

    assert len(output.records) == 1
    assert not output.errors


def test_second_import_of_components_does_not_wrap_spec_generation_again(monkeypatch):
    """A second copy of the module must find the wrapper in place and leave it, or the wrappers nest per import."""
    _set_edition(monkeypatch, "CLOUD")
    _connection_specification()  # makes sure the CDK has imported components.py once
    installed = Spec.generate_spec
    assert getattr(installed, "_zendesk_support_edition_aware", False)

    module_spec = importlib.util.spec_from_file_location("components_second_import", _SOURCE_FOLDER_PATH / "components.py")
    module_spec.loader.exec_module(importlib.util.module_from_spec(module_spec))

    assert Spec.generate_spec is installed
    options = _auth_options(_connection_specification())
    assert {_option_name(option) for option in options if option.get("airbyte_hidden") is True} == _HIDDEN_IN_CLOUD


_SPEC_IN_A_NEW_PROCESS = """
import json, logging, sys
sys.path.append(sys.argv[1])
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
assert "components" not in sys.modules
spec = YamlDeclarativeSource(path_to_yaml=sys.argv[2]).spec(logging.getLogger("airbyte"))
print(json.dumps(spec.connectionSpecification["properties"]["credentials"]["oneOf"]))
"""


@pytest.mark.parametrize("edition, expected_hidden", [("CLOUD", _HIDDEN_IN_CLOUD), ("COMMUNITY", set())])
def test_spec_command_loads_the_components_module(edition, expected_hidden):
    """
    `spec` builds nothing but the spec block, and the CDK imports components.py only when it builds a custom component.
    Every other test in this session has that module imported already, so only a new process shows that the spec block
    itself pulls it in.
    """
    result = subprocess.run(
        [sys.executable, "-c", _SPEC_IN_A_NEW_PROCESS, str(_SOURCE_FOLDER_PATH), str(_YAML_FILE_PATH)],
        env={**os.environ, _EDITION: edition},
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert result.returncode == 0, result.stderr
    options = json.loads(result.stdout.strip().splitlines()[-1])
    assert {_option_name(option) for option in options if option.get("airbyte_hidden") is True} == expected_hidden
