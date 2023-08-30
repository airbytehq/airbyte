#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_wildberries_statistics import SourceWildberriesStatistics

if __name__ == "__main__":
    source = SourceWildberriesStatistics()
    launch(source, sys.argv[1:])
