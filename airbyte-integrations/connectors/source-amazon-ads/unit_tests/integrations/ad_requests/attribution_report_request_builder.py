# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import datetime
import json
from collections import OrderedDict
from typing import Any, Dict, List, Optional


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

from .base_request_builder import AmazonAdsBaseRequestBuilder


class AttributionReportRequestBuilder(AmazonAdsBaseRequestBuilder):
    @classmethod
    def products_endpoint(
        cls, client_id: str, client_access_token: str, profile_id: str, start_date: datetime.date, end_date: datetime.date, limit: int = 300
    ) -> "AttributionReportRequestBuilder":
        return (
            cls("attribution/report")
            .with_client_id(client_id)
            .with_client_access_token(client_access_token)
            .with_profile_id(profile_id)
            .with_report_type("PRODUCTS")
            .with_metrics(METRICS_MAP["PRODUCTS"])
            .with_limit(limit)
            .with_start_date(start_date)
            .with_end_date(end_date)
        )

    @classmethod
    def performance_adgroup_endpoint(
        cls, client_id: str, client_access_token: str, profile_id: str, start_date: datetime.date, end_date: datetime.date, limit: int = 300
    ) -> "AttributionReportRequestBuilder":
        return (
            cls("attribution/report")
            .with_client_id(client_id)
            .with_client_access_token(client_access_token)
            .with_profile_id(profile_id)
            .with_report_type("PERFORMANCE")
            .with_metrics(METRICS_MAP["PERFORMANCE"] + [BRAND_REFERRAL_BONUS])
            .with_limit(limit)
            .with_start_date(start_date)
            .with_end_date(end_date)
            .with_grouping("ADGROUP")
        )

    @classmethod
    def performance_campaign_endpoint(
        cls, client_id: str, client_access_token: str, profile_id: str, start_date: datetime.date, end_date: datetime.date, limit: int = 300
    ) -> "AttributionReportRequestBuilder":
        return (
            cls("attribution/report")
            .with_client_id(client_id)
            .with_client_access_token(client_access_token)
            .with_profile_id(profile_id)
            .with_report_type("PERFORMANCE")
            .with_metrics(METRICS_MAP["PERFORMANCE"] + [BRAND_REFERRAL_BONUS])
            .with_limit(limit)
            .with_start_date(start_date)
            .with_end_date(end_date)
            .with_grouping("CAMPAIGN")
        )

    @classmethod
    def performance_creative_endpoint(
        cls, client_id: str, client_access_token: str, profile_id: str, start_date: datetime.date, end_date: datetime.date, limit: int = 300
    ) -> "AttributionReportRequestBuilder":
        return (
            cls("attribution/report")
            .with_client_id(client_id)
            .with_client_access_token(client_access_token)
            .with_profile_id(profile_id)
            .with_report_type("PERFORMANCE")
            .with_metrics(METRICS_MAP["PERFORMANCE"])
            .with_limit(limit)
            .with_start_date(start_date)
            .with_end_date(end_date)
            .with_grouping("CREATIVE")
        )

    def __init__(self, resource: str) -> None:
        super().__init__(resource)
        self._cursor_field: Optional[int] = None
        self._end_date: Optional[str] = None
        self._grouping: Optional[str] = None
        self._limit: Optional[int] = None
        self._metrics: Optional[List[str]] = []
        self._report_type: Optional[str] = None
        self._start_date: Optional[str] = None

    @property
    def query_params(self) -> Dict[str, Any]:
        return None

    @property
    def request_body(self) -> Optional[str]:
        body: dict = OrderedDict()
        if self._report_type:
            body["reportType"] = self._report_type
        if self._grouping:
            body["groupBy"] = self._grouping
        if self._metrics:
            body["metrics"] = ",".join(self._metrics)
        if self._start_date:
            body["startDate"] = self._start_date
        if self._end_date:
            body["endDate"] = self._end_date

        if self._cursor_field:
            body["cursorId"] = self._cursor_field
        if self._limit:
            body["count"] = self._limit

        return json.dumps(body)

    def with_cursor_field(self, cursor_field: str) -> "AttributionReportRequestBuilder":
        self._cursor_field: int = cursor_field
        return self

    def with_end_date(self, end_date: datetime.date) -> "AttributionReportRequestBuilder":
        self._end_date: str = end_date.isoformat().replace("-", "")
        return self

    def with_grouping(self, grouping: str) -> "AttributionReportRequestBuilder":
        self._grouping: str = grouping
        return self

    def with_limit(self, limit: int) -> "AttributionReportRequestBuilder":
        self._limit: int = limit
        return self

    def with_metrics(self, metrics: List[str]) -> "AttributionReportRequestBuilder":
        self._metrics: str = metrics
        return self

    def with_report_type(self, report_type: str) -> "AttributionReportRequestBuilder":
        self._report_type: str = report_type
        return self

    def with_start_date(self, start_date: datetime.date) -> "AttributionReportRequestBuilder":
        self._start_date: str = start_date.isoformat().replace("-", "")
        return self
