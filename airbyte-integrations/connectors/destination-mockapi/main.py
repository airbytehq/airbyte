#!/usr/bin/env python3
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.


import sys

from destination_mockapi.destination import DestinationMockapi

from airbyte_cdk.entrypoint import launch


def run():
    destination = DestinationMockapi()
    launch(destination, sys.argv[1:])


if __name__ == "__main__":
    run()
