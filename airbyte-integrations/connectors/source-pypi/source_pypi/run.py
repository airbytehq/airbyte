#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_pypi import SourcePypi


def run():
    source = SourcePypi()
    launch(source, sys.argv[1:])
