#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_bamboo_hr import SourceBambooHr

if __name__ == "__main__":
    source = SourceBambooHr()
    launch(source, sys.argv[1:])
