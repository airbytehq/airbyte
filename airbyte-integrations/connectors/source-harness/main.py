#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_harness import SourceHarness

if __name__ == "__main__":
    source = SourceHarness()
    launch(source, sys.argv[1:])
