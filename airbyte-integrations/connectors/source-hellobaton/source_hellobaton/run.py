#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_hellobaton import SourceHellobaton


def run():
    source = SourceHellobaton()
    launch(source, sys.argv[1:])
