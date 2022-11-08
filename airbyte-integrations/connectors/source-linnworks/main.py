#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_linnworks import SourceLinnworks

if __name__ == "__main__":
    source = SourceLinnworks()
    launch(source, sys.argv[1:])
