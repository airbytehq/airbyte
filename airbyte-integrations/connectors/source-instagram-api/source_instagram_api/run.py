# temp file change
#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch

from .source import SourceInstagramApi


def run():
    source = SourceInstagramApi()
    launch(source, sys.argv[1:])
