#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import re
import xml.etree.ElementTree as ET
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Tuple, Union
from urllib.parse import urlparse

from bingads.v13.internal.reporting.row_report import _RowReport
from suds import WebFault

from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from source_bing_ads.reports import BingAdsReportingServicePerformanceStream, BingAdsReportingServiceStream, HourlyReportTransformerMixin
from source_bing_ads.utils import transform_date_format_to_rfc_3339, transform_report_hourly_datetime_format_to_rfc_3339


class BudgetSummaryReport(BingAdsReportingServiceStream):
    report_name: str = "BudgetSummaryReport"
    report_aggregation = None
    cursor_field = "Date"
    report_schema_name = "budget_summary_report"
    primary_key = "Date"

    transformer: TypeTransformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization | TransformConfig.CustomSchemaNormalization)

    @staticmethod
    @transformer.registerCustomTransform
    def custom_transform_date_rfc3339(original_value, field_schema):
        if original_value and "format" in field_schema and field_schema["format"] == "date":
            transformed_value = transform_date_format_to_rfc_3339(original_value)
            return transformed_value
        return original_value


class CampaignImpressionPerformanceReport(BingAdsReportingServicePerformanceStream, ABC):
    """
    https://learn.microsoft.com/en-us/advertising/reporting-service/adgroupperformancereportrequest?view=bingads-13
    Primary key cannot be set: due to included `Impression Share Performance Statistics` some fields should be removed,
    see https://learn.microsoft.com/en-us/advertising/guides/reports?view=bingads-13#columnrestrictions for more info.
    """

    report_name: str = "CampaignPerformanceReport"

    report_schema_name = "campaign_impression_performance_report"

    primary_key = None


class CampaignImpressionPerformanceReportHourly(HourlyReportTransformerMixin, CampaignImpressionPerformanceReport):
    report_aggregation = "Hourly"

    report_schema_name = "campaign_impression_performance_report_hourly"


class CampaignImpressionPerformanceReportDaily(CampaignImpressionPerformanceReport):
    report_aggregation = "Daily"


class CampaignImpressionPerformanceReportWeekly(CampaignImpressionPerformanceReport):
    report_aggregation = "Weekly"


class CampaignImpressionPerformanceReportMonthly(CampaignImpressionPerformanceReport):
    report_aggregation = "Monthly"


class AdGroupImpressionPerformanceReport(BingAdsReportingServicePerformanceStream, ABC):
    """
    https://learn.microsoft.com/en-us/advertising/reporting-service/adgroupperformancereportrequest?view=bingads-13
    Primary key cannot be set: due to included `Impression Share Performance Statistics` some fields should be removed,
    see https://learn.microsoft.com/en-us/advertising/guides/reports?view=bingads-13#columnrestrictions for more info.
    """

    report_name: str = "AdGroupPerformanceReport"
    report_schema_name = "ad_group_impression_performance_report"


class AdGroupImpressionPerformanceReportHourly(HourlyReportTransformerMixin, AdGroupImpressionPerformanceReport):
    report_aggregation = "Hourly"
    report_schema_name = "ad_group_impression_performance_report_hourly"


class AdGroupImpressionPerformanceReportDaily(AdGroupImpressionPerformanceReport):
    report_aggregation = "Daily"


class AdGroupImpressionPerformanceReportWeekly(AdGroupImpressionPerformanceReport):
    report_aggregation = "Weekly"


class AdGroupImpressionPerformanceReportMonthly(AdGroupImpressionPerformanceReport):
    report_aggregation = "Monthly"


class AccountPerformanceReport(BingAdsReportingServicePerformanceStream, ABC):
    report_name: str = "AccountPerformanceReport"
    report_schema_name = "account_performance_report"
    primary_key = [
        "AccountId",
        "TimePeriod",
        "CurrencyCode",
        "AdDistribution",
        "DeviceType",
        "Network",
        "DeliveredMatchType",
        "DeviceOS",
        "TopVsOther",
        "BidMatchType",
    ]


