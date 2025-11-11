# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Models used for standard tests."""

from airbyte_cdk.test.models.outcome import ExpectedOutcome
from airbyte_cdk.test.models.scenario import ConnectorTestScenario

__all__ = [
    "ConnectorTestScenario",
    "ExpectedOutcome",
]
