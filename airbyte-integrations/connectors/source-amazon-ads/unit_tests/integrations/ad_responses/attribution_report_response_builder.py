# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Optional

from airbyte_cdk.test.mock_http.response_builder import FieldPath, HttpResponseBuilder, PaginationStrategy, find_template


class AttributionReportResponseBuilder(HttpResponseBuilder):
    @classmethod
    def products_response(cls, pagination_strategy: Optional[PaginationStrategy] = None) -> "AttributionReportResponseBuilder":
        return cls(find_template("attribution_report_products", __file__), FieldPath("reports"), pagination_strategy)

    @classmethod
    def performance_adgroup_response(cls, pagination_strategy: Optional[PaginationStrategy] = None) -> "AttributionReportResponseBuilder":
        return cls(find_template("attribution_report_performance_adgroup", __file__), FieldPath("reports"), pagination_strategy)

    @classmethod
    def performance_campaign_response(cls, pagination_strategy: Optional[PaginationStrategy] = None) -> "AttributionReportResponseBuilder":
        return cls(find_template("attribution_report_performance_campaign", __file__), FieldPath("reports"), pagination_strategy)

    @classmethod
    def performance_creative_response(cls, pagination_strategy: Optional[PaginationStrategy] = None) -> "AttributionReportResponseBuilder":
        return cls(find_template("attribution_report_performance_creative", __file__), FieldPath("reports"), pagination_strategy)
