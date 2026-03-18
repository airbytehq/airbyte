# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
"""Entry point for source-smoke-test.

Delegates to the PyAirbyte CLI smoke test source implementation.
"""

import sys

from airbyte.cli.smoke_test_source.source import SourceSmokeTest
from airbyte_cdk.entrypoint import launch


def run() -> None:
    """Run the smoke test source connector."""
    launch(SourceSmokeTest(), sys.argv[1:])