class AccountPerformanceReportHourly(HourlyReportTransformerMixin, AccountPerformanceReport):
    report_aggregation = "Hourly"
    report_schema_name = "account_performance_report_hourly"


class AccountPerformanceReportDaily(AccountPerformanceReport):
    report_aggregation = "Daily"


class AccountPerformanceReportWeekly(AccountPerformanceReport):
    report_aggregation = "Weekly"


class AccountPerformanceReportMonthly(AccountPerformanceReport):
    report_aggregation = "Monthly"


class AccountImpressionPerformanceReport(BingAdsReportingServicePerformanceStream, ABC):
    """
    Report source: https://docs.microsoft.com/en-us/advertising/reporting-service/accountperformancereportrequest?view=bingads-13
    Primary key cannot be set: due to included `Impression Share Performance Statistics` some fields should be removed,
    see https://learn.microsoft.com/en-us/advertising/guides/reports?view=bingads-13#columnrestrictions for more info.
    """

    report_name: str = "AccountPerformanceReport"
    report_schema_name = "account_impression_performance_report"
    primary_key = None


class AccountImpressionPerformanceReportHourly(HourlyReportTransformerMixin, AccountImpressionPerformanceReport):
    report_aggregation = "Hourly"
    report_schema_name = "account_impression_performance_report_hourly"


class AccountImpressionPerformanceReportDaily(AccountImpressionPerformanceReport):
    report_aggregation = "Daily"


class AccountImpressionPerformanceReportWeekly(AccountImpressionPerformanceReport):
    report_aggregation = "Weekly"


class AccountImpressionPerformanceReportMonthly(AccountImpressionPerformanceReport):
    report_aggregation = "Monthly"


class SearchQueryPerformanceReport(BingAdsReportingServicePerformanceStream, ABC):
    report_name: str = "SearchQueryPerformanceReport"
    report_schema_name = "search_query_performance_report"

    primary_key = [
        "SearchQuery",
        "Keyword",
        "TimePeriod",
        "AccountId",
        "CampaignId",
        "Language",
        "DeliveredMatchType",
        "DeviceType",
        "DeviceOS",
        "TopVsOther",
    ]


class SearchQueryPerformanceReportHourly(HourlyReportTransformerMixin, SearchQueryPerformanceReport):
    report_aggregation = "Hourly"
    report_schema_name = "search_query_performance_report_hourly"


class SearchQueryPerformanceReportDaily(SearchQueryPerformanceReport):
    report_aggregation = "Daily"


class SearchQueryPerformanceReportWeekly(SearchQueryPerformanceReport):
    report_aggregation = "Weekly"


class SearchQueryPerformanceReportMonthly(SearchQueryPerformanceReport):
    report_aggregation = "Monthly"


class UserLocationPerformanceReport(BingAdsReportingServicePerformanceStream, ABC):
    report_name: str = "UserLocationPerformanceReport"
    report_schema_name = "user_location_performance_report"
    primary_key = [
        "AccountId",
        "AdGroupId",
        "CampaignId",
        "DeliveredMatchType",
        "DeviceOS",
        "DeviceType",
        "Language",
        "LocationId",
        "QueryIntentLocationId",
        "TimePeriod",
        "TopVsOther",
    ]


class UserLocationPerformanceReportHourly(HourlyReportTransformerMixin, UserLocationPerformanceReport):
    report_aggregation = "Hourly"
    report_schema_name = "user_location_performance_report_hourly"


class UserLocationPerformanceReportDaily(UserLocationPerformanceReport):
    report_aggregation = "Daily"


class UserLocationPerformanceReportWeekly(UserLocationPerformanceReport):
    report_aggregation = "Weekly"


class UserLocationPerformanceReportMonthly(UserLocationPerformanceReport):
    report_aggregation = "Monthly"


