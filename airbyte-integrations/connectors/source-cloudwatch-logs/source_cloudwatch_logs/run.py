#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import sys

from airbyte_cdk.entrypoint import launch
from source_cloudwatch_logs.source import SourceCloudwatchLogs


def run() -> None:
    source = SourceCloudwatchLogs()
    launch(source, sys.argv[1:])
