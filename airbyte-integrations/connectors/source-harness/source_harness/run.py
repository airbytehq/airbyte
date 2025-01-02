#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_harness import SourceHarness

from airbyte_cdk.entrypoint import launch


def run():
    source = SourceHarness()
    launch(source, sys.argv[1:])
