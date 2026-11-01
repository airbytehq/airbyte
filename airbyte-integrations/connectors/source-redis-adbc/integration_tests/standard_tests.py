# Copyright (c) 2026 Albert Wong
# SPDX-License-Identifier: MIT
"""Use the pinned CDK's standard source tests and acceptance scenarios."""

from pathlib import Path

from airbyte_cdk.test.standard_tests.util import create_connector_test_suite


TestSuite = create_connector_test_suite(connector_directory=Path(__file__).resolve().parent.parent)
