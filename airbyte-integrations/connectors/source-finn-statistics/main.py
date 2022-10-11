#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_finn_statistics import SourceFinnStatistics

if __name__ == "__main__":
    source = SourceFinnStatistics()
    launch(source, sys.argv[1:])
