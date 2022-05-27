#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import sys

from airbyte_cdk.entrypoint import launch
from source_polygon import SourceStockTickerAPI

if __name__ == "__main__":
    source = SourceStockTickerAPI()
    launch(source, sys.argv[1:])
