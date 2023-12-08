#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_gainsight_px import SourceGainsightPx

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceGainsightPx()
    launch(source, sys.argv[1:])
