#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from .destination import DestinationLangchainIngest

def run():
    destination = DestinationLangchainIngest()
    destination.run(sys.argv[1:])
