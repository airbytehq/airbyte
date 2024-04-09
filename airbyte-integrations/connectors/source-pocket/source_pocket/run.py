#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_pocket import SourcePocket


def run():
    source = SourcePocket()
    launch(source, sys.argv[1:])
