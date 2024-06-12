#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_greenhouse import SourceGreenhouse


def run():
    source = SourceGreenhouse()
    launch(source, sys.argv[1:])
