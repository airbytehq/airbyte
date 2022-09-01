#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, MutableMapping, Optional

import pendulum
import requests
from source_amazon_ads.schemas import AttributionReportModel, Profile
from source_amazon_ads.streams.common import AmazonAdsStream

METRICS_MAP = {
    "PERFORMANCE": [
        "Click-throughs",
        "attributedDetailPageViewsClicks14d",
        "attributedAddToCartClicks14d",
        "attributedPurchases14d",
        "unitsSold14d",
        "attributedSales14d",
        "attributedTotalDetailPageViewsClicks14d",
        "attributedTotalAddToCartClicks14d",
        "attributedTotalPurchases14d",
        "totalUnitsSold14d",
        "totalAttributedSales14d",
    ],
    "PRODUCTS": [
        "attributedDetailPageViewsClicks14d",
        "attributedAddToCartClicks14d",
        "attributedPurchases14d",
        "unitsSold14d",
        "attributedSales14d",
        "brandHaloDetailPageViewsClicks14d",
        "brandHaloAttributedAddToCartClicks14d",
        "brandHaloAttributedPurchases14d",
        "brandHaloUnitsSold14d",
        "brandHaloAttributedSales14d",
        "attributedNewToBrandPurchases14d",
        "attributedNewToBrandUnitsSold14d",
        "attributedNewToBrandSales14d",
        "brandHaloNewToBrandPurchases14d",
        "brandHaloNewToBrandUnitsSold14d",
        "brandHaloNewToBrandSales14d",
    ],
}


class AttributionReport(AmazonAdsStream):
    """
    This stream corresponds to Amazon Advertising API - Attribution Reports
    https://advertising.amazon.com/API/docs/en-us/amazon-attribution-prod-3p/#/
    """

    model = AttributionReportModel
    primary_key = None
    data_field = "reports"
    page_size = 300
    report_type = ""

    _next_page_token_field = "cursorId"
    _current_profile_id = ""

    REPORT_DATE_FORMAT = "YYYYMMDD"
    CONFIG_DATE_FORMAT = "YYYY-MM-DD"
    REPORTING_PERIOD = 90

    def __init__(self, config: Mapping[str, Any], *args, **kwargs):
        self.start_date = config.get("start_date")
        if self.start_date:
            self.start_date = pendulum.from_format(self.start_date, self.CONFIG_DATE_FORMAT).date()

        self._req_start_date = ""
        self._req_end_date = ""

        self.report_type = config.get("attribution_report_type", "PERFORMANCE")

        super().__init__(config, *args, **kwargs)

    def _set_dates(self, profile: Profile):
        new_start_date = pendulum.now(tz=profile.timezone).subtract(days=1).date()
        new_end_date = pendulum.now(tz=profile.timezone).date()

        if self.start_date:
            new_start_date = max(self.start_date, new_end_date.subtract(days=self.REPORTING_PERIOD))

        self._req_start_date = new_start_date.format(self.REPORT_DATE_FORMAT)
        self._req_end_date = new_end_date.format(self.REPORT_DATE_FORMAT)

    @property
    def http_method(self) -> str:
        return "POST"

    def read_records(self, *args, **kvargs) -> Iterable[Mapping[str, Any]]:
        """
        Iterate through self._profiles list and send read all records for each profile.
        """
        for profile in self._profiles:
            self._set_dates(profile)
            self._current_profile_id = profile.profileId
            yield from super().read_records(*args, **kvargs)

    def request_headers(self, *args, **kvargs) -> MutableMapping[str, Any]:
        headers = super().request_headers(*args, **kvargs)
        headers["Amazon-Advertising-API-Scope"] = str(self._current_profile_id)
        return headers

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        stream_data = response.json()
        next_page_token = stream_data.get(self._next_page_token_field)
        if next_page_token:
            return {self._next_page_token_field: next_page_token}

    def path(self, **kvargs) -> str:
        return "/attribution/report"

    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        body = {
            "reportType": self.report_type,
            "count": self.page_size,
            "metrics": ",".join(METRICS_MAP[self.report_type]),
            "startDate": self._req_start_date,
            "endDate": self._req_end_date,
            "cursorId": "",
        }

        if next_page_token:
            body["cursorId"] = next_page_token[self._next_page_token_field]

        return body
