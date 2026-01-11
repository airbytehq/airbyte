#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import sys
from source_cloudwatch_logs.source import SourceCloudwatchLogs
from airbyte_cdk.entrypoint import launch


def run() -> None:
    source = SourceCloudwatchLogs()
    launch(source, sys.argv[1:])
