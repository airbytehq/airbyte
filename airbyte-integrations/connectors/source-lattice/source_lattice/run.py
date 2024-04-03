#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from .source import SourceLattice

def run():
    source = SourceLattice()
    launch(source, sys.argv[1:])
