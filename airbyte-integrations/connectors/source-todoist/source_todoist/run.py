#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_todoist import SourceTodoist


def run():
    source = SourceTodoist()
    launch(source, sys.argv[1:])
