# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest
import yaml

from airbyte_cdk.sources.declarative.interpolation import InterpolatedString


MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"


def _manifest():
    return yaml.safe_load(MANIFEST_PATH.read_text())


def _evaluate(expression, config):
    return int(InterpolatedString.create(expression, parameters={}).eval(config))


@pytest.mark.parametrize(
    ("client_secret", "expected_concurrency", "expected_rate_limit"),
    [
        ("sk_test_x", 4, 25),
        ("rk_test_x", 4, 25),
        ("sk_live_x", 10, 100),
        ("rk_live_x", 10, 100),
    ],
)
def test_manifest_uses_key_mode_for_default_concurrency_and_rate_limit(client_secret, expected_concurrency, expected_rate_limit):
    manifest = _manifest()
    config = {"client_secret": client_secret}

    assert _evaluate(manifest["concurrency_level"]["default_concurrency"], config) == expected_concurrency
    rate_limit_expression = manifest["api_budget"]["policies"][1]["rates"][0]["limit"]
    assert _evaluate(rate_limit_expression, config) == expected_rate_limit


def test_manifest_honors_explicit_concurrency_and_rate_limit():
    manifest = _manifest()
    config = {"client_secret": "rk_live_x", "num_workers": 3, "call_rate_limit": 7}

    assert _evaluate(manifest["concurrency_level"]["default_concurrency"], config) == 3
    rate_limit_expression = manifest["api_budget"]["policies"][1]["rates"][0]["limit"]
    assert _evaluate(rate_limit_expression, config) == 7
