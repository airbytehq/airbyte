#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import abc
from datetime import datetime
from typing import Any, Iterable, Mapping, MutableMapping, Optional, Union

import pendulum
import source_bing_ads.source
from airbyte_cdk.models import SyncMode
from bingads.v13.internal.reporting.row_report import _RowReport
from bingads.v13.internal.reporting.row_report_iterator import _RowReportRecord
from bingads.v13.reporting import ReportingDownloadParameters
from suds import sudsobject

REPORT_FIELD_TYPES = {
    "AccountId": "integer",
    "AdId": "integer",
    "AdGroupCriterionId": "integer",
    "AdGroupId": "integer",
    "AdRelevance": "number",
    "Assists": "integer",
    "AverageCpc": "number",
    "AveragePosition": "number",
    "BusinessCategoryId": "integer",
    "BusinessListingId": "integer",
    "CampaignId": "integer",
    "ClickCalls": "integer",
    "Clicks": "integer",
    "ConversionRate": "number",
    "Conversions": "number",
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
    "HistoricAdRelevance": "number",
    "Impressions": "integer",
    "ImpressionSharePercent": "number",
    "KeywordId": "integer",
    "LandingPageExperience": "number",
    "LowQualityClicks": "integer",
    "LowQualityClicksPercent": "number",
    "LowQualityImpressions": "integer",
    "LowQualitySophisticatedClicks": "integer",
    "PhoneCalls": "integer",
    "PhoneImpressions": "integer",
    "QualityImpact": "number",
    "QualityScore": "number",
    "ReturnOnAdSpend": "number",
    "Revenue": "number",
    "RevenuePerAssist": "number",
    "RevenuePerConversion": "number",
    "SidebarBid": "number",
    "Spend": "number",
    "MonthlyBudget": "number",
    "DailySpend": "number",
    "MonthToDateSpend": "number",
}


class ReportsMixin(abc.ABC):
    file_directory: str = "/tmp"
    timeout: int = 60000  # in milliseconds
    report_file_format: str = "Csv"
    # list of possible aggregations
    # https://docs.microsoft.com/en-us/advertising/reporting-service/reportaggregation?view=bingads-13
    # if None aggregation is disabled
    aggregation: Optional[str] = None

    @property
    @abc.abstractmethod
    def report_name(self) -> str:
        """
        Specifies bing ads report naming
        """
        pass

    @property
    @abc.abstractmethod
    def report_columns(self) -> Iterable[str]:
        """
        Specifies bing ads report naming
        """
        pass

    @property
    @abc.abstractmethod
    def date_format(self) -> Iterable[str]:
        """
        Specifies format for cursor field
        """
        pass

    def get_request_date(self, reporting_service, date: datetime) -> sudsobject.Object:
        request_date = reporting_service.factory.create("Date")
        request_date.Day = date.day
        request_date.Month = date.month
        request_date.Year = date.year
        return request_date

    def request_params(
        self, stream_state: Mapping[str, Any] = None, account_id: str = None, **kwargs: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        if not stream_state or not account_id or not stream_state.get(account_id, {}).get(self.cursor_field):
            start_date = self.client.reports_start_date
        else:
            # gets starting point for a stream and account
            start_date = pendulum.from_timestamp(stream_state[account_id][self.cursor_field])

        reporting_service = self.client.get_service("ReportingService")
        request_start_date = self.get_request_date(reporting_service, start_date)
        request_end_date = self.get_request_date(reporting_service, datetime.utcnow())
        request_time_zone = reporting_service.factory.create("ReportTimeZone")

        report_time = reporting_service.factory.create("ReportTime")
        report_time.CustomDateRangeStart = request_start_date
        report_time.CustomDateRangeEnd = request_end_date
        report_time.PredefinedTime = None
        report_time.ReportTimeZone = request_time_zone.GreenwichMeanTimeDublinEdinburghLisbonLondon

        report_request = self.get_report_request(
            account_id, self.aggregation, False, False, False, self.report_file_format, False, report_time
        )

        return {
            "report_request": report_request,
            "result_file_directory": self.file_directory,
            "result_file_name": self.report_name,
            "overwrite_result_file": True,
            "timeout_in_milliseconds": self.timeout,
        }

    def get_updated_state(
        self,
        current_stream_state: MutableMapping[str, Any],
        latest_record: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        account_id = latest_record["AccountId"]
        current_stream_state[account_id] = current_stream_state.get(account_id, {})
        current_stream_state[account_id][self.cursor_field] = max(
            pendulum.from_format(latest_record[self.cursor_field], self.date_format).int_timestamp,
            current_stream_state.get(account_id, {}).get(self.cursor_field, 1),
        )
        return current_stream_state

    def send_request(self, params: Mapping[str, Any], account_id: str) -> _RowReport:
        request_kwargs = {
            "service_name": None,
            "account_id": account_id,
            "operation_name": self.operation_name,
            "is_report_service": True,
            "params": {"download_parameters": ReportingDownloadParameters(**params)},
        }
        return self.client.request(**request_kwargs)

    def get_report_request(
        self,
        account_id: str,
        aggregation: Optional[str],
        exclude_column_headers: bool,
        exclude_report_footer: bool,
        exclude_report_header: bool,
        report_file_format: str,
        return_only_complete_data: bool,
        time: sudsobject.Object,
    ) -> sudsobject.Object:
        reporting_service = self.client.get_service(self.service_name)
        report_request = reporting_service.factory.create(f"{self.report_name}Request")
        if aggregation:
            report_request.Aggregation = aggregation

        report_request.ExcludeColumnHeaders = exclude_column_headers
        report_request.ExcludeReportFooter = exclude_report_footer
        report_request.ExcludeReportHeader = exclude_report_header
        report_request.Format = report_file_format
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
                value = 0.0 if value == "--" else float(value.replace("%", "").replace(",", ""))

        return value

    def stream_slices(
        self,
        **kwargs: Mapping[str, Any],
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        for account in source_bing_ads.source.Accounts(self.client, self.config).read_records(SyncMode.full_refresh):
            yield {"account_id": account["Id"]}

        yield from []
