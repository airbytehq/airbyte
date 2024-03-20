#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_orb import SourceOrb


def run():
    source = SourceOrb()
    launch(source, sys.argv[1:])
