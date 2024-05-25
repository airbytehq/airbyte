#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_linnworks import SourceLinnworks


def run():
    source = SourceLinnworks()
    launch(source, sys.argv[1:])
