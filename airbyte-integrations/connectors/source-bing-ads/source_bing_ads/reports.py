#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union

import pendulum
import source_bing_ads.source
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.core import package_name_from_class
from airbyte_cdk.sources.utils.schema_helpers import ResourceSchemaLoader
from bingads.service_client import ServiceClient
from bingads.v13.internal.reporting.row_report import _RowReport
from bingads.v13.internal.reporting.row_report_iterator import _RowReportRecord
from bingads.v13.reporting import ReportingDownloadParameters
from suds import sudsobject

AVERAGE_FIELD_TYPES = {
    "AverageCpc": "number",
    "AveragePosition": "number",
    "AverageCpm": "number",
}
AVERAGE_FIELDS = list(AVERAGE_FIELD_TYPES.keys())

CONVERSION_FIELD_TYPES = {
    "Conversions": "number",
    "ConversionRate": "number",
    "ConversionsQualified": "number",
}
CONVERSION_FIELDS = list(CONVERSION_FIELD_TYPES.keys())

ALL_CONVERSION_FIELD_TYPES = {
    "AllConversions": "integer",
    "AllConversionRate": "number",
}
ALL_CONVERSION_FIELDS = list(ALL_CONVERSION_FIELD_TYPES.keys())

LOW_QUALITY_FIELD_TYPES = {
    "LowQualityClicks": "integer",
    "LowQualityClicksPercent": "number",
    "LowQualityImpressions": "integer",
    "LowQualitySophisticatedClicks": "integer",
    "LowQualityConversions": "integer",
    "LowQualityConversionRate": "number",
}
LOW_QUALITY_FIELDS = list(LOW_QUALITY_FIELD_TYPES.keys())

REVENUE_FIELD_TYPES = {
    "Revenue": "number",
    "RevenuePerConversion": "number",
    "RevenuePerAssist": "number",
}
REVENUE_FIELDS = list(REVENUE_FIELD_TYPES.keys())

ALL_REVENUE_FIELD_TYPES = {
    "AllRevenue": "number",
    "AllRevenuePerConversion": "number",
}
ALL_REVENUE_FIELDS = list(ALL_REVENUE_FIELD_TYPES.keys())

IMPRESSION_FIELD_TYPES = {
    "ImpressionSharePercent": "number",
    "ImpressionLostToBudgetPercent": "number",
    "ImpressionLostToRankAggPercent": "number",
}
IMPRESSION_FIELDS = list(IMPRESSION_FIELD_TYPES.keys())


HISTORICAL_FIELD_TYPES = {
    "HistoricalQualityScore": "number",
    "HistoricalExpectedCtr": "number",
    "HistoricalAdRelevance": "number",
    "HistoricalLandingPageExperience": "number",
}
HISTORICAL_FIELDS = list(HISTORICAL_FIELD_TYPES.keys())

BUDGET_FIELD_TYPES = {
    "BudgetName": "string",
    "BudgetStatus": "string",
    "BudgetAssociationStatus": "string",
}
BUDGET_FIELDS = list(BUDGET_FIELD_TYPES.keys())

REPORT_FIELD_TYPES = {
    "AccountId": "integer",
    "AdId": "integer",
    "AdGroupCriterionId": "integer",
    "AdGroupId": "integer",
    "AdRelevance": "number",
    "Assists": "integer",
    "AllCostPerConversion": "number",
    "AllReturnOnAdSpend": "number",
    "BusinessCategoryId": "integer",
    "BusinessListingId": "integer",
    "CampaignId": "integer",
    "ClickCalls": "integer",
    "Clicks": "integer",
    "CostPerAssist": "number",
    "CostPerConversion": "number",
    "Ctr": "number",
    "CurrentMaxCpc": "number",
    "EstimatedClickPercent": "number",
    "EstimatedClicks": "integer",
    "EstimatedConversionRate": "number",
    "EstimatedConversions": "integer",
    "EstimatedCtr": "number",
    "EstimatedImpressionPercent": "number",
    "EstimatedImpressions": "integer",
    "ExactMatchImpressionSharePercent": "number",
    "Impressions": "integer",
    "ImpressionSharePercent": "number",
    "KeywordId": "integer",
    "LandingPageExperience": "number",
    "PhoneCalls": "integer",
    "PhoneImpressions": "integer",
    "Ptr": "number",
    "QualityImpact": "number",
    "QualityScore": "number",
    "ReturnOnAdSpend": "number",
    "SidebarBid": "number",
    "Spend": "number",
    "MonthlyBudget": "number",
    "DailySpend": "number",
    "MonthToDateSpend": "number",
    "AbsoluteTopImpressionRatePercent": "number",
    "ViewThroughConversions": "integer",
    "ViewThroughConversionsQualified": "number",
    "MainlineBid": "number",
    "Mainline1Bid": "number",
    "FirstPageBid": "number",
    **AVERAGE_FIELD_TYPES,
    **CONVERSION_FIELD_TYPES,
    **ALL_CONVERSION_FIELD_TYPES,
    **LOW_QUALITY_FIELD_TYPES,
    **REVENUE_FIELD_TYPES,
    **ALL_REVENUE_FIELD_TYPES,
    **IMPRESSION_FIELD_TYPES,
    **HISTORICAL_FIELD_TYPES,
    **BUDGET_FIELD_TYPES,
}


