# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import os
import sys
from pathlib import Path

import pytest

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


os.environ["REQUEST_CACHE_PATH"] = "REQUEST_CACHE_PATH"


@pytest.fixture
def source_factory(connector_dir):
    sys.path.insert(0, str(connector_dir))

    def get_source(config, catalog, state=None):
        return YamlDeclarativeSource(path_to_yaml=str(connector_dir / "manifest.yaml"), config=config, catalog=catalog, state=state)

    yield get_source
    sys.path.remove(str(connector_dir))


@pytest.fixture(autouse=True)
def clear_cache_before_each_test():
    cache_dir = Path(os.environ["REQUEST_CACHE_PATH"])
    if cache_dir.is_dir():
        for cache_file in cache_dir.glob("*.sqlite"):
            cache_file.unlink()
