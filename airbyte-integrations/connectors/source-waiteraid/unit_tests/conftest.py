# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest
from requests_mock import Mocker

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


def get_source(config, catalog):
    return YamlDeclarativeSource(
        path_to_yaml=str(Path(__file__).parent.parent / "manifest.yaml"),
        config=config,
        catalog=catalog,
        state=[],
    )


@pytest.fixture
def requests_mock():
    with Mocker(case_sensitive=True) as mocker:
        yield mocker
