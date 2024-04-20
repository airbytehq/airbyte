#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_convex import SourceConvex


def run():
    source = SourceConvex()
    launch(source, sys.argv[1:])
