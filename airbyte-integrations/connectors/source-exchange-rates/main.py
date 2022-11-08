#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_exchange_rates import SourceExchangeRates

if __name__ == "__main__":
    source = SourceExchangeRates()
    launch(source, sys.argv[1:])