class ProductDimensionPerformanceReport(BingAdsReportingServicePerformanceStream, ABC):
    """
    https://learn.microsoft.com/en-us/advertising/reporting-service/productdimensionperformancereportrequest?view=bingads-13
    """

    report_name: str = "ProductDimensionPerformanceReport"
    report_schema_name = "product_dimension_performance_report"
    primary_key = None

    @property
    def report_columns(self) -> Iterable[str]:
        """AccountId is not in reporting columns for this report"""
        properties = list(self.get_json_schema().get("properties", {}).keys())
        properties.remove("AccountId")
        return properties

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        record = super().transform(record, stream_slice)
        record["AccountId"] = stream_slice["account_id"]
        return record


class ProductDimensionPerformanceReportHourly(HourlyReportTransformerMixin, ProductDimensionPerformanceReport):
    report_aggregation = "Hourly"
    report_schema_name = "product_dimension_performance_report_hourly"


class ProductDimensionPerformanceReportDaily(ProductDimensionPerformanceReport):
    report_aggregation = "Daily"


class ProductDimensionPerformanceReportWeekly(ProductDimensionPerformanceReport):
    report_aggregation = "Weekly"


class ProductDimensionPerformanceReportMonthly(ProductDimensionPerformanceReport):
    report_aggregation = "Monthly"


class ProductSearchQueryPerformanceReport(BingAdsReportingServicePerformanceStream, ABC):
    """
    https://learn.microsoft.com/en-us/advertising/reporting-service/productsearchqueryperformancereportrequest?view=bingads-13
    """

    report_name: str = "ProductSearchQueryPerformanceReport"
    report_schema_name = "product_search_query_performance_report"
    primary_key = [
        "AccountId",
        "TimePeriod",
        "CampaignId",
        "AdId",
        "AdGroupId",
        "SearchQuery",
        "DeviceType",
        "DeviceOS",
        "Language",
        "Network",
    ]


class ProductSearchQueryPerformanceReportHourly(HourlyReportTransformerMixin, ProductSearchQueryPerformanceReport):
    report_aggregation = "Hourly"
    report_schema_name = "product_search_query_performance_report_hourly"


class ProductSearchQueryPerformanceReportDaily(ProductSearchQueryPerformanceReport):
    report_aggregation = "Daily"


class ProductSearchQueryPerformanceReportWeekly(ProductSearchQueryPerformanceReport):
    report_aggregation = "Weekly"


class ProductSearchQueryPerformanceReportMonthly(ProductSearchQueryPerformanceReport):
    report_aggregation = "Monthly"


class GoalsAndFunnelsReport(BingAdsReportingServicePerformanceStream, ABC):
    """
    https://learn.microsoft.com/en-us/advertising/reporting-service/goalsandfunnelsreportrequest?view=bingads-13
    """

    report_name: str = "GoalsAndFunnelsReport"
    report_schema_name = "goals_and_funnels_report"
    primary_key = [
        "GoalId",
        "TimePeriod",
        "AccountId",
        "CampaignId",
        "DeviceType",
        "DeviceOS",
        "AdGroupId",
    ]


class GoalsAndFunnelsReportHourly(HourlyReportTransformerMixin, GoalsAndFunnelsReport):
    report_aggregation = "Hourly"
    report_schema_name = "goals_and_funnels_report_hourly"


class GoalsAndFunnelsReportDaily(GoalsAndFunnelsReport):
    report_aggregation = "Daily"


class GoalsAndFunnelsReportWeekly(GoalsAndFunnelsReport):
    report_aggregation = "Weekly"


class GoalsAndFunnelsReportMonthly(GoalsAndFunnelsReport):
    report_aggregation = "Monthly"


class AudiencePerformanceReport(BingAdsReportingServicePerformanceStream, ABC):
    """
    https://learn.microsoft.com/en-us/advertising/reporting-service/audienceperformancereportrequest?view=bingads-13
    """

    report_name: str = "AudiencePerformanceReport"
    report_schema_name = "audience_performance_report"
    primary_key = [
        "AudienceId",
        "TimePeriod",
        "AccountId",
        "CampaignId",
        "AdGroupId",
    ]


class AudiencePerformanceReportHourly(HourlyReportTransformerMixin, AudiencePerformanceReport):
    report_aggregation = "Hourly"
    report_schema_name = "audience_performance_report_hourly"


