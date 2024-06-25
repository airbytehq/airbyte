#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_outreach import SourceOutreach


def run():
    source = SourceOutreach()
    launch(source, sys.argv[1:])
