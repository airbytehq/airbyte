# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


import sys

from airbyte_cdk.entrypoint import launch
from airbyte_cdk.test.source_hardcoded_records.source import SourceHardcodedRecords


def run():
    source = SourceHardcodedRecords()
    launch(source, sys.argv[1:])


if __name__ == "__main__":
    run()
