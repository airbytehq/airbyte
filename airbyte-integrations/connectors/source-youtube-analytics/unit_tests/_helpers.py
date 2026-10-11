#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

"""Shared helpers for `source-youtube-analytics` unit tests."""

from pathlib import Path
from typing import Any, Mapping, Optional

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.state_builder import StateBuilder


_MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"


def get_source(config: Mapping[str, Any], state: Optional[list] = None) -> YamlDeclarativeSource:
    """Instantiate a `YamlDeclarativeSource` for `source-youtube-analytics` using its manifest."""
    catalog = CatalogBuilder().build()
    state = StateBuilder().build() if state is None else state
    return YamlDeclarativeSource(path_to_yaml=str(_MANIFEST_PATH), catalog=catalog, config=config, state=state)
