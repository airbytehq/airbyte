#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_exchange_rate_api import SourceExchangeRateApi

if __name__ == "__main__":
    source = SourceExchangeRateApi()
    launch(source, sys.argv[1:])
