# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path
from typing import Any, Mapping, Optional

import pytest

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.state_builder import StateBuilder


MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"
RESPONSES_PATH = Path(__file__).parent / "responses"


@pytest.fixture
def config() -> Mapping[str, Any]:
    return {
        "api_key": "test-api-key",
        "project_id": "d7b46c01-32a3-4f74-80d3-616a3c18fb6b",
        "start_date": "2024-01-01T00:00:00Z",
    }


def build_source(config: Mapping[str, Any], state: Optional[list] = None) -> YamlDeclarativeSource:
    catalog = CatalogBuilder().build()
    state = StateBuilder().build() if state is None else state
    return YamlDeclarativeSource(path_to_yaml=str(MANIFEST_PATH), catalog=catalog, config=config, state=state)


def load_response(name: str) -> Mapping[str, Any]:
    with open(RESPONSES_PATH / name) as response_file:
        return json.load(response_file)
