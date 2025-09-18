#!/usr/bin/env python3

import sys
from airbyte_cdk.entrypoint import launch
from destination_mockapi.destination import DestinationMockapi

def run():
    destination = DestinationMockapi()
    launch(destination, sys.argv[1:])

if __name__ == "__main__":
    run()