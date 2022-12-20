#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_elevate_rockset import SourceElevateRockset

if __name__ == "__main__":
    source = SourceElevateRockset()
    launch(source, sys.argv[1:])
