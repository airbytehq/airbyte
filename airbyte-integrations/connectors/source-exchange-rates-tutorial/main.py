#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_exchange_rates_tutorial import SourceExchangeRatesTutorial

if __name__ == "__main__":
    source = SourceExchangeRatesTutorial()
    launch(source, sys.argv[1:])
