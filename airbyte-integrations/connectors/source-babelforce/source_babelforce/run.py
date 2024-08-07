#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch

from .source import SourceBabelforce


def run():
    source = SourceBabelforce()
    launch(source, sys.argv[1:])
