#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, List, Mapping, Optional

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from requests.exceptions import HTTPError
from source_amazon_ads.schemas import AttributionReportModel
from source_amazon_ads.streams.common import AmazonAdsStream

BRAND_REFERRAL_BONUS = "brb_bonus_amount"

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
    custom_metrics = []
    group_by = ""

    _next_page_token_field = "cursorId"
    _current_profile_id = ""

    REPORT_DATE_FORMAT = "YYYYMMDD"
    CONFIG_DATE_FORMAT = "YYYY-MM-DD"
    REPORTING_PERIOD = 90

    def __init__(self, config: Mapping[str, Any], *args, **kwargs):
        self._start_date = config.get("start_date")
        super().__init__(config, *args, **kwargs)

    @property
    def metrics(self):
        return METRICS_MAP[self.report_type] + self.custom_metrics

    @property
    def http_method(self) -> str:
        return "POST"

    def path(self, **kwargs) -> str:
        return "/attribution/report"

    def get_json_schema(self):
        schema = super().get_json_schema()
        metrics_type_map = {metric: {"type": ["null", "string"]} for metric in self.metrics}
        schema["properties"].update(metrics_type_map)
        return schema

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        for profile in self._profiles:
            start_date = pendulum.now(tz=profile.timezone).subtract(days=1).date()
            end_date = pendulum.now(tz=profile.timezone).date()
            if self._start_date:
                start_date = max(self._start_date, end_date.subtract(days=self.REPORTING_PERIOD))

            yield {
                "profileId": profile.profileId,
                "startDate": start_date.format(self.REPORT_DATE_FORMAT),
                "endDate": end_date.format(self.REPORT_DATE_FORMAT),
            }

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        try:
            yield from super().read_records(sync_mode, cursor_field, stream_slice, stream_state)
        except HTTPError as e:
            if e.response.status_code == 400:
                if e.response.json()["message"] == "This profileID is not authorized to use Amazon Attribution":
                    self.logger.warning(f"This profileID {stream_slice['profileId']} is not authorized to use Amazon Attribution")
                    return
            raise e

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        headers = super().request_headers(stream_state, stream_slice, next_page_token)
        headers["Amazon-Advertising-API-Scope"] = str(stream_slice["profileId"])
        return headers

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        stream_data = response.json()
        next_page_token = stream_data.get(self._next_page_token_field)
        if next_page_token:
            return {self._next_page_token_field: next_page_token}

    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:

        body = {
            "reportType": self.report_type,
            "count": self.page_size,
            "metrics": ",".join(self.metrics),
            "startDate": stream_slice["startDate"],
            "endDate": stream_slice["endDate"],
            self._next_page_token_field: "",
        }

        if self.group_by:
            body["groupBy"] = self.group_by

        if next_page_token:
            body[self._next_page_token_field] = next_page_token[self._next_page_token_field]

        return body


class AttributionReportProducts(AttributionReport):
    report_type = "PRODUCTS"
    group_by = ""


class AttributionReportPerformanceCreative(AttributionReport):
    report_type = "PERFORMANCE"
    group_by = "CREATIVE"


class AttributionReportPerformanceAdgroup(AttributionReport):
    report_type = "PERFORMANCE"
    custom_metrics = [BRAND_REFERRAL_BONUS]
    group_by = "ADGROUP"


class AttributionReportPerformanceCampaign(AttributionReport):
    report_type = "PERFORMANCE"
    custom_metrics = [BRAND_REFERRAL_BONUS]
    group_by = "CAMPAIGN"
