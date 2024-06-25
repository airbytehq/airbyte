#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch

from .source import SourceLinkedinPages


def run():
    source = SourceLinkedinPages()
    launch(source, sys.argv[1:])
