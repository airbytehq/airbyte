#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_pagerduty import SourcePagerduty

from airbyte_cdk.entrypoint import launch


def run():
    source = SourcePagerduty()
    launch(source, sys.argv[1:])
