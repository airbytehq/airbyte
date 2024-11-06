#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from destination_timeplus import DestinationTimeplus


def run():
    destination = DestinationTimeplus()
    destination.run(sys.argv[1:])
