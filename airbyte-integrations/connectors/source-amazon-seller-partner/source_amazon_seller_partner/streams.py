#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import csv
import gzip
import json
import logging
import os
import time
from abc import ABC, abstractmethod
from datetime import timedelta
from enum import Enum
from functools import lru_cache
from io import StringIO
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union

import pendulum
import requests

from airbyte_cdk import BackoffStrategy
from airbyte_cdk.entrypoint import logger
from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies import ExponentialBackoffStrategy
from airbyte_cdk.sources.streams.core import CheckpointMixin, package_name_from_class
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.error_handlers import ErrorHandler, ErrorResolution, HttpStatusErrorHandler, ResponseAction
from airbyte_cdk.sources.streams.http.rate_limiting import default_backoff_handler
from airbyte_cdk.sources.utils.schema_helpers import ResourceSchemaLoader
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from source_amazon_seller_partner.utils import threshold_period_decorator


REPORTS_API_VERSION = "2021-06-30"
ORDERS_API_VERSION = "v0"
VENDORS_API_VERSION = "v1"
FINANCES_API_VERSION = "v0"
VENDOR_ORDERS_API_VERSION = "v1"

DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
DATE_FORMAT = "%Y-%m-%d"

IS_TESTING = os.environ.get("DEPLOYMENT_MODE") == "testing"


