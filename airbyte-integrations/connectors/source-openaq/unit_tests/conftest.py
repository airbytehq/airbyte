# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import os
from pathlib import Path
from typing import Any, Mapping

from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.state_builder import StateBuilder


os.environ.setdefault("REQUEST_CACHE_PATH", "REQUEST_CACHE_PATH")

_CI_PATH = Path("/airbyte/integration_code/source_declarative_manifest")
MANIFEST_PATH = (_CI_PATH if _CI_PATH.exists() else Path(__file__).parent.parent) / "manifest.yaml"


def get_source(config: Mapping[str, Any], catalog: ConfiguredAirbyteCatalog) -> YamlDeclarativeSource:
    return YamlDeclarativeSource(
        path_to_yaml=str(MANIFEST_PATH),
        catalog=catalog,
        config=config,
        state=StateBuilder().build(),
    )
