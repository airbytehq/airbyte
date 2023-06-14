#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from datetime import datetime
import pandas as pd
import pytest

from ci_connector_ops.qa_engine.constants import OSS_CATALOG_URL, CLOUD_CATALOG_URL
from ci_connector_ops.qa_engine.inputs import fetch_remote_catalog


@pytest.fixture(scope="module")
def oss_catalog():
    return fetch_remote_catalog(OSS_CATALOG_URL)


@pytest.fixture(scope="module")
def cloud_catalog():
    return fetch_remote_catalog(CLOUD_CATALOG_URL)


@pytest.fixture(scope="module")
def adoption_metrics_per_connector_version():
    return pd.DataFrame(
        [
            {
                "connector_definition_id": "dfd88b22-b603-4c3d-aad7-3701784586b1",
                "connector_version": "2.0.0",
                "number_of_connections": 0,
                "number_of_users": 0,
                "succeeded_syncs_count": 0,
                "failed_syncs_count": 0,
                "total_syncs_count": 0,
                "sync_success_rate": 0.0,
            }
        ]
    )


@pytest.fixture
def dummy_qa_report() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "connector_type": "source",
                "connector_name": "test",
                "connector_technical_name": "source-test",
                "connector_definition_id": "foobar",
                "connector_version": "0.0.0",
                "release_stage": "alpha",
                "is_on_cloud": False,
                "is_appropriate_for_cloud_use": True,
                "latest_build_is_successful": True,
                "documentation_is_available": False,
                "number_of_connections": 0,
                "number_of_users": 0,
                "sync_success_rate": 0.99,
                "total_syncs_count": 0,
                "failed_syncs_count": 0,
                "succeeded_syncs_count": 0,
                "is_eligible_for_promotion_to_cloud": True,
                "report_generation_datetime": datetime.utcnow(),
            }
        ]
    )
