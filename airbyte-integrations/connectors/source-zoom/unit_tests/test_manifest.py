# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import yaml

from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"


def test_manifest_declares_concurrency_and_api_budget():
    manifest = yaml.safe_load(MANIFEST_PATH.read_text())

    concurrency = manifest["concurrency_level"]
    assert concurrency == {
        "type": "ConcurrencyLevel",
        "default_concurrency": "{{ config.get('num_workers', 8) }}",
        "max_concurrency": 20,
    }

    api_budget = manifest["api_budget"]
    policy = api_budget["policies"][0]
    assert api_budget["type"] == "HTTPAPIBudget"
    assert policy["type"] == "MovingWindowCallRatePolicy"
    assert policy["rates"][0] == {
        "limit": "{{ config.get('api_rate_limit_per_second', 10) }}",
        "interval": "PT1S",
    }
    assert policy["matchers"] == []
    assert api_budget["ratelimit_reset_header"] == "Retry-After"
    assert api_budget["status_codes_for_ratelimit_hit"] == [429]


def test_source_resolves_configured_concurrency():
    source = YamlDeclarativeSource(
        path_to_yaml=str(MANIFEST_PATH),
        catalog=ConfiguredAirbyteCatalog(streams=[]),
        config={
            "account_id": "account_id",
            "client_id": "client_id",
            "client_secret": "client_secret",
            "authorization_endpoint": "https://zoom.us/oauth/token",
            "num_workers": 7,
            "api_rate_limit_per_second": 4,
        },
    )

    assert source._concurrent_source._threadpool._threadpool._max_workers == 7
