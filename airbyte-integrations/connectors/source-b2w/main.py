#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_b2w import SourceB2W

if __name__ == "__main__":
    source = SourceB2W()
    launch(source, sys.argv[1:])
