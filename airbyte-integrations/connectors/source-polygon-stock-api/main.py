#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_polygon_stock_api import SourcePolygonStockApi

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourcePolygonStockApi()
    launch(source, sys.argv[1:])
