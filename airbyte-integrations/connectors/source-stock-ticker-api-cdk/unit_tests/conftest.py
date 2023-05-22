#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import datetime

import pytest
from source_stock_ticker_api_cdk.source import StockPrices


@pytest.fixture
def stream():
    return StockPrices(
        stock_ticker="TSLA",
        start_date=datetime.strptime("2022-07-07", "%Y-%m-%d"),
        end_date=datetime.strptime("2022-08-08", "%Y-%m-%d"),
        time_step=30
    )