class ReportsMixin(ABC):
    # The directory where the file with report will be downloaded.
    file_directory: str = "/tmp"
    # timeout for reporting download operations in milliseconds
    timeout: int = 300000
    report_file_format: str = "Csv"

    primary_key: List[str] = ["TimePeriod", "Network", "DeviceType"]

    @property
    @abstractmethod
    def report_name(self) -> str:
        """
        Specifies bing ads report naming
        """
        pass

    @property
    @abstractmethod
    def report_columns(self) -> Iterable[str]:
        """
        Specifies bing ads report naming
        """
        pass

    @property
    @abstractmethod
    def report_aggregation(self) -> Optional[str]:
        """
        Specifies bing ads report aggregation type
        Supported types: Hourly, Daily, Weekly, Monthly
        """
        pass

    @property
    @abstractmethod
    def report_schema_name(self) -> str:
        """
        Specifies file name with schema
        """
        pass

    def get_json_schema(self) -> Mapping[str, Any]:
        return ResourceSchemaLoader(package_name_from_class(self.__class__)).get_schema(self.report_schema_name)

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
        start_date = self.get_start_date(stream_state, account_id)

        reporting_service = self.client.get_service("ReportingService")
        request_time_zone = reporting_service.factory.create("ReportTimeZone")

        report_time = reporting_service.factory.create("ReportTime")
        report_time.CustomDateRangeStart = self.get_request_date(reporting_service, start_date)
        report_time.CustomDateRangeEnd = self.get_request_date(reporting_service, datetime.utcnow())
        report_time.PredefinedTime = None
        report_time.ReportTimeZone = request_time_zone.GreenwichMeanTimeDublinEdinburghLisbonLondon

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
                return pendulum.from_timestamp(stream_state[account_id][self.cursor_field])

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
            current_stream_state.get(account_id, {}).get(self.cursor_field, 1),
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

    def parse_response(self, response: sudsobject.Object, **kwargs: Mapping[str, Any]) -> Iterable[Mapping]:
        if response is not None:
            for row in response.report_records:
                yield {column: self.get_column_value(row, column) for column in self.report_columns}

        yield from []

    def get_column_value(self, row: _RowReportRecord, column: str) -> Union[str, None, int, float]:
        """
        Reads field value from row and transforms string type field to numeric if possible
        """
        value = row.value(column)
        if value == "":
            return None

        if value is not None and column in REPORT_FIELD_TYPES:
            if REPORT_FIELD_TYPES[column] == "integer":
                value = 0 if value == "--" else int(value.replace(",", ""))
            elif REPORT_FIELD_TYPES[column] == "number":
                if value == "--":
                    value = 0.0
                else:
                    if "%" in value:
                        value = float(value.replace("%", "").replace(",", "")) / 100
                    else:
                        value = float(value.replace(",", ""))

        return value

    def get_report_record_timestamp(self, datestring: str) -> int:
        """
        Parse report date field based on aggregation type
        """
        if not self.report_aggregation:
            date = pendulum.from_format(datestring, "M/D/YYYY")
        else:
            if self.report_aggregation == "Hourly":
                date = pendulum.from_format(datestring, "YYYY-MM-DD|H")
            else:
                date = pendulum.parse(datestring)

        return date.int_timestamp

    def stream_slices(
        self,
        **kwargs: Mapping[str, Any],
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        for account in source_bing_ads.source.Accounts(self.client, self.config).read_records(SyncMode.full_refresh):
            yield {"account_id": account["Id"], "customer_id": account["ParentCustomerId"]}

        yield from []


class PerformanceReportsMixin(ReportsMixin):
    def get_start_date(self, stream_state: Mapping[str, Any] = None, account_id: str = None):
        start_date = super().get_start_date(stream_state, account_id)

        if self.config.get("lookback_window"):
            # Datetime subtract won't work with days = 0
            # it'll output an AirbuteError
            return start_date.subtract(days=self.config["lookback_window"])
        else:
            return start_date
