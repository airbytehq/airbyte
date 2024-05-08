#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_exchange_rates import SourceExchangeRates


def run():
    source = SourceExchangeRates()
    launch(source, sys.argv[1:])
