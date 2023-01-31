#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_appmetrika_logs_stream_api import SourceAppmetrikaLogsStreamApi

if __name__ == "__main__":
    source = SourceAppmetrikaLogsStreamApi()
    launch(source, sys.argv[1:])
