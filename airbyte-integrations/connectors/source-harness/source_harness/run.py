#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_harness import SourceHarness


def run():
    source = SourceHarness()
    launch(source, sys.argv[1:])
