#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_hi_platform import SourceHiPlatform

if __name__ == "__main__":
    source = SourceHiPlatform()
    launch(source, sys.argv[1:])
