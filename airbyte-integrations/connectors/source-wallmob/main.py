#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_wallmob import SourceWallmob

if __name__ == "__main__":
    source = SourceWallmob()
    launch(source, sys.argv[1:])
