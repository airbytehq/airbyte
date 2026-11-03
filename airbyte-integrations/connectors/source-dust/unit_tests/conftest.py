# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest
import yaml

from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]


def _get_manifest_path() -> Path:
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    return ci_path if ci_path.exists() else Path(__file__).parent.parent


@pytest.fixture(scope="session")
def manifest() -> dict:
    return yaml.safe_load((_get_manifest_path() / "manifest.yaml").read_text())


@pytest.fixture(scope="session")
def resolved_manifest(manifest: dict) -> dict:
    return ManifestReferenceResolver().preprocess_manifest(manifest)
