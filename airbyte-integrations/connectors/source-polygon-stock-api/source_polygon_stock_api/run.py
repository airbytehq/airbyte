#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_polygon_stock_api import SourcePolygonStockApi


def run():
    source = SourcePolygonStockApi()
    launch(source, sys.argv[1:])
