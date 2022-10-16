#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_square import SourceSquare

if __name__ == "__main__":
    source = SourceSquare()
    launch(source, sys.argv[1:])
