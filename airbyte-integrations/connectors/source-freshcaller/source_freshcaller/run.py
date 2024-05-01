#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_freshcaller import SourceFreshcaller


def run():
    source = SourceFreshcaller()
    launch(source, sys.argv[1:])
