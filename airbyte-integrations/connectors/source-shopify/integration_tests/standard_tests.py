# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
"""FAST Airbyte Standard Tests for source-shopify, run in-process by `poe test-standard-tests`.

With the airbyte-cdk version this connector pins (before 7.36), the in-process `test_basic_read`
reads every discovered stream, for every config that acceptance-test-config.yml lists (connection
configs included). For this connector that read is the size of the old acceptance-test basic read
(its `timeout_seconds` is 4800) and does not finish in the CI time budget. This suite skips that
one test and keeps every other in-process test. The `basic_read` coverage stays with
`airbyte-cdk image test`, which reads the connector's suggested streams from the built image.

Remove this file when the connector pins a CDK that runs `basic_read` only for its basic_read
configs and its basic_read entries declare a `configured_catalog_path`.

The file is not named `test_*.py`, so that `poe test-integration-tests` does not collect it.
"""

from pathlib import Path

import pytest

from airbyte_cdk.test.standard_tests.util import create_connector_test_suite


pytest_plugins = ["airbyte_cdk.test.standard_tests.pytest_hooks"]

_GeneratedSuite = create_connector_test_suite(connector_directory=Path(__file__).resolve().parent.parent)


class TestAirbyteStandardTests(_GeneratedSuite):  # type: ignore[misc, valid-type]
    """The generated in-process suite, without the full-catalog `test_basic_read`."""

    def test_basic_read(self, scenario: object) -> None:
        pytest.skip(
            "The in-process basic read of every discovered stream for every config does not finish "
            "in the CI time budget; `airbyte-cdk image test` covers basic_read."
        )
