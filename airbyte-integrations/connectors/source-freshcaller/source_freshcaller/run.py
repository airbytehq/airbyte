#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_freshcaller import SourceFreshcaller

from airbyte_cdk.entrypoint import launch


def run():
    source = SourceFreshcaller()
    launch(source, sys.argv[1:])
