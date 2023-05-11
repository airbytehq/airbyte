#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_open_exchange_rates import SourceOpenExchangeRates

if __name__ == "__main__":
    source = SourceOpenExchangeRates()
    launch(source, sys.argv[1:])
