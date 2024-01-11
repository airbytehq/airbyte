#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_smartsheets import SourceSmartsheets


def run():
    source = SourceSmartsheets()
    launch(source, sys.argv[1:])
