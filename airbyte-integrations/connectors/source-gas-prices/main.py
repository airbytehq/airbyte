#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_gas_prices import SourceGasPrices

if __name__ == "__main__":
    source = SourceGasPrices()
    launch(source, sys.argv[1:])
