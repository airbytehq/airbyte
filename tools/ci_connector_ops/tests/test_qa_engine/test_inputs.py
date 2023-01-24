#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pandas as pd
import pytest

from ci_connector_ops.qa_engine import inputs

@pytest.mark.parametrize("catalog_url", [inputs.OSS_CATALOG_URL, inputs.CLOUD_CATALOG_URL])
def test_fetch_remote_catalog(catalog_url):
    catalog = inputs.fetch_remote_catalog(catalog_url)
    assert isinstance(catalog, pd.DataFrame)
    expected_columns = ["connector_type", "connector_definition_id"]
    assert all(expected_column in catalog.columns for expected_column in expected_columns)
    assert set(catalog.connector_type.unique()) == {"source", "destination"}

def test_fetch_adoption_metrics_per_connector_version():
    expected_columns = {
        "connector_definition_id",
        "connector_version",
        "number_of_connections",
        "number_of_users",
        "sync_success_rate",
    }

    adoption_metrics_per_connector_version = inputs.fetch_adoption_metrics_per_connector_version()
    assert len(adoption_metrics_per_connector_version) == 0
    assert set(adoption_metrics_per_connector_version.columns) == expected_columns
