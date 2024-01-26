#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_gnews import SourceGnews


def run():
    source = SourceGnews()
    launch(source, sys.argv[1:])
