#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import pytest
from pathlib import Path
from typing import Any

from airbyte_cdk import models
from airbyte_cdk.entrypoint import launch

from source_dbt_duckdb import SourceDbtDuckDB


SAMPLE_CATALOG_PATH = Path(__file__).parent.parent / "sample-catalog.json"
SAMPLE_CONFIGURED_CATALOG_PATH = (
    Path(__file__).parent.parent / "sample-configured-catalog.json"
)
SAMPLE_CONFIG_PATH = Path(__file__).parent.parent / "sample-config.json"


@pytest.fixture
def sample_catalog() -> models.AirbyteCatalog:
    catalog = json.loads(SAMPLE_CATALOG_PATH.read_text())
    return models.AirbyteCatalog.parse_obj(catalog)


@pytest.fixture
def sample_configured_catalog() -> models.ConfiguredAirbyteCatalog:
    catalog = json.loads(SAMPLE_CONFIGURED_CATALOG_PATH.read_text())
    return models.ConfiguredAirbyteCatalog.parse_obj(catalog)


@pytest.fixture
def sample_config() -> dict[str, Any]:
    return json.loads(SAMPLE_CONFIG_PATH.read_text())


def test_test_sync(sample_configured_catalog, sample_config):
    """Test that we can run a sync."""
    launch(
        SourceDbtDuckDB(),
        [
            "read",
            f"--catalog={SAMPLE_CONFIGURED_CATALOG_PATH}",
            f"--config={SAMPLE_CONFIG_PATH}",
        ],
    )
