#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_yahoo_finance_price import SourceYahooFinancePrice


def run():
    source = SourceYahooFinancePrice()
    launch(source, sys.argv[1:])
