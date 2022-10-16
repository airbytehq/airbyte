#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_lever_hiring import SourceLeverHiring

if __name__ == "__main__":
    source = SourceLeverHiring()
    launch(source, sys.argv[1:])
