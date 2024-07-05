#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import re
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Set, Tuple, Union
from urllib.parse import urlparse

import _csv
import pendulum
from airbyte_cdk.sources.streams.core import package_name_from_class
from airbyte_cdk.sources.utils.schema_helpers import ResourceSchemaLoader
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from airbyte_protocol.models import SyncMode
from bingads import ServiceClient
from bingads.v13.internal.reporting.row_report import _RowReport
from bingads.v13.internal.reporting.row_report_iterator import _RowReportRecord
from bingads.v13.reporting import ReportingDownloadParameters
from cached_property import cached_property
from source_bing_ads.base_streams import Accounts, BingAdsStream
from source_bing_ads.utils import transform_date_format_to_rfc_3339, transform_report_hourly_datetime_format_to_rfc_3339
from suds import WebFault, sudsobject


class HourlyReportTransformerMixin:
    transformer: TypeTransformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization | TransformConfig.CustomSchemaNormalization)

    @staticmethod
    @transformer.registerCustomTransform
    def custom_transform_datetime_rfc3339(original_value, field_schema):
        if original_value and "format" in field_schema and field_schema["format"] == "date-time":
            transformed_value = transform_report_hourly_datetime_format_to_rfc_3339(original_value)
            return transformed_value
        return original_value


class BingAdsReportingServiceStream(BingAdsStream, ABC):
    # The directory where the file with report will be downloaded.
    file_directory: str = "/tmp"
    # timeout for reporting download operations in milliseconds
    timeout: int = 300000
    report_file_format: str = "Csv"

    transformer: TypeTransformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)
    primary_key: List[str] = ["TimePeriod", "Network", "DeviceType"]

    cursor_field = "TimePeriod"
    service_name: str = "ReportingService"
    operation_name: str = "download_report"

    def get_json_schema(self) -> Mapping[str, Any]:
        return ResourceSchemaLoader(package_name_from_class(self.__class__)).get_schema(self.report_schema_name)

    @property
    @abstractmethod
    def report_name(self) -> str:
        """
        Specifies bing ads report naming
        """

    @property
    @abstractmethod
    def report_aggregation(self) -> Optional[str]:
        """
        Specifies bing ads report aggregation type
        Supported types: Hourly, Daily, Weekly, Monthly
        """

    @property
    @abstractmethod
    def report_schema_name(self) -> str:
        """
        Specifies file name with schema
        """

    @property
    def default_time_periods(self):
        # used when reports start date is not provided
        return ["LastYear", "ThisYear"] if self.report_aggregation not in ("DayOfWeek", "HourOfDay") else ["ThisYear"]

    @property
    def report_columns(self) -> Iterable[str]:
        return list(self.get_json_schema().get("properties", {}).keys())

    def parse_response(self, response: sudsobject.Object, **kwargs: Mapping[str, Any]) -> Iterable[Mapping]:
        if response is not None:
            try:
                for row in response.report_records:
                    yield {column: self.get_column_value(row, column) for column in self.report_columns}
            except _csv.Error as e:
                self.logger.warning(f"CSV report file for stream `{self.name}` is broken or cannot be read correctly: {e}, skipping ...")

    def get_column_value(self, row: _RowReportRecord, column: str) -> Union[str, None, int, float]:
        """
        Reads field value from row and transforms:
        1. empty values to logical None
        2. Percent values to numeric string e.g. "12.25%" -> "12.25"
        """
        value = row.value(column)
        if not value or value == "--":
            return None
        if "%" in value:
            value = value.replace("%", "")
        if value and column in self._get_schema_numeric_properties:
            value = value.replace(",", "")
        return value

    @cached_property
    def _get_schema_numeric_properties(self) -> Set[str]:
        return set(k for k, v in self.get_json_schema()["properties"].items() if set(v.get("type")) & {"integer", "number"})

    def get_request_date(self, reporting_service: ServiceClient, date: datetime) -> sudsobject.Object:
        """
        Creates XML Date object based on datetime.
        https://docs.microsoft.com/en-us/advertising/reporting-service/date?view=bingads-13
        The [suds.client.Factory-class.html factory] namespace provides a factory that may be used
        to create instances of objects and types defined in the WSDL.
        """
        request_date = reporting_service.factory.create("Date")
        request_date.Day = date.day
        request_date.Month = date.month
        request_date.Year = date.year
        return request_date

    def request_params(
        self, stream_state: Mapping[str, Any] = None, account_id: str = None, **kwargs: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        stream_slice = kwargs["stream_slice"]
        start_date = self.get_start_date(stream_state, account_id)

        reporting_service = self.client.get_service("ReportingService")
        request_time_zone = reporting_service.factory.create("ReportTimeZone")

        report_time = reporting_service.factory.create("ReportTime")
        report_time.ReportTimeZone = request_time_zone.GreenwichMeanTimeDublinEdinburghLisbonLondon
        if start_date:
            report_time.CustomDateRangeStart = self.get_request_date(reporting_service, start_date)
            report_time.CustomDateRangeEnd = self.get_request_date(reporting_service, datetime.utcnow())
            report_time.PredefinedTime = None
        else:
            report_time.CustomDateRangeStart = None
            report_time.CustomDateRangeEnd = None
            report_time.PredefinedTime = stream_slice["time_period"]

        report_request = self.get_report_request(account_id, False, False, False, self.report_file_format, False, report_time)

        return {
            "report_request": report_request,
            "result_file_directory": self.file_directory,
            "result_file_name": self.report_name,
            "overwrite_result_file": True,
            "timeout_in_milliseconds": self.timeout,
        }

    def get_start_date(self, stream_state: Mapping[str, Any] = None, account_id: str = None):
        if stream_state and account_id:
            if stream_state.get(account_id, {}).get(self.cursor_field):
                return pendulum.parse(stream_state[account_id][self.cursor_field])

        return self.client.reports_start_date

    def get_updated_state(
        self,
        current_stream_state: MutableMapping[str, Any],
        latest_record: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        account_id = str(latest_record["AccountId"])
        current_stream_state[account_id] = current_stream_state.get(account_id, {})
        current_stream_state[account_id][self.cursor_field] = max(
            self.get_report_record_timestamp(latest_record[self.cursor_field]),
            current_stream_state.get(account_id, {}).get(self.cursor_field, ""),
        )
        return current_stream_state

    def send_request(self, params: Mapping[str, Any], customer_id: str, account_id: str) -> _RowReport:
        request_kwargs = {
            "service_name": None,
            "customer_id": customer_id,
            "account_id": account_id,
            "operation_name": self.operation_name,
            "is_report_service": True,
            "params": {"download_parameters": ReportingDownloadParameters(**params)},
        }
        return self.client.request(**request_kwargs)

    def get_report_request(
        self,
        account_id: str,
        exclude_column_headers: bool,
        exclude_report_footer: bool,
        exclude_report_header: bool,
        report_file_format: str,
        return_only_complete_data: bool,
        time: sudsobject.Object,
    ) -> sudsobject.Object:
        reporting_service = self.client.get_service(self.service_name)
        report_request = reporting_service.factory.create(f"{self.report_name}Request")
        if self.report_aggregation:
            report_request.Aggregation = self.report_aggregation

        report_request.ExcludeColumnHeaders = exclude_column_headers
        report_request.ExcludeReportFooter = exclude_report_footer
        report_request.ExcludeReportHeader = exclude_report_header
        report_request.Format = report_file_format
        report_request.FormatVersion = "2.0"
        report_request.ReturnOnlyCompleteData = return_only_complete_data
        report_request.Time = time
        report_request.ReportName = self.report_name
        # Defines the set of accounts and campaigns to include in the report.
        scope = reporting_service.factory.create("AccountThroughCampaignReportScope")
        scope.AccountIds = {"long": [account_id]}
        scope.Campaigns = None
        report_request.Scope = scope

        columns = reporting_service.factory.create(f"ArrayOf{self.report_name}Column")
        getattr(columns, f"{self.report_name}Column").append(self.report_columns)
        report_request.Columns = columns
        return report_request

    def get_report_record_timestamp(self, datestring: str) -> str:
        """
        Parse report date field based on aggregation type
        """
        return (
            self.transformer._custom_normalizer(datestring, self.get_json_schema()["properties"][self.cursor_field])
            if self.transformer._custom_normalizer
            else datestring
        )

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: Optional[List[str]] = None, stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        accounts = Accounts(self.client, self.config)
        for _slice in accounts.stream_slices():
            for account in accounts.read_records(SyncMode.full_refresh, _slice):
                if self.get_start_date(stream_state, account["Id"]):  # if start date is not provided default time periods will be used
                    yield {"account_id": account["Id"], "customer_id": account["ParentCustomerId"]}
                else:
                    for period in self.default_time_periods:
                        yield {"account_id": account["Id"], "customer_id": account["ParentCustomerId"], "time_period": period}


class BingAdsReportingServicePerformanceStream(BingAdsReportingServiceStream, ABC):
    def get_start_date(self, stream_state: Mapping[str, Any] = None, account_id: str = None):
        start_date = super().get_start_date(stream_state, account_id)

        if self.config.get("lookback_window") and start_date:
            # Datetime subtract won't work with days = 0
            # it'll output an AirbyteError
            return start_date.subtract(days=self.config["lookback_window"])
        else:
            return start_date


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


class CampaignPerformanceReport(BingAdsReportingServicePerformanceStream, ABC):
    report_name: str = "CampaignPerformanceReport"

    report_schema_name = "campaign_performance_report"
    primary_key = [
        "AccountId",
        "CampaignId",
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


class CampaignPerformanceReportHourly(HourlyReportTransformerMixin, CampaignPerformanceReport):
    report_aggregation = "Hourly"

    report_schema_name = "campaign_performance_report_hourly"


class CampaignPerformanceReportDaily(CampaignPerformanceReport):
    report_aggregation = "Daily"


class CampaignPerformanceReportWeekly(CampaignPerformanceReport):
    report_aggregation = "Weekly"


class CampaignPerformanceReportMonthly(CampaignPerformanceReport):
    report_aggregation = "Monthly"


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


class AdPerformanceReport(BingAdsReportingServicePerformanceStream, ABC):
    report_name: str = "AdPerformanceReport"

    report_schema_name = "ad_performance_report"
    primary_key = [
        "AccountId",
        "CampaignId",
        "AdGroupId",
        "AdId",
        "TimePeriod",
        "CurrencyCode",
        "AdDistribution",
        "DeviceType",
        "Language",
        "Network",
        "DeviceOS",
        "TopVsOther",
        "BidMatchType",
        "DeliveredMatchType",
    ]


class AdPerformanceReportHourly(HourlyReportTransformerMixin, AdPerformanceReport):
    report_aggregation = "Hourly"
    report_schema_name = "ad_performance_report_hourly"


class AdPerformanceReportDaily(AdPerformanceReport):
    report_aggregation = "Daily"


class AdPerformanceReportWeekly(AdPerformanceReport):
    report_aggregation = "Weekly"


class AdPerformanceReportMonthly(AdPerformanceReport):
    report_aggregation = "Monthly"


class AdGroupPerformanceReport(BingAdsReportingServicePerformanceStream, ABC):
    report_name: str = "AdGroupPerformanceReport"
    report_schema_name = "ad_group_performance_report"

    primary_key = [
        "AccountId",
        "CampaignId",
        "AdGroupId",
        "TimePeriod",
        "CurrencyCode",
        "AdDistribution",
        "DeviceType",
        "Network",
        "DeliveredMatchType",
        "DeviceOS",
        "TopVsOther",
        "BidMatchType",
        "Language",
    ]


class AdGroupPerformanceReportHourly(HourlyReportTransformerMixin, AdGroupPerformanceReport):
    report_aggregation = "Hourly"
    report_schema_name = "ad_group_performance_report_hourly"


class AdGroupPerformanceReportDaily(AdGroupPerformanceReport):
    report_aggregation = "Daily"


class AdGroupPerformanceReportWeekly(AdGroupPerformanceReport):
    report_aggregation = "Weekly"


class AdGroupPerformanceReportMonthly(AdGroupPerformanceReport):
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


class KeywordPerformanceReport(BingAdsReportingServicePerformanceStream, ABC):
    report_name: str = "KeywordPerformanceReport"
    report_schema_name = "keyword_performance_report"
    primary_key = [
        "AccountId",
        "CampaignId",
        "AdGroupId",
        "KeywordId",
        "AdId",
        "TimePeriod",
        "CurrencyCode",
        "DeliveredMatchType",
        "AdDistribution",
        "DeviceType",
        "Language",
        "Network",
        "DeviceOS",
        "TopVsOther",
        "BidMatchType",
    ]


class KeywordPerformanceReportHourly(HourlyReportTransformerMixin, KeywordPerformanceReport):
    report_aggregation = "Hourly"
    report_schema_name = "keyword_performance_report_hourly"


class KeywordPerformanceReportDaily(KeywordPerformanceReport):
    report_aggregation = "Daily"
    report_schema_name = "keyword_performance_report_daily"


class KeywordPerformanceReportWeekly(KeywordPerformanceReport):
    report_aggregation = "Weekly"


class KeywordPerformanceReportMonthly(KeywordPerformanceReport):
    report_aggregation = "Monthly"


class GeographicPerformanceReport(BingAdsReportingServicePerformanceStream, ABC):
    report_name: str = "GeographicPerformanceReport"
    report_schema_name = "geographic_performance_report"

    # Need to override the primary key here because the one inherited from the PerformanceReportsMixin
    # is incorrect for the geographic performance reports
    primary_key = None


class GeographicPerformanceReportHourly(HourlyReportTransformerMixin, GeographicPerformanceReport):
    report_aggregation = "Hourly"
    report_schema_name = "geographic_performance_report_hourly"


class GeographicPerformanceReportDaily(GeographicPerformanceReport):
    report_aggregation = "Daily"


class GeographicPerformanceReportWeekly(GeographicPerformanceReport):
    report_aggregation = "Weekly"


class GeographicPerformanceReportMonthly(GeographicPerformanceReport):
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


class AgeGenderAudienceReport(BingAdsReportingServicePerformanceStream, ABC):
    report_name: str = "AgeGenderAudienceReport"

    report_schema_name = "age_gender_audience_report"
    primary_key = ["AgeGroup", "Gender", "TimePeriod", "AccountId", "CampaignId", "Language", "AdDistribution"]


class AgeGenderAudienceReportHourly(HourlyReportTransformerMixin, AgeGenderAudienceReport):
    report_aggregation = "Hourly"
    report_schema_name = "age_gender_audience_report_hourly"


class AgeGenderAudienceReportDaily(AgeGenderAudienceReport):
    report_aggregation = "Daily"


class AgeGenderAudienceReportWeekly(AgeGenderAudienceReport):
    report_aggregation = "Weekly"


class AgeGenderAudienceReportMonthly(AgeGenderAudienceReport):
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
