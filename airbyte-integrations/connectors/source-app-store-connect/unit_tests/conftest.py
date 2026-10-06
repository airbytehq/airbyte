# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.state_builder import StateBuilder


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]

_CI_MANIFEST_PATH = Path("/airbyte/integration_code/source_declarative_manifest/manifest.yaml")
_MANIFEST_PATH = _CI_MANIFEST_PATH if _CI_MANIFEST_PATH.exists() else Path(__file__).resolve().parents[1] / "manifest.yaml"


def build_config(**overrides: Any) -> Mapping[str, Any]:
    private_key = ec.generate_private_key(ec.SECP256R1()).private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    config = {
        "iss": "00000000-0000-0000-0000-000000000000",
        "kid": "TESTKEY123",
        "secret_key": private_key.decode(),
        "vendorID": "12345678",
        "reviews_start_date": "2026-01-01T00:00:00Z",
        "analytics_reports_start_date": "2026-01-01",
    }
    config.update(overrides)
    return config


def get_source(config: Mapping[str, Any], state: Any = None) -> YamlDeclarativeSource:
    source = YamlDeclarativeSource(
        path_to_yaml=str(_MANIFEST_PATH),
        catalog=CatalogBuilder().build(),
        config=config,
        state=state if state is not None else StateBuilder().build(),
    )
    source._constructor._disable_cache = True
    return source
