#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch

from .source import SourceOrb


def run():
    source = SourceOrb()
    launch(source, sys.argv[1:])
