# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import sys
from pathlib import Path
from typing import Any, List, Mapping, Optional

from airbyte_cdk.models import AirbyteStateMessage, ConfiguredAirbyteCatalog
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]

_CI_SOURCE_PATH = Path("/airbyte/integration_code/source_declarative_manifest")
_SOURCE_PATH = _CI_SOURCE_PATH if _CI_SOURCE_PATH.exists() else Path(__file__).resolve().parents[1]

sys.path.append(str(_SOURCE_PATH))  # lets the CDK import the connector's components.py


def get_source(
    config: Mapping[str, Any],
    catalog: ConfiguredAirbyteCatalog,
    state: Optional[List[AirbyteStateMessage]] = None,
) -> YamlDeclarativeSource:
    return YamlDeclarativeSource(path_to_yaml=str(_SOURCE_PATH / "manifest.yaml"), catalog=catalog, config=config, state=state)
