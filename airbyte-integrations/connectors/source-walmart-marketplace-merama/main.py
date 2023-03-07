#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_walmart_marketplace import SourceWalmartMarketplace

if __name__ == "__main__":
    source = SourceWalmartMarketplace()
    launch(source, sys.argv[1:])
