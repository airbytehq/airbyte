#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_orbit import SourceOrbit


def run():
    source = SourceOrbit()
    launch(source, sys.argv[1:])
