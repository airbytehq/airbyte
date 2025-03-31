#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from .destination import DestinationTestconnector

def run():
    destination = DestinationTestconnector()
    destination.run(sys.argv[1:])
