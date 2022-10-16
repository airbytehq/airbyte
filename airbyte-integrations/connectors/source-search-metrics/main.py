#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_search_metrics import SourceSearchMetrics

if __name__ == "__main__":
    source = SourceSearchMetrics()
    launch(source, sys.argv[1:])
