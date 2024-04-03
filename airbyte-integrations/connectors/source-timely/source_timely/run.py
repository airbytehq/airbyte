#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_timely import SourceTimely


def run():
    source = SourceTimely()
    launch(source, sys.argv[1:])
