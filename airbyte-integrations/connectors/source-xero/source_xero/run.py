#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_xero import SourceXero

from airbyte_cdk.entrypoint import launch


def run():
    source = SourceXero()
    launch(source, sys.argv[1:])
