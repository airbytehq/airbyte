# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


import sys

from airbyte_cdk.entrypoint import launch
from source_hardcoded_records import SourceHardcodedRecords


def run():
    source = SourceHardcodedRecords()
    launch(source, sys.argv[1:])


if __name__ == "__main__":
    run()
