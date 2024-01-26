#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_whisky_hunter import SourceWhiskyHunter


def run():
    source = SourceWhiskyHunter()
    launch(source, sys.argv[1:])
