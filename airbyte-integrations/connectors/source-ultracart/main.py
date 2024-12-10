#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_ultracart import SourceUltracart

if __name__ == "__main__":
    source = SourceUltracart()
    launch(source, sys.argv[1:])
