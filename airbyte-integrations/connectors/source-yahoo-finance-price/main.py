#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_yahoo_finance_price import SourceYahooFinancePrice

if __name__ == "__main__":
    source = SourceYahooFinancePrice()
    launch(source, sys.argv[1:])
