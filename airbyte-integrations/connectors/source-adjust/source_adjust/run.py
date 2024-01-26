#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_adjust import SourceAdjust


def run():
    source = SourceAdjust()
    launch(source, sys.argv[1:])
