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

from datetime import datetime
from typing import Any, Iterable, Mapping, MutableMapping, Optional, Union
import abc

import source_bing_ads.source
from airbyte_cdk.models import SyncMode
from bingads.v13.reporting import ReportingDownloadParameters
from bingads.v13.internal.reporting.row_report import _RowReport
from suds import sudsobject
import pendulum


class IncrementalReportStream(abc.ABC):
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
    def cursor_aggregation(self) -> Iterable[str]:
        """
        Specifies bing ads report naming
        """
        pass

    def get_request_date(self, reporting_service, date: datetime) -> sudsobject.Object:
        request_date = reporting_service.factory.create("Date")
        request_date.Day = date.day
        request_date.Month = date.month
        request_date.Year = date.year
        return request_date

    def request_params(
        self,
        stream_state: Mapping[str, Any] = None,
        account_id: str = None,
        **kwargs: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        if not stream_state or not account_id or not stream_state.get(account_id, {}).get(self.cursor_field):
            start_date = self.client.reports_start_date
        else:
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

    def get_record_state_field(self, latest_record: Mapping[str, Any]) -> str:
        return ":".join([latest_record[key] for key in self.cursor_aggregation])

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        field_name = self.get_record_state_field(latest_record)

        current_stream_state[field_name] = max(
            pendulum.parse(latest_record[self.cursor_field]).int_timestamp,
            current_stream_state.get(field_name, 1),
        )
        return current_stream_state

    def send_request(self, params: Mapping[str, Any], account_id: str) -> _RowReport:
        request_kwargs = {
            "service_name": None,
            "account_id": account_id,
            "operation_name": self.operation_name,
            "is_report_service": True,
            "params": {
                "download_parameters": ReportingDownloadParameters(**params)
            },
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
                yield {column: row.value(column) for column in self.report_columns}

        yield from []

    def stream_slices(
        self,
        **kwargs: Mapping[str, Any],
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        for account in source_bing_ads.source.Accounts(self.client, self.config).read_records(SyncMode.full_refresh):
            yield {"account_id": account["Id"]}

        yield from []
