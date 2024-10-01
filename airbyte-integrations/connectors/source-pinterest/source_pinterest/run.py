#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_pinterest import SourcePinterest


def run():
    source = SourcePinterest()
    launch(source, sys.argv[1:])
