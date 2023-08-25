#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_open_exchange_rates import SourceOpenExchangeRates

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceOpenExchangeRates()
    launch(source, sys.argv[1:])
