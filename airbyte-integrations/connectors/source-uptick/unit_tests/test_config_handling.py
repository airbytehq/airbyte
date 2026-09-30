# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Guards the config-derived behavior added in `manifest.yaml`.

Covers the `base_url` normalization rule under `spec.config_normalization_rules` and the
`num_workers` fallback in `concurrency_level.default_concurrency`. Both are Jinja expressions
that are only evaluated at runtime, so these tests fail if a future manifest edit breaks them.
"""

from typing import Any

import pytest
from conftest import base_config, get_source
from jsonschema import ValidationError, validate

from airbyte_cdk.sources.declarative.models.declarative_component_schema import ConcurrencyLevel as ConcurrencyLevelModel


_DEFAULT_CONCURRENCY = 3
_OMITTED = object()


@pytest.mark.parametrize(
    "raw_base_url, expected",
    [
        pytest.param("https://demo.onuptick.com", "https://demo.onuptick.com", id="canonical_unchanged"),
        pytest.param("http://demo.onuptick.com/", "https://demo.onuptick.com", id="http_scheme_and_trailing_slash"),
        pytest.param("HTTP://demo.onuptick.com//", "https://demo.onuptick.com", id="uppercase_scheme"),
        pytest.param("  https://demo.onuptick.com  ", "https://demo.onuptick.com", id="surrounding_whitespace"),
        pytest.param("https://demo.onuptick.com/api/v2.15/", "https://demo.onuptick.com", id="path_stripped"),
        pytest.param("demo.onuptick.com", "https://demo.onuptick.com", id="bare_host"),
        pytest.param("", "", id="empty_left_unnormalized"),
        pytest.param("   ", "   ", id="whitespace_only_left_unnormalized"),
        pytest.param(None, None, id="null_left_for_spec_validation"),
        pytest.param(42, 42, id="non_string_left_for_spec_validation"),
    ],
)
def test_base_url_normalization(raw_base_url: Any, expected: Any) -> None:
    source = get_source(base_config(base_url=raw_base_url))

    assert source._config["base_url"] == expected


def test_base_url_normalization_skips_missing_key() -> None:
    config = base_config()
    del config["base_url"]

    source = get_source(config)

    assert "base_url" not in source._config


@pytest.mark.parametrize(
    "num_workers, expected",
    [
        pytest.param(5, 5, id="valid_integer_used"),
        pytest.param(1, 1, id="lower_bound_used"),
        pytest.param(None, _DEFAULT_CONCURRENCY, id="null_falls_back"),
        pytest.param(0, _DEFAULT_CONCURRENCY, id="zero_falls_back"),
        pytest.param(-2, _DEFAULT_CONCURRENCY, id="negative_falls_back"),
        pytest.param(2.5, _DEFAULT_CONCURRENCY, id="float_falls_back"),
        pytest.param(True, _DEFAULT_CONCURRENCY, id="boolean_falls_back"),
        pytest.param("4", _DEFAULT_CONCURRENCY, id="string_falls_back"),
    ],
)
def test_default_concurrency(num_workers: Any, expected: int) -> None:
    source = get_source(base_config(num_workers=num_workers))
    component = source._constructor.create_component(ConcurrencyLevelModel, source.resolved_manifest["concurrency_level"], source._config)

    assert component.get_concurrency_level() == expected


def test_default_concurrency_when_num_workers_missing() -> None:
    source = get_source(base_config())
    component = source._constructor.create_component(ConcurrencyLevelModel, source.resolved_manifest["concurrency_level"], source._config)

    assert component.get_concurrency_level() == _DEFAULT_CONCURRENCY


def test_max_requests_per_minute_spec_validation() -> None:
    spec_schema = get_source(base_config()).resolved_manifest["spec"]["connection_specification"]

    def _config(value: Any) -> dict:
        config = base_config()
        if value is not _OMITTED:
            config["max_requests_per_minute"] = value
        return config

    validate(instance=_config(_OMITTED), schema=spec_schema)
    validate(instance=_config(60), schema=spec_schema)
    for invalid in (0, "60", 2.5, 601):
        with pytest.raises(ValidationError):
            validate(instance=_config(invalid), schema=spec_schema)


def test_spec_declares_oauth_advanced_auth() -> None:
    spec = get_source(base_config()).resolved_manifest["spec"]

    assert spec["advanced_auth"]["predicate_key"] == ["credentials", "auth_type"]
    assert spec["advanced_auth"]["predicate_value"] == "oauth2.0"
    credentials = spec["connection_specification"]["properties"]["credentials"]
    assert [variant["properties"]["auth_type"]["const"] for variant in credentials["oneOf"]] == ["oauth2.0", "password"]
    oauth_variant = credentials["oneOf"][0]
    assert "workspace" in oauth_variant["required"]
    assert oauth_variant["properties"]["workspace"]["pattern"] == "^[a-z0-9-]+$"
    assert oauth_variant["properties"]["workspace"]["pattern_descriptor"] == "acme"
    assert "base_url" not in oauth_variant["properties"]
    password_variant = credentials["oneOf"][1]
    assert "base_url" in password_variant["required"]
    assert "base_url" in password_variant["properties"]
    properties = spec["connection_specification"]["properties"]
    # The legacy top-level fields stay in the schema (copy-only migration keeps writing them) but
    # are hidden in the UI; base_url is derived from credentials at runtime.
    for field in ("base_url", "client_id", "client_secret", "username", "password"):
        assert properties[field]["airbyte_hidden"] is True
    assert spec["connection_specification"]["required"] == []
    assert "pattern" not in spec["connection_specification"]["properties"]["base_url"]
    user_input = spec["advanced_auth"]["oauth_config_specification"]["oauth_user_input_from_connector_config_specification"]
    assert user_input["properties"]["workspace"]["path_in_connector_config"] == ["credentials", "workspace"]
    oauth_input = spec["advanced_auth"]["oauth_config_specification"]["oauth_connector_input_specification"]
    assert oauth_input["consent_url"].startswith("https://{{ workspace | urlencode }}.onuptick.com/api/oauth2/")
    assert oauth_input["access_token_url"].startswith("https://{{ workspace | urlencode }}.onuptick.com/api/oauth2/")
    assert "regex_replace" not in oauth_input["consent_url"]
    assert "regex_replace" not in oauth_input["access_token_url"]


@pytest.mark.parametrize(
    "base_url",
    [
        pytest.param("http://x.onuptick.com", id="http_scheme"),
        pytest.param("https://x.onuptick.com/", id="trailing_slash"),
        pytest.param("https://x.onuptick.com", id="canonical_https"),
        pytest.param(" https://x.onuptick.com/api/v2.15/ ", id="whitespace_and_path"),
    ],
)
def test_legacy_base_url_shapes_validate_against_spec(base_url: Any) -> None:
    spec_schema = get_source(base_config()).resolved_manifest["spec"]["connection_specification"]

    validate(instance=base_config(base_url=base_url), schema=spec_schema)


def test_legacy_top_level_config_validates() -> None:
    spec_schema = get_source(base_config()).resolved_manifest["spec"]["connection_specification"]

    validate(instance=base_config(), schema=spec_schema)
    # The config the connector actually runs with: migrated legacy credentials.
    validate(instance=get_source(base_config())._config, schema=spec_schema)


@pytest.mark.parametrize("credential_value", ["S3cret!", "12345678", "True", "1e5"])
def test_migrated_legacy_config_validates_against_spec(credential_value: str) -> None:
    spec_schema = get_source(base_config()).resolved_manifest["spec"]["connection_specification"]
    config = base_config(password=credential_value, client_id=credential_value)

    migrated = get_source(config)._config

    validate(instance=migrated, schema=spec_schema)
    credentials = migrated["credentials"]
    assert credentials["auth_type"] == "password"
    for field in ("base_url", "client_id", "client_secret", "username", "password"):
        assert isinstance(credentials[field], str)
        # Copy-only migration: the top-level fields are kept so the config works on <=1.3.x.
        assert migrated[field] == credentials[field]


def test_oauth_config_without_base_url_validates_against_spec() -> None:
    spec_schema = get_source(base_config()).resolved_manifest["spec"]["connection_specification"]
    config = {
        "credentials": {
            "auth_type": "oauth2.0",
            "workspace": "test-tenant",
            "client_id": "test-client-id",
            "client_secret": "test-client-secret",
            "refresh_token": "test-refresh-token",
        }
    }

    validate(instance=config, schema=spec_schema)
    # The connector derives base_url from the workspace at construction.
    assert get_source(config)._config["base_url"] == "https://test-tenant.onuptick.com"


def test_password_config_with_nested_base_url_validates_against_spec() -> None:
    spec_schema = get_source(base_config()).resolved_manifest["spec"]["connection_specification"]
    config = {
        "credentials": {
            "auth_type": "password",
            "base_url": "https://test-tenant.onuptick.com",
            "client_id": "test-client-id",
            "client_secret": "test-client-secret",
            "username": "test-user",
            "password": "test-password",
        }
    }

    validate(instance=config, schema=spec_schema)
    # The connector derives the top-level base_url (what requesters read) from credentials.base_url.
    assert get_source(config)._config["base_url"] == "https://test-tenant.onuptick.com"


@pytest.mark.parametrize("workspace", ["evil.com/", "UPPER", "bad host", "tenant.example.org"])
def test_oauth_workspace_rejects_non_workspace_values(workspace: str) -> None:
    oauth_user_input_schema = get_source(base_config()).resolved_manifest["spec"]["advanced_auth"]["oauth_config_specification"][
        "oauth_user_input_from_connector_config_specification"
    ]

    with pytest.raises(ValidationError):
        validate(instance={"workspace": workspace}, schema=oauth_user_input_schema)
