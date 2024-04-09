#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_coda import SourceCoda


def run():
    source = SourceCoda()
    launch(source, sys.argv[1:])