class AmazonSPStream(HttpStream, ABC):
    data_field = "payload"

    def __init__(
        self,
        url_base: str,
        replication_start_date: str,
        marketplace_id: str,
        period_in_days: Optional[int],
        replication_end_date: Optional[str],
        report_options: Optional[List[Mapping[str, Any]]] = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self._url_base = url_base.rstrip("/") + "/"
        self._replication_start_date = replication_start_date
        self._replication_end_date = replication_end_date
        self.marketplace_id = marketplace_id

    @property
    def url_base(self) -> str:
        return self._url_base

    def request_headers(self, *args, **kwargs) -> Mapping[str, Any]:
        return {"content-type": "application/json"}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def retry_factor(self) -> float:
        """
        Override for testing purposes
        """
        return 0 if IS_TESTING else super().retry_factor


class IncrementalAmazonSPStream(AmazonSPStream, CheckpointMixin, ABC):
    page_size = 100

    @property
    @abstractmethod
    def replication_start_date_field(self) -> str:
        pass

    @property
    @abstractmethod
    def replication_end_date_field(self) -> str:
        pass

    @property
    @abstractmethod
    def next_page_token_field(self) -> str:
        pass

    @property
    @abstractmethod
    def page_size_field(self) -> str:
        pass

    @property
    @abstractmethod
    def cursor_field(self) -> Union[str, List[str]]:
        pass

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self._state

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        self._state = value

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._state = {}

    def request_params(
        self, stream_state: Mapping[str, Any], next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        if next_page_token:
            return dict(next_page_token)

        start_date = self._replication_start_date
        params = {self.replication_start_date_field: start_date, self.page_size_field: self.page_size}

        if self.cursor_field:
            start_date = max(stream_state.get(self.cursor_field, self._replication_start_date), self._replication_start_date)
            start_date = min(start_date, pendulum.now("utc").to_date_string())
            params[self.replication_start_date_field] = start_date

        if self._replication_end_date:
            params[self.replication_end_date_field] = max(self._replication_end_date, start_date)

        return params

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        stream_data = response.json()
        next_page_token = stream_data.get("payload").get(self.next_page_token_field)
        if next_page_token:
            return {self.next_page_token_field: next_page_token}

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        **kwargs: Any,
    ) -> Iterable[Mapping]:
        """
        Return an iterable containing each record in the response
        """
        yield from response.json().get(self.data_field, [])

    def _get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's
        most recent state object and returning an updated state object.
        """
        latest_record_state = latest_record[self.cursor_field]
        if stream_state := current_stream_state.get(self.cursor_field):
            return {self.cursor_field: max(latest_record_state, stream_state)}
        return {self.cursor_field: latest_record_state}

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        for record in super().read_records(sync_mode, cursor_field, stream_slice, stream_state):
            self.state = self._get_updated_state(self.state, record)
            yield record


class ReportProcessingStatus(str, Enum):
    CANCELLED = "CANCELLED"
    DONE = "DONE"
    FATAL = "FATAL"
    IN_PROGRESS = "IN_PROGRESS"
    IN_QUEUE = "IN_QUEUE"


class ReportsAmazonSPStream(HttpStream, ABC):
    """
    API docs: https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference

    Report streams are intended to work as following:
        - create a new report;
        - retrieve the report;
        - retry the retrieval if the report is still not fully processed;
        - retrieve the report document (if report processing status is `DONE`);
        - decrypt the report document (if report processing status is `DONE`);
        - yield the report document (if report processing status is `DONE`)
    """

    max_wait_seconds = 3600
    replication_start_date_limit_in_days = 365

    primary_key = None
    path_prefix = f"reports/{REPORTS_API_VERSION}"
    sleep_seconds = 30
    data_field = "payload"
    result_key = None

    # see data availability sla at
    # https://developer-docs.amazon.com/sp-api/docs/report-type-values#vendor-retail-analytics-reports
    availability_sla_days = 1
    availability_strategy = None
    report_name = None

    def __init__(
        self,
        url_base: str,
        replication_start_date: str,
        marketplace_id: str,
        stream_name: str,
        period_in_days: Optional[int],
        replication_end_date: Optional[str],
        report_options: Optional[List[Mapping[str, Any]]] = None,
        wait_to_avoid_fatal_errors: Optional[bool] = False,
        *args,
        **kwargs,
    ):
        self._url_base = url_base.rstrip("/") + "/"
        self._replication_start_date = replication_start_date
        self._replication_end_date = replication_end_date
        self.marketplace_id = marketplace_id
        self.period_in_days = min(period_in_days, self.replication_start_date_limit_in_days)  # ensure old configs work
        self._report_options = report_options
        self._http_method = "GET"
        self._stream_name = stream_name
        super().__init__(*args, **kwargs)

        self.wait_to_avoid_fatal_errors = wait_to_avoid_fatal_errors

    @property
    def name(self):
        return self._stream_name

    @lru_cache(maxsize=None)
    def get_json_schema(self) -> Mapping[str, Any]:
        return ResourceSchemaLoader(package_name_from_class(self.__class__)).get_schema(self.report_name)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    @property
    def http_method(self) -> str:
        return self._http_method

    @http_method.setter
    def http_method(self, value: str):
        self._http_method = value

    @property
    def retry_factor(self) -> float:
        """
        Set this 60.0 due to
        https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference#post-reports2021-06-30reports
        Override to 0 for integration testing purposes
        """
        return 0 if IS_TESTING else 60.0

    def get_backoff_strategy(self) -> Optional[Union[BackoffStrategy, List[BackoffStrategy]]]:
        return ExponentialBackoffStrategy(config={}, parameters={}, factor=self.retry_factor)

    @property
    def url_base(self) -> str:
        return self._url_base

    def request_params(self) -> MutableMapping[str, Any]:
        return {"MarketplaceIds": self.marketplace_id}

    def request_headers(self) -> Mapping[str, Any]:
        return {"content-type": "application/json"}

    def path(self, document_id: str) -> str:
        return f"{self.path_prefix}/documents/{document_id}"

    def _report_data(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Mapping[str, Any]:
        params = {"reportType": self.name, "marketplaceIds": [self.marketplace_id], **(stream_slice or {})}
        options = self.report_options()
        if options is not None:
            params.update({"reportOptions": options})
        return params

    def _create_report(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Mapping[str, Any]:
        request_headers = self.request_headers()
        report_data = self._report_data(sync_mode, cursor_field, stream_slice, stream_state)
        _, report_response = self._http_client.send_request(
            http_method="POST",
            url=self._join_url(
                self.url_base,
                f"{self.path_prefix}/reports",
            ),
            request_kwargs={},
            headers=dict(request_headers, **self._http_client._session.auth.get_auth_header()),
            data=json.dumps(report_data),
        )
        return report_response.json()

    def _retrieve_report(self, report_id: str) -> Mapping[str, Any]:
        request_headers = self.request_headers()
        _, retrieve_report_response = self._http_client.send_request(
            http_method="GET",
            url=self._join_url(self.url_base, f"{self.path_prefix}/reports/{report_id}"),
            request_kwargs={},
            headers=dict(request_headers, **self._http_client._session.auth.get_auth_header()),
        )
        report_payload = retrieve_report_response.json()

        return report_payload

    def _retrieve_report_result(self, report_document_id: str) -> requests.Response:
        request_headers = self.request_headers()
        _, response = self._http_client.send_request(
            http_method="GET",
            url=self._join_url(self.url_base, self.path(document_id=report_document_id)),
            request_kwargs={},
            headers=dict(request_headers, **self._http_client._session.auth.get_auth_header()),
            params=self.request_params(),
        )
        return response

    @default_backoff_handler(factor=5, max_tries=5)
    def download_and_decompress_report_document(self, payload: dict) -> str:
        """
        Unpacks a report document
        """
        _, report = self._http_client.send_request(
            http_method="GET",
            url=self._join_url(self.url_base, payload.get("url")),
            request_kwargs={},
        )
        if "compressionAlgorithm" in payload:
            return gzip.decompress(report.content).decode("iso-8859-1")
        return report.content.decode("iso-8859-1")

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        **kwargs: Any,
    ) -> Iterable[Mapping]:
        payload = response.json()

        document = self.download_and_decompress_report_document(payload)

        document_records = self.parse_document(document)
        yield from document_records

    def parse_document(self, document):
        return csv.DictReader(StringIO(document), delimiter="\t")

    def report_options(self) -> Optional[Mapping[str, Any]]:
        return {option.get("option_name"): option.get("option_value") for option in self._report_options} if self._report_options else None

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        now = pendulum.now("utc")
        start_date = pendulum.parse(self._replication_start_date)
        end_date = now
        if self._replication_end_date:
            end_date = min(end_date, pendulum.parse(self._replication_end_date))

        if stream_state:
            state = stream_state.get(self.cursor_field)
            start_date = state and pendulum.parse(state) or start_date

        start_date = min(start_date, end_date)
        while start_date < end_date:
            end_date_slice = start_date.add(days=self.period_in_days)
            yield {
                "dataStartTime": start_date.strftime(DATE_TIME_FORMAT),
                "dataEndTime": min(end_date_slice.subtract(seconds=1), end_date).strftime(DATE_TIME_FORMAT),
            }
            start_date = end_date_slice

    def get_error_handler(self) -> Optional[ErrorHandler]:
        class AmazonSPErrorHandler(HttpStatusErrorHandler):
            def interpret_response(self, response_or_exception: Optional[Union[requests.Response, Exception]] = None) -> ErrorResolution:
                if (
                    not isinstance(response_or_exception, Exception)
                    and response_or_exception.status_code != 200
                    and response_or_exception.status_code != 202
                ):
                    response = response_or_exception
                    errors = " ".join([er.get("message", "") for er in response.json().get("errors", [])])
                    if response.status_code == requests.codes.BAD_REQUEST:
                        invalid_report_names = list(
                            map(
                                lambda error: error.get("message").replace("Invalid Report Type ", ""),
                                filter(lambda error: "Invalid Report Type " in error.get("message"), response.json().get("errors", [])),
                            )
                        )
                        if invalid_report_names:
                            return ErrorResolution(
                                response_action=ResponseAction.IGNORE,
                                failure_type=FailureType.config_error,
                                error_message=f"Report {invalid_report_names} does not exist. Please update the report options in your config to match only existing reports.",
                                # internal_message=f"Errors received from the API were: {errors}",
                            )
                    if response.status_code == requests.codes.FORBIDDEN:
                        return ErrorResolution(
                            response_action=ResponseAction.FAIL,
                            failure_type=FailureType.config_error,
                            error_message=f"The endpoint {response.url} returned {response.status_code}: {response.reason}. "
                            "This is most likely due to insufficient permissions on the credentials in use. "
                            "Try to grant required permissions/scopes or re-authenticate.",
                            # internal_message=f"Errors received from the API were: {errors}",
                        )
                    if response.status_code == requests.codes.TOO_MANY_REQUESTS:
                        return ErrorResolution(
                            response_action=ResponseAction.RATE_LIMITED,
                            failure_type=FailureType.transient_error,
                            error_message=f"Too many requests on resource {response.url}. Please retry later",
                            # internal_message=f"Errors received from the API were: {errors}",
                        )

                    if "does not support account ID of type class com.amazon.partner.account.id.VendorGroupId." in errors:
                        return ErrorResolution(
                            response_action=ResponseAction.IGNORE,
                            failure_type=FailureType.config_error,
                            error_message=f"The endpoint {response.url} returned {response.status_code}: {errors}. "
                            "This is most likely due to account type (Vendor) on the credentials in use. "
                            "Try to re-authenticate with Seller account type and sync again.",
                            # internal_message=f"Errors received from the API were: {errors}",
                        )

                    return ErrorResolution(
                        response_action=ResponseAction.FAIL,
                        failure_type=FailureType.system_error,
                        error_message="The report for stream '{self.name}' was cancelled due to several failed retry attempts.",
                    )
                    # raise AirbyteTracedException.from_exception(
                    #     e, message=f"The report for stream '{self.name}' was cancelled due to several failed retry attempts."
                    # )
                else:
                    return super().interpret_response(response_or_exception)

        # return AmazonSPErrorHandler(logger=self.logger, max_retries=10, error_mapping=error_mapping)
        return AmazonSPErrorHandler(logger=self.logger, max_retries=10)

    @threshold_period_decorator
    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """
        Create and retrieve the report.
        Decrypt and parse the report if it's fully processed, then yield the report document records.
        """
        report_payload = {}
        stream_slice = stream_slice or {}
        start_time = pendulum.now("utc")
        seconds_waited = 0
        try:
            report_id = self._create_report(sync_mode, cursor_field, stream_slice, stream_state)["reportId"]
        except requests.exceptions.HTTPError as e:
            errors = " ".join([er.get("message", "") for er in e.response.json().get("errors", [])])
            if e.response.status_code == requests.codes.BAD_REQUEST:
                invalid_report_names = list(
                    map(
                        lambda error: error.get("message").replace("Invalid Report Type ", ""),
                        filter(lambda error: "Invalid Report Type " in error.get("message"), e.response.json().get("errors", [])),
                    )
                )
                if invalid_report_names:
                    raise AirbyteTracedException(
                        failure_type=FailureType.config_error,
                        message=f"Report {invalid_report_names} does not exist. Please update the report options in your config to match only existing reports.",
                        internal_message=f"Errors received from the API were: {errors}",
                    )
            if e.response.status_code == requests.codes.FORBIDDEN:
                raise AirbyteTracedException(
                    failure_type=FailureType.config_error,
                    message=f"The endpoint {e.response.url} returned {e.response.status_code}: {e.response.reason}. "
                    "This is most likely due to insufficient permissions on the credentials in use. "
                    "Try to grant required permissions/scopes or re-authenticate.",
                    internal_message=f"Errors received from the API were: {errors}",
                )
            if e.response.status_code == requests.codes.TOO_MANY_REQUESTS:
                raise AirbyteTracedException(
                    failure_type=FailureType.transient_error,
                    message=f"Too many requests on resource {e.response.url}. Please retry later",
                    internal_message=f"Errors received from the API were: {errors}",
                )

            if "does not support account ID of type class com.amazon.partner.account.id.VendorGroupId." in errors:
                raise AirbyteTracedException(
                    failure_type=FailureType.config_error,
                    message=f"The endpoint {e.response.url} returned {e.response.status_code}: {errors}. "
                    "This is most likely due to account type (Vendor) on the credentials in use. "
                    "Try to re-authenticate with Seller account type and sync again.",
                    internal_message=f"Errors received from the API were: {errors}",
                )
            raise AirbyteTracedException.from_exception(
                e, message=f"The report for stream '{self.name}' was cancelled due to several failed retry attempts."
            )

        # create and retrieve the report
        processed = False
        while not processed and seconds_waited < self.max_wait_seconds:
            report_payload = self._retrieve_report(report_id=report_id)
            seconds_waited = (pendulum.now("utc") - start_time).seconds
            processed = report_payload.get("processingStatus") not in (ReportProcessingStatus.IN_QUEUE, ReportProcessingStatus.IN_PROGRESS)
            if not processed:
                time.sleep(self.sleep_seconds)

        processing_status = report_payload.get("processingStatus")
        # TODO: How to process this>>>?
        report_end_date = pendulum.parse(report_payload.get("dataEndTime", stream_slice.get("dataEndTime")))
        # TODO <<<<<>>>>>>
        #  use stream_slice for test (regression)
        if processing_status == ReportProcessingStatus.DONE:
            # retrieve and decrypt the report document
            document_id = report_payload["reportDocumentId"]
            response = self._retrieve_report_result(document_id)

            for record in self.parse_response(response, stream_state, stream_slice):
                if report_end_date:
                    record["dataEndTime"] = report_end_date.strftime(DATE_FORMAT)
                yield record
        elif processing_status == ReportProcessingStatus.FATAL:
            # retrieve and decrypt the report document
            try:
                document_id = report_payload["reportDocumentId"]
                response = self._retrieve_report_result(document_id)

                document = self.download_and_decompress_report_document(response.json())
                error_response = json.loads(document)
            except Exception as e:
                logging.error(f"Failed to retrieve the report result document for stream '{self.name}'. Exception: {e}")
                error_response = "Failed to retrieve the report result document."

            exception_message = f"Failed to retrieve the report '{self.name}'"
            if stream_slice and "dataStartTime" in stream_slice:
                exception_message += (
                    f" for period {stream_slice['dataStartTime']}-{stream_slice['dataEndTime']}. "
                    f"This will be read during the next sync. Report ID: {report_id}."
                    f" Error: {error_response}"
                    " Visit https://docs.airbyte.com/integrations/sources/amazon-seller-partner#limitations--troubleshooting for more info."
                )
            raise AirbyteTracedException(internal_message=exception_message)
        elif processing_status == ReportProcessingStatus.CANCELLED:
            logger.warning(f"The report for stream '{self.name}' was cancelled or there is no data to return.")
        else:
            raise Exception(f"Unknown response for stream '{self.name}'. Response body: {report_payload}.")


class IncrementalReportsAmazonSPStream(ReportsAmazonSPStream, CheckpointMixin):
    @property
    def cursor_field(self) -> Union[str, List[str]]:
        return "dataEndTime"

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self._state

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        self._state = value

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._state = {}

    def _transform_report_record_cursor_value(self, date_string: str) -> str:
        """
        Parse report date field based using transformer defined in the stream class
        """
        return (
            self.transformer._custom_normalizer(date_string, self.get_json_schema()["properties"][self.cursor_field])
            if self.transformer._custom_normalizer
            else date_string
        )

    def _get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's
        most recent state object and returning an updated state object.
        """
        latest_record_state = self._transform_report_record_cursor_value(latest_record[self.cursor_field])
        if stream_state := current_stream_state.get(self.cursor_field):
            return {self.cursor_field: max(latest_record_state, stream_state)}
        return {self.cursor_field: latest_record_state}

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        for record in super().read_records(sync_mode, cursor_field, stream_slice, stream_state):
            self.state = self._get_updated_state(self.state, record)
            yield record


class AnalyticsStream(ReportsAmazonSPStream):
    def parse_document(self, document):
        parsed = json.loads(document)
        return parsed.get(self.result_key, [])

    # delete this method since we're not going to modify report_options anymore
    def _report_data(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Mapping[str, Any]:
        data = super()._report_data(sync_mode, cursor_field, stream_slice, stream_state)
        options = self.report_options()
        if options and options.get("reportPeriod"):
            data.update(self._augmented_data(options))
        return data

    def _augmented_data(self, report_options) -> Mapping[str, Any]:
        now = pendulum.now("utc")
        if report_options["reportPeriod"] == "DAY":
            now = now.subtract(days=self.availability_sla_days)
            data_start_time = now.start_of("day")
            data_end_time = now.end_of("day")
        elif report_options["reportPeriod"] == "WEEK":
            now = now.subtract(days=self.availability_sla_days).subtract(weeks=1)
            # According to report api docs
            # dataStartTime must be a Sunday and dataEndTime must be the following Saturday
            pendulum.week_starts_at(pendulum.SUNDAY)
            pendulum.week_ends_at(pendulum.SATURDAY)

            data_start_time = now.start_of("week")
            data_end_time = now.end_of("week")

            # Reset week start and end
            pendulum.week_starts_at(pendulum.MONDAY)
            pendulum.week_ends_at(pendulum.SUNDAY)
        elif report_options["reportPeriod"] == "MONTH":
            now = now.subtract(months=1)
            data_start_time = now.start_of("month")
            data_end_time = now.end_of("month")
        else:
            raise Exception([{"message": "This reportPeriod is not implemented."}])

        return {
            "dataStartTime": data_start_time.strftime(DATE_TIME_FORMAT),
            "dataEndTime": data_end_time.strftime(DATE_TIME_FORMAT),
            "reportOptions": report_options,
        }


class IncrementalAnalyticsStream(AnalyticsStream, CheckpointMixin):
    fixed_period_in_days = 0

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self._state

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        self._state = value

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        return "endDate"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._state = {}

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        **kwargs: Any,
    ) -> Iterable[Mapping]:
        payload = response.json()

        document = self.download_and_decompress_report_document(payload)
        document_records = self.parse_document(document)

        # Not all (partial) responses include the request date, so adding it manually here
        for record in document_records:
            if stream_slice.get("dataEndTime"):
                record["queryEndDate"] = pendulum.parse(stream_slice["dataEndTime"]).strftime("%Y-%m-%d")
            yield record

    # this is the same as the reports incremental method used for updating state. low-code stream doesn't need to account for deviation
    def _get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's
        most recent state object and returning an updated state object.
        """
        latest_record_state = latest_record[self.cursor_field]
        if stream_state := current_stream_state.get(self.cursor_field):
            return {self.cursor_field: max(latest_record_state, stream_state)}
        return {self.cursor_field: latest_record_state}

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        start_date = pendulum.parse(self._replication_start_date)

        # doing the interpolation of the end date we need to subtract
        end_date = pendulum.now("utc").subtract(days=self.availability_sla_days)

        if self._replication_end_date:
            end_date = pendulum.parse(self._replication_end_date)

        if stream_state:
            state = stream_state.get(self.cursor_field)
            start_date = pendulum.parse(state)

        start_date = min(start_date, end_date)

        while start_date < end_date:
            # This part needs to be incorporated into low-code analytics streams where the datetimebased cursor's step will be
            # hardcoded to the fixed_period_in_days if defined or "P{{ min( config.get('period_in_days', 365), 365 ) }}D" via incoming
            # configs
            # If request only returns data on day level
            if self.fixed_period_in_days != 0:
                slice_range = self.fixed_period_in_days
            else:
                slice_range = self.period_in_days

            end_date_slice = start_date.add(days=slice_range)
            yield {
                "dataStartTime": start_date.strftime(DATE_TIME_FORMAT),
                "dataEndTime": min(end_date_slice.subtract(seconds=1), end_date).strftime(DATE_TIME_FORMAT),
            }
            start_date = end_date_slice

    # this is equivalent to the reports incremental read records
    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        for record in super().read_records(sync_mode, cursor_field, stream_slice, stream_state):
            self.state = self._get_updated_state(self.state, record)
            yield record


class NetPureProductMarginReport(IncrementalAnalyticsStream):
    report_name = "GET_VENDOR_NET_PURE_PRODUCT_MARGIN_REPORT"
    result_key = "netPureProductMarginByAsin"


class RapidRetailAnalyticsInventoryReport(IncrementalAnalyticsStream):
    report_name = "GET_VENDOR_REAL_TIME_INVENTORY_REPORT"
    result_key = "reportData"
    cursor_field = "endTime"


class BrandAnalyticsMarketBasketReports(IncrementalAnalyticsStream):
    report_name = "GET_BRAND_ANALYTICS_MARKET_BASKET_REPORT"
    result_key = "dataByAsin"


class BrandAnalyticsSearchTermsReports(IncrementalAnalyticsStream):
    """
    Field definitions: https://sellercentral.amazon.co.uk/help/hub/reference/G5NXWNY8HUD3VDCW
    """

    report_name = "GET_BRAND_ANALYTICS_SEARCH_TERMS_REPORT"
    result_key = "dataByDepartmentAndSearchTerm"
    cursor_field = "queryEndDate"


class BrandAnalyticsRepeatPurchaseReports(IncrementalAnalyticsStream):
    report_name = "GET_BRAND_ANALYTICS_REPEAT_PURCHASE_REPORT"
    result_key = "dataByAsin"


class VendorInventoryReports(IncrementalAnalyticsStream):
    """
    Field definitions: https://developer-docs.amazon.com/sp-api/docs/report-type-values#vendor-retail-analytics-reports
    """

    report_name = "GET_VENDOR_INVENTORY_REPORT"
    result_key = "inventoryByAsin"
    availability_sla_days = 3


class VendorTrafficReport(IncrementalAnalyticsStream):
    report_name = "GET_VENDOR_TRAFFIC_REPORT"
    result_key = "trafficByAsin"
    availability_sla_days = 3
    fixed_period_in_days = 1


class SellerAnalyticsSalesAndTrafficReports(IncrementalAnalyticsStream):
    """
    Field definitions: https://developer-docs.amazon.com/sp-api/docs/report-type-values#seller-retail-analytics-reports
    """

    report_name = "GET_SALES_AND_TRAFFIC_REPORT"
    result_key = "salesAndTrafficByAsin"
    cursor_field = "queryEndDate"
    fixed_period_in_days = 1


class VendorSalesReports(IncrementalAnalyticsStream):
    report_name = "GET_VENDOR_SALES_REPORT"
    result_key = "salesByAsin"
    availability_sla_days = 4  # Data is only available after 4 days


class VendorForecastingReport(AnalyticsStream, ABC):
    """
    Field definitions:
    https://github.com/amzn/selling-partner-api-models/blob/main/schemas/reports/vendorForecastingReport.json
    Docs: https://developer-docs.amazon.com/sp-api/docs/report-type-values-analytics#vendor-retail-analytics-reports
    """

    result_key = "forecastByAsin"
    report_name = None

    @property
    @abstractmethod
    def selling_program(self) -> str:
        pass

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        return [None]

    def _report_data(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Mapping[str, Any]:
        # This report supports the `sellingProgram` parameter only
        return {
            "reportType": "GET_VENDOR_FORECASTING_REPORT",
            "marketplaceIds": [self.marketplace_id],
            "reportOptions": {"sellingProgram": self.selling_program},
        }


class VendorForecastingFreshReport(VendorForecastingReport):
    report_name = "GET_VENDOR_FORECASTING_FRESH_REPORT"
    selling_program = "FRESH"


class VendorForecastingRetailReport(VendorForecastingReport):
    report_name = "GET_VENDOR_FORECASTING_RETAIL_REPORT"
    selling_program = "RETAIL"
