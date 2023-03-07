#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_polygon_stock_api import SourcePolygonStockApi

if __name__ == "__main__":
    source = SourcePolygonStockApi()
    launch(source, sys.argv[1:])
