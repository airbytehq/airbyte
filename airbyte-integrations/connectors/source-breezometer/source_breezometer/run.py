#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_breezometer import SourceBreezometer


def run():
    source = SourceBreezometer()
    launch(source, sys.argv[1:])
