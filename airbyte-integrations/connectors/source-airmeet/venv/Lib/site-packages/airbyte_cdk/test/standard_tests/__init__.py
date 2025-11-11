# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
'''FAST Airbyte Standard Tests

This module provides a set of base classes for declarative connector test suites.
The goal of this module is to provide a robust and extensible framework for testing Airbyte
connectors.

Example usage:

```python
# `test_airbyte_standards.py`
from airbyte_cdk.test import standard_tests

pytest_plugins = [
    "airbyte_cdk.test.standard_tests.pytest_hooks",
]


class TestSuiteSourcePokeAPI(standard_tests.DeclarativeSourceTestSuite):
    """Test suite for the source."""
```

Available test suites base classes:
- `DeclarativeSourceTestSuite`: A test suite for declarative sources.
- `SourceTestSuiteBase`: A test suite for sources.
- `DestinationTestSuiteBase`: A test suite for destinations.

'''

from airbyte_cdk.test.models.scenario import ConnectorTestScenario
from airbyte_cdk.test.standard_tests.connector_base import ConnectorTestSuiteBase
from airbyte_cdk.test.standard_tests.declarative_sources import (
    DeclarativeSourceTestSuite,
)
from airbyte_cdk.test.standard_tests.destination_base import DestinationTestSuiteBase
from airbyte_cdk.test.standard_tests.source_base import SourceTestSuiteBase

__all__ = [
    "ConnectorTestScenario",
    "ConnectorTestSuiteBase",
    "DeclarativeSourceTestSuite",
    "DestinationTestSuiteBase",
    "SourceTestSuiteBase",
]
