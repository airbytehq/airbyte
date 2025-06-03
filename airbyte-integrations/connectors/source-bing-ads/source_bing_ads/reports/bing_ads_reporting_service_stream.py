#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import _csv
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Set, Tuple, Union

import pendulum
from bingads import ServiceClient
from bingads.v13.internal.reporting.row_report import _RowReport
from bingads.v13.internal.reporting.row_report_iterator import _RowReportRecord
from bingads.v13.reporting import ReportingDownloadParameters
from cached_property import cached_property
from suds import sudsobject

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.core import package_name_from_class
from airbyte_cdk.sources.utils.schema_helpers import ResourceSchemaLoader
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from source_bing_ads.base_streams import Accounts, BingAdsStream


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
            # we've observed that account_id is being passed as an integer upstream, so we convert it to string
            parsed_account_id = str(account_id)
            if stream_state.get(parsed_account_id, {}).get(self.cursor_field):
                return pendulum.parse(stream_state[parsed_account_id][self.cursor_field])

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
