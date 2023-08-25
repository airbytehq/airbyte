#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_bamboo_hr import SourceBambooHr

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceBambooHr()
    launch(source, sys.argv[1:])
