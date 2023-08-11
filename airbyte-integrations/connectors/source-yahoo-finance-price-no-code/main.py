#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_yahoo_finance_price_no_code import SourceYahooFinancePriceNoCode

if __name__ == "__main__":
    source = SourceYahooFinancePriceNoCode()
    launch(source, sys.argv[1:])
