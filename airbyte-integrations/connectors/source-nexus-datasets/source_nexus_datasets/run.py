#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch

from .source import SourceNexusDatasets


def run():
    source = SourceNexusDatasets()
    launch(source, sys.argv[1:])
