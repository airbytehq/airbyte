# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
"""FAST Airbyte Standard Tests for source-smoke-test, run in-process by `poe test-standard-tests`.

The suite that `poe test-standard-tests` generates cannot build the source: the `source_smoke_test`
package does not export `SourceSmokeTest`; `run.py` imports it from `source_smoke_test.source`. This
suite builds it the way `run.py` does.

The file is not named `test_*.py`, so that `poe test-integration-tests` does not collect it.
"""

from typing import Any

from source_smoke_test.source import SourceSmokeTest

from airbyte_cdk.test.standard_tests import SourceTestSuiteBase


pytest_plugins = ["airbyte_cdk.test.standard_tests.pytest_hooks"]


class TestAirbyteStandardTests(SourceTestSuiteBase):
    """The FAST Airbyte Standard Tests, with the source built as `run.py` builds it."""

    @classmethod
    def create_connector(cls, scenario: Any) -> Any:
        return SourceSmokeTest()
