# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
import sys

import ddtrace

from airbyte_cdk.entrypoint import launch
from source_hardcoded_records import SourceHardcodedRecords


# Automatically patch all supported libraries to enable tracing
ddtrace.patch_all()

# Set DataDog configuration options directly in your Python code
ddtrace.config.env = "dev"                          # Equivalent to DD_ENV
ddtrace.config.service = "source-hardcoded-records" # Equivalent to DD_SERVICE
ddtrace.config.version = "1.0.0"                    # Equivalent to DD_VERSION
ddtrace.config.agent_hostname = "localhost"         # Equivalent to DD_AGENT_HOST


def run() -> None:
    # Turn on tracing
    ddtrace.patch_all()

    # Initialize and launch the source
    source = SourceHardcodedRecords()
    launch(source, sys.argv[1:])


if __name__ == "__main__":
    run()
