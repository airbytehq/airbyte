# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


def _manifest_dir() -> Path:
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if ci_path.exists():
        return ci_path
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def streams():
    config = {"access_token": "test-token", "start_date": "2023-01-01T00:00:00Z"}
    source = YamlDeclarativeSource(path_to_yaml=str(_manifest_dir() / "manifest.yaml"), config=config)
    return {stream.name: stream for stream in source.streams(config)}
