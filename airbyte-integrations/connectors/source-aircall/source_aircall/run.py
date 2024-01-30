#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_aircall import SourceAircall


def run():
    source = SourceAircall()
    launch(source, sys.argv[1:])
