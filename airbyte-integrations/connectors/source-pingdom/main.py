#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_pingdom import SourcePingdom

if __name__ == "__main__":
    source = SourcePingdom()
    launch(source, sys.argv[1:])
