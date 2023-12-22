#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_gainsight_cs import SourceGainsightCs

if __name__ == "__main__":
    source = SourceGainsightCs()
    launch(source, sys.argv[1:])
