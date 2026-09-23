# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Airbyte CDK standard connector tests (spec / check / discover / read contract).

The scenarios below run in-process against the fake HANA, so they never need a real server.
acceptance-test-config.yml stays free for the regular acceptance tests against a real HANA
(secrets/config.json). Docker image tests are marked `image_tests` and deselected by default.
"""

from pathlib import Path

import pytest
from source_sap_hana import SourceSapHana

from airbyte_cdk.test.models import ConnectorTestScenario
from airbyte_cdk.test.standard_tests import SourceTestSuiteBase


@pytest.fixture(autouse=True)
def seeded_fake_hana(hana):
    hana.add_table(
        "ACDOCA",
        [("RCLNT", "NVARCHAR"), ("BELNR", "NVARCHAR"), ("DOCLN", "NVARCHAR"), ("HSL", "DECIMAL")],
        [("100", "0000000001", "000001", -1.5), ("100", "0000000001", "000002", 1.5)],
        pk=["RCLNT", "BELNR", "DOCLN"],
    )
    hana.add_table("MAKT", [("MATNR", "NVARCHAR"), ("MAKTX", "NVARCHAR")], [("M1", "Libro")])
    return hana


FAKE_HANA_SCENARIOS = [
    ConnectorTestScenario(config_path=Path("integration_tests/fake_hana_config.json"), status="succeed"),
    ConnectorTestScenario(config_path=Path("integration_tests/fake_hana_invalid_config.json"), status="failed"),
]


class TestSourceSapHanaStandard(SourceTestSuiteBase):
    connector = SourceSapHana

    @classmethod
    def get_scenarios(cls) -> list[ConnectorTestScenario]:
        return FAKE_HANA_SCENARIOS
