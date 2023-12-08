#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_us_census import SourceUsCensus

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceUsCensus()
    launch(source, sys.argv[1:])
