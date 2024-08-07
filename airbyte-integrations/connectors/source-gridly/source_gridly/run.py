#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_gridly import SourceGridly


def run():
    source = SourceGridly()
    launch(source, sys.argv[1:])