class AudiencePerformanceReportDaily(AudiencePerformanceReport):
    report_aggregation = "Daily"


class AudiencePerformanceReportWeekly(AudiencePerformanceReport):
    report_aggregation = "Weekly"


class AudiencePerformanceReportMonthly(AudiencePerformanceReport):
    report_aggregation = "Monthly"


class CustomReport(BingAdsReportingServicePerformanceStream, ABC):
    transformer: TypeTransformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)
    custom_report_columns = []
    report_schema_name = None
    primary_key = None

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        # Summary aggregation doesn't include TimePeriod field
        if self.report_aggregation not in ("Summary", "DayOfWeek", "HourOfDay"):
            return "TimePeriod"

    @property
    def report_columns(self):
        # adding common and default columns
        if "AccountId" not in self.custom_report_columns:
            self.custom_report_columns.append("AccountId")
        if self.cursor_field and self.cursor_field not in self.custom_report_columns:
            self.custom_report_columns.append(self.cursor_field)
        return list(frozenset(self.custom_report_columns))

    def get_json_schema(self) -> Mapping[str, Any]:
        columns_schema = {col: {"type": ["null", "string"]} for col in self.report_columns}
        schema: Mapping[str, Any] = {
            "$schema": "https://json-schema.org/draft-07/schema#",
            "type": ["null", "object"],
            "additionalProperties": True,
            "properties": columns_schema,
        }
        return schema

    def validate_report_configuration(self) -> Tuple[bool, str]:
        # gets /bingads/v13/proxies/production/reporting_service.xml
        reporting_service_file = self.client.get_service(self.service_name)._get_service_info_dict(self.client.api_version)[
            ("reporting", self.client.environment)
        ]
        tree = ET.parse(urlparse(reporting_service_file).path)
        request_object = tree.find(f".//{{*}}complexType[@name='{self.report_name}Request']")

        report_object_columns = self._get_object_columns(request_object, tree)
        is_custom_cols_in_report_object_cols = all(x in report_object_columns for x in self.custom_report_columns)

        if not is_custom_cols_in_report_object_cols:
            return False, (
                f"Reporting Columns are invalid. Columns that you provided don't belong to Reporting Data Object Columns:"
                f" {self.custom_report_columns}. Please ensure it is correct in Bing Ads Docs."
            )

        return True, ""

    def _clear_namespace(self, type: str) -> str:
        return re.sub(r"^[a-z]+:", "", type)

    def _get_object_columns(self, request_el: ET.Element, tree: ET.ElementTree) -> List[str]:
        column_el = request_el.find(".//{*}element[@name='Columns']")
        array_of_columns_name = self._clear_namespace(column_el.get("type"))

        array_of_columns_elements = tree.find(f".//{{*}}complexType[@name='{array_of_columns_name}']")
        inner_array_of_columns_elements = array_of_columns_elements.find(".//{*}element")
        column_el_name = self._clear_namespace(inner_array_of_columns_elements.get("type"))

        column_el = tree.find(f".//{{*}}simpleType[@name='{column_el_name}']")
        column_enum_items = column_el.findall(".//{*}enumeration")
        column_enum_items_values = [el.get("value") for el in column_enum_items]
        return column_enum_items_values

    def get_report_record_timestamp(self, datestring: str) -> str:
        """
        Parse report date field based on aggregation type
        """
        if not self.report_aggregation or self.report_aggregation == "Summary":
            datestring = transform_date_format_to_rfc_3339(datestring)
        elif self.report_aggregation == "Hourly":
            datestring = transform_report_hourly_datetime_format_to_rfc_3339(datestring)
        return datestring

    def send_request(self, params: Mapping[str, Any], customer_id: str, account_id: str) -> _RowReport:
        try:
            return super().send_request(params, customer_id, account_id)
        except WebFault as e:
            self.logger.error(
                f"Could not sync custom report {self.name}: Please validate your column and aggregation configuration. "
                f"Error form server: [{e.fault.faultstring}]"
            )
