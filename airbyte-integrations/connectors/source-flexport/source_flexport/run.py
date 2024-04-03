#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_flexport import SourceFlexport


def run():
    source = SourceFlexport()
    launch(source, sys.argv[1:])
