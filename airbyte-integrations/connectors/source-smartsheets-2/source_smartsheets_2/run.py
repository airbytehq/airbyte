#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch

from .source import SourceSmartsheets_2


def run():
    source = SourceSmartsheets_2()
    launch(source, sys.argv[1:])
