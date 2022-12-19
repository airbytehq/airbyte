#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_railz_ai import SourceRailzAi

if __name__ == "__main__":
    source = SourceRailzAi()
    launch(source, sys.argv[1:])
