#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_us_census import SourceUsCensus


def run():
    source = SourceUsCensus()
    launch(source, sys.argv[1:])
