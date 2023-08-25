#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_yahoo_finance_price import SourceYahooFinancePrice

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceYahooFinancePrice()
    launch(source, sys.argv[1:])
