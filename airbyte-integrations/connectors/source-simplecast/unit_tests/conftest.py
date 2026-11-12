# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from collections.abc import Callable
from pathlib import Path

import pytest

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


@pytest.fixture
def get_source() -> Callable[[dict[str, str]], YamlDeclarativeSource]:
    def _get_source(config: dict[str, str]) -> YamlDeclarativeSource:
        return YamlDeclarativeSource(
            path_to_yaml=str(Path(__file__).parent.parent / "manifest.yaml"),
            config=config,
        )

    return _get_source
