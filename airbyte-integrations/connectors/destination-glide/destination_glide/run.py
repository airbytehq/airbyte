#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from .destination import DestinationGlide

def run():
    destination = DestinationGlide()
    destination.run(sys.argv[1:])
