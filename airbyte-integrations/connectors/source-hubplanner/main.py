#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_hubplanner import SourceHubplanner

if __name__ == "__main__":
    source = SourceHubplanner()
    launch(source, sys.argv[1:])
