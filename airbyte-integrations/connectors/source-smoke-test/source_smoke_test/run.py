# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
"""Entry point for source-smoke-test."""

import sys

from airbyte_cdk.entrypoint import launch
from source_smoke_test.source import SourceSmokeTest


def run() -> None:
    """Run the smoke test source connector."""
    launch(SourceSmokeTest(), sys.argv[1:])
