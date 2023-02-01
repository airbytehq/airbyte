#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_convex import SourceConvex

if __name__ == "__main__":
    source = SourceConvex()
    launch(source, sys.argv[1:])
