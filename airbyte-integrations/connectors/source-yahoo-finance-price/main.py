#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_yahoo_finance_price import SourceYahooFinance

if __name__ == "__main__":
    source = SourceYahooFinance()
    launch(source, sys.argv[1:])
