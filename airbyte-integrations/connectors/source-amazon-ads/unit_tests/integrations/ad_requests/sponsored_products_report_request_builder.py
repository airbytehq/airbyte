# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json
from collections import OrderedDict
from typing import Any, Dict, List, Optional

import pendulum

from .base_request_builder import AmazonAdsBaseRequestBuilder


class SponsoredProductsReportRequestBuilder(AmazonAdsBaseRequestBuilder):
    @classmethod
    def _init_report_endpoint(
        cls, client_id: str, client_access_token: str, profile_id: str, report_type: str, metrics: List[str], report_date: Optional[str] = None
    ) -> "SponsoredProductsReportRequestBuilder":
        return cls(f"reporting/reports") \
            .with_client_id(client_id) \
            .with_client_access_token(client_access_token) \
            .with_profile_id(profile_id) \
            .with_metrics(metrics) \
            .with_report_date(report_date) \
            .with_report_type(report_type)

    @classmethod
    def init_campaigns_report_endpoint(
        cls, client_id: str, client_access_token: str, profile_id: str, metrics: List[str], report_date: Optional[str]
    ) -> "SponsoredProductsReportRequestBuilder":
        return cls._init_report_endpoint(client_id, client_access_token, profile_id, "campaigns", report_date, metrics)

    @classmethod
    def init_ad_groups_report_endpoint(
        cls, client_id: str, client_access_token: str, profile_id: str, metrics: List[str], report_date: Optional[str]
    ) -> "SponsoredProductsReportRequestBuilder":
        return cls._init_report_endpoint(client_id, client_access_token, profile_id, "adGroups", report_date, metrics)

    @classmethod
    def init_keywords_report_endpoint(
        cls, client_id: str, client_access_token: str, profile_id: str, metrics: List[str], report_date: Optional[str]
    ) -> "SponsoredProductsReportRequestBuilder":
        return cls._init_report_endpoint(client_id, client_access_token, profile_id, "keywords", report_date, metrics)

    @classmethod
    def init_targets_report_endpoint(
        cls, client_id: str, client_access_token: str, profile_id: str, metrics: List[str], report_date: Optional[str]
    ) -> "SponsoredProductsReportRequestBuilder":
        return cls._init_report_endpoint(client_id, client_access_token, profile_id, "targets", report_date, metrics)

    @classmethod
    def init_product_ads_report_endpoint(
        cls, client_id: str, client_access_token: str, profile_id: str, metrics: List[str], report_date: Optional[str]
    ) -> "SponsoredProductsReportRequestBuilder":
        return cls._init_report_endpoint(client_id, client_access_token, profile_id, "productAds", report_date, metrics)

    @classmethod
    def init_asins_keywords_report_endpoint(
        cls, client_id: str, client_access_token: str, profile_id: str, metrics: List[str], report_date: Optional[str]
    ) -> "SponsoredProductsReportRequestBuilder":
        return cls._init_report_endpoint(client_id, client_access_token, profile_id, "asins_keywords", report_date, metrics)

    @classmethod
    def init_asins_targets_report_endpoint(
        cls, client_id: str, client_access_token: str, profile_id: str, metrics: List[str], report_date: Optional[str]
    ) -> "SponsoredProductsReportRequestBuilder":
        return cls._init_report_endpoint(client_id, client_access_token, profile_id, "asins_targets", report_date, metrics)

    def __init__(self, resource: str) -> None:
        super().__init__(resource)
        self._metrics: List[str] = None
        self._report_date: str = None
        self._report_type: str = None

    @property
    def _report_config_group_by(self) -> List[str]:
        return {
            "campaigns": ["campaign"],
            "adGroups": ["campaign", "adGroup"],
            "keywords": ["targeting"],
            "targets": ["targeting"],
            "productAds": ["advertiser"],
            "asins_keywords": ["asin"],
            "asins_targets": ["asin"],
        }[self._report_type]

    @property
    def _report_config_report_type_id(self) -> str:
        return {
            "campaigns": "spCampaigns",
            "adGroups": "spCampaigns",
            "keywords": "spTargeting",
            "targets": "spTargeting",
            "productAds": "spAdvertisedProduct",
            "asins_keywords": "spPurchasedProduct",
            "asins_targets": "spPurchasedProduct",
        }[self._report_type]

    @property
    def _report_config_filters(self) -> List[str]:
        return {
            "campaigns": [],
            "adGroups": [],
            "keywords": [{"field": "keywordType", "values": ["BROAD", "PHRASE", "EXACT"]}],
            "targets": [{"field": "keywordType", "values": ["TARGETING_EXPRESSION", "TARGETING_EXPRESSION_PREDEFINED"]}],
            "productAds": [],
            "asins_keywords": [],
            "asins_targets": [],
        }[self._report_type]

    @property
    def query_params(self) -> Dict[str, Any]:
        return None

    @property
    def request_body(self) ->Optional[str]:
        body: dict = OrderedDict()
        if self._report_type and self._report_date:
            body["name"] = f"{self._report_type} report {self._report_date}"

        if self._report_date:
            body["startDate"] = self._report_date
            body["endDate"] = self._report_date

        if self._report_type:
            body["configuration"] = {
                "adProduct": "SPONSORED_PRODUCTS",
                "groupBy": self._report_config_group_by
            }

        if self._metrics:
            body["configuration"]["columns"] = self._metrics

        if self._report_type:
            body["configuration"]["reportTypeId"] = self._report_config_report_type_id
            body["configuration"]["filters"] = self._report_config_filters

        body["configuration"]["timeUnit"] = "SUMMARY"
        body["configuration"]["format"] = "GZIP_JSON"

        return json.dumps(body)

    def with_report_date(self, report_date: pendulum.date) -> "SponsoredProductsReportRequestBuilder":
        self._report_date = report_date.format("YYYY-MM-DD")
        return self

    def with_report_type(self, report_type: str) -> "SponsoredProductsReportRequestBuilder":
        self._report_type = report_type
        return self

    def with_tactics(self, tactics: str) -> "SponsoredProductsReportRequestBuilder":
        self._tactics = tactics
        return self

    def with_metrics(self, metrics: List[str]) -> "SponsoredProductsReportRequestBuilder":
        self._metrics = metrics
        return self
