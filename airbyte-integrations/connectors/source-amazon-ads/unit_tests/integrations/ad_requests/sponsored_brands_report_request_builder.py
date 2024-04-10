# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json
from collections import OrderedDict
from typing import Any, Dict, List, Optional

import pendulum

from .base_request_builder import AmazonAdsBaseRequestBuilder


class SponsoredBrandsReportRequestBuilder(AmazonAdsBaseRequestBuilder):
    @classmethod
    def _init_report_endpoint(
        cls, client_id: str, client_access_token: str, profile_id: str, report_type: str, metrics: List[str], report_date: Optional[str] = None
    ) -> "SponsoredBrandsReportRequestBuilder":
        return cls(f"v2/hsa/{report_type}/report") \
            .with_client_id(client_id) \
            .with_client_access_token(client_access_token) \
            .with_profile_id(profile_id) \
            .with_metrics(metrics) \
            .with_report_date(report_date)

    @classmethod
    def init_campaigns_report_endpoint(
        cls, client_id: str, client_access_token: str, profile_id: str, metrics: List[str], report_date: Optional[str]
    ) -> "SponsoredBrandsReportRequestBuilder":
        return cls._init_report_endpoint(client_id, client_access_token, profile_id, "campaigns", report_date, metrics)

    @classmethod
    def init_ad_groups_report_endpoint(
        cls, client_id: str, client_access_token: str, profile_id: str, metrics: List[str], report_date: Optional[str]
    ) -> "SponsoredBrandsReportRequestBuilder":
        return cls._init_report_endpoint(client_id, client_access_token, profile_id, "adGroups", report_date, metrics)

    @classmethod
    def init_keywords_report_endpoint(
        cls, client_id: str, client_access_token: str, profile_id: str, metrics: List[str], report_date: Optional[str]
    ) -> "SponsoredBrandsReportRequestBuilder":
        return cls._init_report_endpoint(client_id, client_access_token, profile_id, "keywords", report_date, metrics)

    def __init__(self, resource: str) -> None:
        super().__init__(resource)
        self._metrics: List[str] = None
        self._report_date: str = None

    @property
    def query_params(self) -> Dict[str, Any]:
        return None

    @property
    def request_body(self) ->Optional[str]:
        body: dict = OrderedDict()
        if self._report_date:
            body["reportDate"] = self._report_date
        if self._metrics:
            body["metrics"] = self._metrics
        return json.dumps(body)

    def with_report_date(self, report_date: pendulum.date) -> "SponsoredBrandsReportRequestBuilder":
        self._report_date = report_date.format("YYYYMMDD")
        return self

    def with_metrics(self, metrics: List[str]) -> "SponsoredBrandsReportRequestBuilder":
        self._metrics = ",".join(metrics)
        return self
