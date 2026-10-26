# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import os
import sys
from pathlib import Path
from typing import Any, Mapping, Optional

from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.state_builder import StateBuilder


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]

os.environ.setdefault("REQUEST_CACHE_PATH", "REQUEST_CACHE_PATH")


def _manifest_dir() -> Path:
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if ci_path.exists():
        return ci_path
    return Path(__file__).parent.parent


_MANIFEST_DIR = _manifest_dir()
_MANIFEST_PATH = _MANIFEST_DIR / "manifest.yaml"

if str(_MANIFEST_DIR) not in sys.path:
    sys.path.append(str(_MANIFEST_DIR))


def get_source(
    config: Mapping[str, Any],
    catalog: Optional[ConfiguredAirbyteCatalog] = None,
    state=None,
) -> YamlDeclarativeSource:
    return YamlDeclarativeSource(
        path_to_yaml=str(_MANIFEST_PATH),
        catalog=catalog or CatalogBuilder().build(),
        config=config,
        state=state if state is not None else StateBuilder().build(),
    )
