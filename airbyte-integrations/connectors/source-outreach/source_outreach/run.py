#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import sys

from source_outreach import SourceOutreach

from airbyte_cdk.entrypoint import launch


def run():
    source = SourceOutreach()
    launch(source, sys.argv[1:])
