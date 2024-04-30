# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json
from collections import OrderedDict
from typing import Any, Dict, List, Optional

import pendulum

from .base_request_builder import AmazonAdsBaseRequestBuilder


class SponsoredDisplayReportRequestBuilder(AmazonAdsBaseRequestBuilder):
    @classmethod
    def _init_report_endpoint(
        cls, client_id: str, client_access_token: str, profile_id: str, report_type: str, tactics: str, metrics: List[str], report_date: Optional[str] = None
    ) -> "SponsoredDisplayReportRequestBuilder":
        return cls(f"sd/{report_type}/report") \
            .with_client_id(client_id) \
            .with_client_access_token(client_access_token) \
            .with_profile_id(profile_id) \
            .with_tactics(tactics) \
            .with_metrics(metrics) \
            .with_report_date(report_date)

    @classmethod
    def init_campaigns_report_endpoint(
        cls, client_id: str, client_access_token: str, profile_id: str, tactics: str, metrics: List[str], report_date: Optional[str]
    ) -> "SponsoredDisplayReportRequestBuilder":
        return cls._init_report_endpoint(client_id, client_access_token, profile_id, "campaigns", report_date, tactics, metrics)

    @classmethod
    def init_ad_groups_report_endpoint(
        cls, client_id: str, client_access_token: str, profile_id: str, tactics: str, metrics: List[str], report_date: Optional[str]
    ) -> "SponsoredDisplayReportRequestBuilder":
        return cls._init_report_endpoint(client_id, client_access_token, profile_id, "adGroups", report_date, tactics, metrics)

    @classmethod
    def init_product_ads_report_endpoint(
        cls, client_id: str, client_access_token: str, profile_id: str, tactics: str, metrics: List[str], report_date: Optional[str]
    ) -> "SponsoredDisplayReportRequestBuilder":
        return cls._init_report_endpoint(client_id, client_access_token, profile_id, "productAds", report_date, tactics, metrics)

    @classmethod
    def init_targets_report_endpoint(
        cls, client_id: str, client_access_token: str, profile_id: str, tactics: str, metrics: List[str], report_date: Optional[str]
    ) -> "SponsoredDisplayReportRequestBuilder":
        return cls._init_report_endpoint(client_id, client_access_token, profile_id, "targets", report_date, tactics, metrics)

    @classmethod
    def init_asins_report_endpoint(
        cls, client_id: str, client_access_token: str, profile_id: str, tactics: str, metrics: List[str], report_date: Optional[str]
    ) -> "SponsoredDisplayReportRequestBuilder":
        return cls._init_report_endpoint(client_id, client_access_token, profile_id, "asins", report_date, tactics, metrics)

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
        if self._tactics:
            body["tactic"] = self._tactics
        if self._metrics:
            body["metrics"] = self._metrics
        return json.dumps(body)

    def with_report_date(self, report_date: pendulum.date) -> "SponsoredDisplayReportRequestBuilder":
        self._report_date = report_date.format("YYYYMMDD")
        return self

    def with_tactics(self, tactics: str) -> "SponsoredDisplayReportRequestBuilder":
        self._tactics = tactics
        return self

    def with_metrics(self, metrics: List[str]) -> "SponsoredDisplayReportRequestBuilder":
        self._metrics = ",".join(metrics)
        return self
