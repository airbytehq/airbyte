#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from typing import Any, Mapping

from .bing_ads_reporting_service_stream import BingAdsReportingServiceStream


class BingAdsReportingServicePerformanceStream(BingAdsReportingServiceStream, ABC):
    def get_start_date(self, stream_state: Mapping[str, Any] = None, account_id: str = None):
        start_date = super().get_start_date(stream_state, account_id)

        if self.config.get("lookback_window") and start_date:
            # Datetime subtract won't work with days = 0
            # it'll output an AirbyteError
            return start_date.subtract(days=self.config["lookback_window"])
        else:
            return start_date
