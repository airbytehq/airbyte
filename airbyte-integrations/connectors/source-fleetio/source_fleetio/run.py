#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_fleetio import SourceFleetio


def run():
    source = SourceFleetio()
    launch(source, sys.argv[1:])
