#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_hubspot import SourceHubspot


def run():
    source = SourceHubspot()
    launch(source, sys.argv[1:])
