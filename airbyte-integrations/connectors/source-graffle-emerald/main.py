#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_graffle_emerald import SourceGraffleEmerald

if __name__ == "__main__":
    source = SourceGraffleEmerald()
    launch(source, sys.argv[1:])
