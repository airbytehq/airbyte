#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_exchange_rates import SourceExchangeRates

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceExchangeRates()
    launch(source, sys.argv[1:])
