#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_dolead_exchange_rates import SourceDoleadExchangeRates

if __name__ == "__main__":
    source = SourceDoleadExchangeRates()
    launch(source, sys.argv[1:])
