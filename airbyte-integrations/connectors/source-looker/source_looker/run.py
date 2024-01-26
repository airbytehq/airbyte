#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_looker import SourceLooker


def run():
    source = SourceLooker()
    launch(source, sys.argv[1:])
