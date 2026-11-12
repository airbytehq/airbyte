# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path
from typing import Any, Mapping, Optional

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


MANIFEST_PATH = Path(__file__).parents[1] / "manifest.yaml"


def get_source(config: Mapping[str, Any], state: Optional[list] = None) -> YamlDeclarativeSource:
    return YamlDeclarativeSource(path_to_yaml=str(MANIFEST_PATH), config=config, catalog=None, state=state)
