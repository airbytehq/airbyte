# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Any, Dict, Optional

from .base_request_builder import AmazonAdsBaseRequestBuilder


class ReportCheckStatusRequestBuilder(AmazonAdsBaseRequestBuilder):
    @classmethod
    def check_v2_report_status_endpoint(
        cls, client_id: str, client_access_token: str, profile_id: str, report_id: str
    ) -> "ReportCheckStatusRequestBuilder":
        return (
            cls(f"v2/reports/{report_id}")
            .with_client_id(client_id)
            .with_client_access_token(client_access_token)
            .with_profile_id(profile_id)
        )

    @classmethod
    def check_v3_report_status_endpoint(
        cls, client_id: str, client_access_token: str, profile_id: str, report_id: str
    ) -> "ReportCheckStatusRequestBuilder":
        return (
            cls(f"reporting/reports/{report_id}")
            .with_client_id(client_id)
            .with_client_access_token(client_access_token)
            .with_profile_id(profile_id)
        )

    @classmethod
    def check_sponsored_display_report_status_endpoint(
        cls, client_id: str, client_access_token: str, profile_id: str, report_id: str
    ) -> "ReportCheckStatusRequestBuilder":
        return cls.check_v3_report_status_endpoint(client_id, client_access_token, profile_id, report_id)

    @classmethod
    def check_sponsored_products_report_status_endpoint(
        cls, client_id: str, client_access_token: str, profile_id: str, report_id: str
    ) -> "ReportCheckStatusRequestBuilder":
        return cls.check_v3_report_status_endpoint(client_id, client_access_token, profile_id, report_id)

    @classmethod
    def check_sponsored_brands_v3_report_status_endpoint(
        cls, client_id: str, client_access_token: str, profile_id: str, report_id: str
    ) -> "ReportCheckStatusRequestBuilder":
        return cls.check_v3_report_status_endpoint(client_id, client_access_token, profile_id, report_id)

    def __init__(self, resource: str) -> None:
        super().__init__(resource)

    @property
    def query_params(self) -> Dict[str, Any]:
        return None

    @property
    def request_body(self) -> Optional[str]:
        return None
