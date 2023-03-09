#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import re

import pandas as pd
import pytest

from ci_connector_ops.qa_engine import inputs, enrichments

@pytest.fixture
def enriched_catalog() -> pd.DataFrame:
    return enrichments.get_enriched_catalog(inputs.OSS_CATALOG, inputs.CLOUD_CATALOG)

@pytest.fixture
def enriched_catalog_columns(enriched_catalog: pd.DataFrame) -> set:
    return set(enriched_catalog.columns)

def test_merge_performed_correctly(enriched_catalog):
    assert len(enriched_catalog) == len(inputs.OSS_CATALOG)

def test_new_columns_are_added(enriched_catalog_columns):
    expected_new_columns = {
        "is_on_cloud",
        "connector_name",
        "connector_technical_name",
        "connector_version"
    }
    assert expected_new_columns.issubset(enriched_catalog_columns)

def test_no_column_are_removed_and_lowercased(enriched_catalog_columns):
    for column in inputs.OSS_CATALOG:
        assert re.sub(r"(?<!^)(?=[A-Z])", "_", column).lower() in enriched_catalog_columns

def test_release_stage_not_null(enriched_catalog):
    assert len(enriched_catalog["release_stage"].dropna()) == len(enriched_catalog["release_stage"])
