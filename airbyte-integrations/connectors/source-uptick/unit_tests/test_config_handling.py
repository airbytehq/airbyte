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


@pytest.mark.parametrize(
    "raw_base_url, expected",
    [
        pytest.param("https://demo.onuptick.com", "https://demo.onuptick.com", id="canonical_unchanged"),
        pytest.param("http://demo.onuptick.com/", "https://demo.onuptick.com", id="http_scheme_and_trailing_slash"),
        pytest.param("HTTP://demo.onuptick.com//", "https://demo.onuptick.com", id="uppercase_scheme"),
        pytest.param("  https://demo.onuptick.com  ", "https://demo.onuptick.com", id="surrounding_whitespace"),
        pytest.param("https://demo.onuptick.com/api/v2.15/", "https://demo.onuptick.com", id="path_stripped"),
        pytest.param("demo.onuptick.com", "https://demo.onuptick.com", id="bare_host"),
        pytest.param("", "", id="empty_left_for_spec_validation"),
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


def test_base_url_spec_rejects_blank_values() -> None:
    base_url_schema = get_source(base_config()).resolved_manifest["spec"]["connection_specification"]["properties"]["base_url"]

    for blank in ("", "   "):
        with pytest.raises(ValidationError):
            validate(instance=blank, schema=base_url_schema)
    validate(instance="https://demo.onuptick.com", schema=base_url_schema)
