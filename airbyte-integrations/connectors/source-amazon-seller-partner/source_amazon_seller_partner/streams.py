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
from enum import Enum
from functools import lru_cache
from io import StringIO
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Union

import dateparser
import pendulum
import requests
import xmltodict

from airbyte_cdk.entrypoint import logger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.core import CheckpointMixin, package_name_from_class
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.rate_limiting import default_backoff_handler
from airbyte_cdk.sources.utils.schema_helpers import ResourceSchemaLoader
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from airbyte_protocol.models import FailureType
from source_amazon_seller_partner.utils import STREAM_THRESHOLD_PERIOD, threshold_period_decorator


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
        super().__init__(*args, **kwargs)
        self._url_base = url_base.rstrip("/") + "/"
        self._replication_start_date = replication_start_date
        self._replication_end_date = replication_end_date
        self.marketplace_id = marketplace_id
        self.period_in_days = min(period_in_days, self.replication_start_date_limit_in_days)  # ensure old configs work
        self._report_options = report_options
        self._http_method = "GET"
        self._stream_name = stream_name

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
        self.http_method = "POST"
        create_report_request = self._create_prepared_request(
            path=f"{self.path_prefix}/reports",
            headers=dict(request_headers, **self.authenticator.get_auth_header()),
            data=json.dumps(report_data),
        )
        report_response = self._send_request(create_report_request, {})
        self.http_method = "GET"  # rollback
        return report_response.json()

    def _retrieve_report(self, report_id: str) -> Mapping[str, Any]:
        request_headers = self.request_headers()
        retrieve_report_request = self._create_prepared_request(
            path=f"{self.path_prefix}/reports/{report_id}",
            headers=dict(request_headers, **self.authenticator.get_auth_header()),
        )
        retrieve_report_response = self._send_request(retrieve_report_request, {})
        report_payload = retrieve_report_response.json()

        return report_payload

    def _retrieve_report_result(self, report_document_id: str) -> requests.Response:
        request_headers = self.request_headers()
        request = self._create_prepared_request(
            path=self.path(document_id=report_document_id),
            headers=dict(request_headers, **self.authenticator.get_auth_header()),
            params=self.request_params(),
        )
        return self._send_request(request, {})

    @default_backoff_handler(factor=5, max_tries=5)
    def download_and_decompress_report_document(self, payload: dict) -> str:
        """
        Unpacks a report document
        """

        download_report_request = self._create_prepared_request(path=payload.get("url"))
        report = self._send_request(download_report_request, {})
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
        report_end_date = pendulum.parse(report_payload.get("dataEndTime", stream_slice.get("dataEndTime")))

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


class MerchantReports(IncrementalReportsAmazonSPStream, ABC):
    transformer: TypeTransformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization | TransformConfig.CustomSchemaNormalization)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.transformer.registerCustomTransform(self.get_transform_function())

    @staticmethod
    def get_transform_function():
        def transform_function(original_value: Any, field_schema: Dict[str, Any]) -> Any:
            if original_value and field_schema.get("format") == "date-time":
                # open-date field is returned in format "2022-07-11 01:34:18 PDT"
                transformed_value = dateparser.parse(original_value).isoformat()
                return transformed_value
            return original_value

        return transform_function


class MerchantListingsReports(MerchantReports):
    report_name = "GET_MERCHANT_LISTINGS_ALL_DATA"
    primary_key = "listing-id"


class FlatFileOrdersReports(IncrementalReportsAmazonSPStream):
    """
    Field definitions: https://sellercentral.amazon.com/gp/help/help.html?itemID=201648780
    """

    report_name = "GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL"
    primary_key = "amazon-order-id"
    cursor_field = "last-updated-date"
    replication_start_date_limit_in_days = 30


class FbaStorageFeesReports(IncrementalReportsAmazonSPStream):
    """
    Field definitions: https://sellercentral.amazon.com/help/hub/reference/G202086720
    """

    report_name = "GET_FBA_STORAGE_FEE_CHARGES_DATA"


class FulfilledShipmentsReports(IncrementalReportsAmazonSPStream):
    """
    Field definitions: https://sellercentral.amazon.com/gp/help/help.html?itemID=200453120

    Threshold 12
    Period (minutes) 480

    """

    report_name = "GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL"

    # You can request up to one month of data in a single report
    # https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-sales-reports
    replication_start_date_limit_in_days = 30


class FlatFileOpenListingsReports(IncrementalReportsAmazonSPStream):
    report_name = "GET_FLAT_FILE_OPEN_LISTINGS_DATA"


class FbaOrdersReports(IncrementalReportsAmazonSPStream):
    """
    Field definitions: https://sellercentral.amazon.com/gp/help/help.html?itemID=200989110
    """

    report_name = "GET_FBA_FULFILLMENT_REMOVAL_ORDER_DETAIL_DATA"
    cursor_field = "last-updated-date"


class FlatFileActionableOrderDataShipping(IncrementalReportsAmazonSPStream):
    """
    Field definitions:
    https://developer-docs.amazon.com/sp-api/docs/order-reports-attributes#get_flat_file_actionable_order_data_shipping
    """

    report_name = "GET_FLAT_FILE_ACTIONABLE_ORDER_DATA_SHIPPING"


class OrderReportDataShipping(IncrementalReportsAmazonSPStream):
    """
    Field definitions:
    https://developer-docs.amazon.com/sp-api/docs/order-reports-attributes#get_order_report_data_shipping
    """

    report_name = "GET_ORDER_REPORT_DATA_SHIPPING"

    def parse_document(self, document):
        try:
            parsed = xmltodict.parse(document, attr_prefix="", cdata_key="value", force_list={"Message"})
        except Exception as e:
            self.logger.warning(f"Unable to parse the report for the stream {self.name}, error: {str(e)}")
            return []

        reports = parsed.get("AmazonEnvelope", {}).get("Message", {})
        result = []
        for report in reports:
            result.append(report.get("OrderReport", {}))

        return result


class FbaShipmentsReports(IncrementalReportsAmazonSPStream):
    """
    Field definitions: https://sellercentral.amazon.com/gp/help/help.html?itemID=200989100
    """

    report_name = "GET_FBA_FULFILLMENT_REMOVAL_SHIPMENT_DETAIL_DATA"


class FbaReplacementsReports(IncrementalReportsAmazonSPStream):
    """
    Field definitions: https://sellercentral.amazon.com/help/hub/reference/200453300
    """

    report_name = "GET_FBA_FULFILLMENT_CUSTOMER_SHIPMENT_REPLACEMENT_DATA"


class RestockInventoryReports(IncrementalReportsAmazonSPStream):
    """
    Field definitions: 	https://sellercentral.amazon.com/help/hub/reference/202105670
    """

    report_name = "GET_RESTOCK_INVENTORY_RECOMMENDATIONS_REPORT"


class GetXmlBrowseTreeData(IncrementalReportsAmazonSPStream):
    def parse_document(self, document):
        try:
            parsed = xmltodict.parse(
                document,
                dict_constructor=dict,
                attr_prefix="",
                cdata_key="text",
                force_list={"attribute", "id", "refinementField"},
            )
        except Exception as e:
            self.logger.warning(f"Unable to parse the report for the stream {self.name}, error: {str(e)}")
            return []

        return parsed.get("Result", {}).get("Node", [])

    report_name = "GET_XML_BROWSE_TREE_DATA"
    primary_key = "browseNodeId"


class FbaEstimatedFbaFeesTxtReport(IncrementalReportsAmazonSPStream):
    """

    Threshold 2000
    Period (minutes) 60

    """

    report_name = "GET_FBA_ESTIMATED_FBA_FEES_TXT_DATA"


class FbaFulfillmentCustomerShipmentPromotionReport(IncrementalReportsAmazonSPStream):
    report_name = "GET_FBA_FULFILLMENT_CUSTOMER_SHIPMENT_PROMOTION_DATA"


class FbaMyiUnsuppressedInventoryReport(IncrementalReportsAmazonSPStream):
    report_name = "GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA"


class MerchantListingsReport(MerchantReports):
    report_name = "GET_MERCHANT_LISTINGS_DATA"
    primary_key = "listing-id"


class MerchantListingsInactiveData(MerchantReports):
    report_name = "GET_MERCHANT_LISTINGS_INACTIVE_DATA"
    primary_key = "listing-id"


class StrandedInventoryUiReport(IncrementalReportsAmazonSPStream):
    report_name = "GET_STRANDED_INVENTORY_UI_DATA"


class XmlAllOrdersDataByOrderDataGeneral(IncrementalReportsAmazonSPStream):
    report_name = "GET_XML_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL"
    primary_key = "AmazonOrderID"
    cursor_field = "LastUpdatedDate"

    def parse_document(self, document):
        try:
            parsed = xmltodict.parse(document, attr_prefix="", cdata_key="value", force_list={"Message", "OrderItem"})
        except Exception as e:
            self.logger.warning(f"Unable to parse the report for the stream {self.name}, error: {str(e)}")
            return []

        orders = parsed.get("AmazonEnvelope", {}).get("Message", [])
        result = []
        if isinstance(orders, list):
            for order in orders:
                result.append(order.get("Order", {}))

        return result


class MerchantListingsReportBackCompat(MerchantReports):
    report_name = "GET_MERCHANT_LISTINGS_DATA_BACK_COMPAT"
    primary_key = "listing-id"


class MerchantCancelledListingsReport(IncrementalReportsAmazonSPStream):
    report_name = "GET_MERCHANT_CANCELLED_LISTINGS_DATA"


class MerchantListingsFypReport(IncrementalReportsAmazonSPStream):
    report_name = "GET_MERCHANTS_LISTINGS_FYP_REPORT"
    transformer: TypeTransformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization | TransformConfig.CustomSchemaNormalization)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.transformer.registerCustomTransform(self.get_transform_function())

    @staticmethod
    def get_transform_function():
        def transform_function(original_value: Any, field_schema: Dict[str, Any]) -> Any:
            if original_value and field_schema.get("format") == "date":
                try:
                    transformed_value = pendulum.from_format(original_value, "MMM D[,] YYYY").to_date_string()
                    return transformed_value
                except ValueError:
                    pass
            return original_value

        return transform_function


class FbaSnsForecastReport(IncrementalReportsAmazonSPStream):
    report_name = "GET_FBA_SNS_FORECAST_DATA"


class FbaSnsPerformanceReport(IncrementalReportsAmazonSPStream):
    report_name = "GET_FBA_SNS_PERFORMANCE_DATA"


class FlatFileArchivedOrdersDataByOrderDate(IncrementalReportsAmazonSPStream):
    report_name = "GET_FLAT_FILE_ARCHIVED_ORDERS_DATA_BY_ORDER_DATE"
    cursor_field = "last-updated-date"


class FlatFileReturnsDataByReturnDate(IncrementalReportsAmazonSPStream):
    report_name = "GET_FLAT_FILE_RETURNS_DATA_BY_RETURN_DATE"

    # You can request up to 60 days of data in a single report
    # https://developer-docs.amazon.com/sp-api/docs/report-type-values-returns
    replication_start_date_limit_in_days = 60


class FbaInventoryPlaningReport(IncrementalReportsAmazonSPStream):
    report_name = "GET_FBA_INVENTORY_PLANNING_DATA"


class AnalyticsStream(ReportsAmazonSPStream):
    def parse_document(self, document):
        parsed = json.loads(document)
        return parsed.get(self.result_key, [])

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
        end_date = pendulum.now("utc").subtract(days=self.availability_sla_days)

        if self._replication_end_date:
            end_date = pendulum.parse(self._replication_end_date)

        if stream_state:
            state = stream_state.get(self.cursor_field)
            start_date = pendulum.parse(state)

        start_date = min(start_date, end_date)

        while start_date < end_date:
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


class SellerFeedbackReports(IncrementalReportsAmazonSPStream):
    """
    Field definitions: https://sellercentral.amazon.com/help/hub/reference/G202125660
    """

    # The list of MarketplaceIds can be found here:
    # https://docs.developer.amazonservices.com/en_UK/dev_guide/DG_Endpoints.html
    MARKETPLACE_DATE_FORMAT_MAP = dict(
        # eu
        A2VIGQ35RCS4UG="D/M/YY",  # AE
        A1PA6795UKMFR9="D.M.YY",  # DE
        A1C3SOZRARQ6R3="D/M/YY",  # PL
        ARBP9OOSHTCHU="D/M/YY",  # EG
        A1RKKUPIHCS9HS="D/M/YY",  # ES
        A13V1IB3VIYZZH="D/M/YY",  # FR
        A21TJRUUN4KGV="D/M/YY",  # IN
        APJ6JRA9NG5V4="D/M/YY",  # IT
        A1805IZSGTT6HS="D/M/YY",  # NL
        A17E79C6D8DWNP="D/M/YY",  # SA
        A2NODRKZP88ZB9="YYYY-MM-DD",  # SE
        A33AVAJ2PDY3EV="D/M/YY",  # TR
        A1F83G8C2ARO7P="D/M/YY",  # UK
        AMEN7PMS3EDWL="D/M/YY",  # BE
        # fe
        A39IBJ37TRP1C6="D/M/YY",  # AU
        A1VC38T7YXB528="YY/M/D",  # JP
        A19VAU5U5O7RUS="D/M/YY",  # SG
        # na
        ATVPDKIKX0DER="M/D/YY",  # US
        A2Q3Y263D00KWC="D/M/YY",  # BR
        A2EUQ1WTGCTBG2="D/M/YY",  # CA
        A1AM78C64UM0Y8="D/M/YY",  # MX
    )

    NORMALIZED_FIELD_NAMES = ["date", "rating", "comments", "response", "order_id", "rater_email"]

    report_name = "GET_SELLER_FEEDBACK_DATA"
    cursor_field = "date"
    transformer: TypeTransformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization | TransformConfig.CustomSchemaNormalization)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.transformer.registerCustomTransform(self.get_transform_function())

    def get_transform_function(self):
        def transform_function(original_value: Any, field_schema: Dict[str, Any]) -> Any:
            if original_value and field_schema.get("format") == "date":
                date_format = self.MARKETPLACE_DATE_FORMAT_MAP.get(self.marketplace_id)
                if not date_format:
                    raise KeyError(f"Date format not found for Marketplace ID: {self.marketplace_id}")
                try:
                    transformed_value = pendulum.from_format(original_value, date_format).to_date_string()
                    return transformed_value
                except ValueError:
                    pass

            return original_value

        return transform_function

    # csv header field names for this report differ per marketplace (are localized to marketplace language)
    # but columns come in the same order, so we set fieldnames to our custom ones
    # and raise error if original and custom header field count does not match
    @staticmethod
    def parse_document(document):
        reader = csv.DictReader(StringIO(document), delimiter="\t", fieldnames=SellerFeedbackReports.NORMALIZED_FIELD_NAMES)
        original_fieldnames = next(reader)
        if len(original_fieldnames) != len(SellerFeedbackReports.NORMALIZED_FIELD_NAMES):
            raise ValueError("Original and normalized header field count does not match")

        return reader


class FbaAfnInventoryReports(IncrementalReportsAmazonSPStream):
    """
    Field definitions: https://developer-docs.amazon.com/sp-api/docs/report-type-values#inventory-reports
    Report has a long-running issue (fails when requested frequently):
    https://github.com/amzn/selling-partner-api-docs/issues/2231

    Threshold 2
    Period (minutes) 25

    """

    report_name = "GET_AFN_INVENTORY_DATA"


class FbaAfnInventoryByCountryReports(IncrementalReportsAmazonSPStream):
    """
    Field definitions: https://developer-docs.amazon.com/sp-api/docs/report-type-values#inventory-reports
    Report has a long-running issue (fails when requested frequently):
    https://github.com/amzn/selling-partner-api-docs/issues/2231
    """

    report_name = "GET_AFN_INVENTORY_DATA_BY_COUNTRY"


class FlatFileOrdersReportsByLastUpdate(IncrementalReportsAmazonSPStream):
    """
    Field definitions: https://sellercentral.amazon.com/gp/help/help.html?itemID=201648780
    """

    report_name = "GET_FLAT_FILE_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL"
    primary_key = "amazon-order-id"
    cursor_field = "last-updated-date"
    replication_start_date_limit_in_days = 30


class Orders(IncrementalAmazonSPStream):
    """
    API docs: https://developer-docs.amazon.com/sp-api/docs/orders-api-v0-reference
    API model: https://github.com/amzn/selling-partner-api-models/blob/main/models/orders-api-model/ordersV0.json
    """

    name = "Orders"
    primary_key = "AmazonOrderId"
    cursor_field = "LastUpdateDate"
    replication_start_date_field = "LastUpdatedAfter"
    replication_end_date_field = "LastUpdatedBefore"
    next_page_token_field = "NextToken"
    page_size_field = "MaxResultsPerPage"
    default_backoff_time = 60
    use_cache = True

    def path(self, **kwargs) -> str:
        return f"orders/{ORDERS_API_VERSION}/orders"

    def request_params(
        self, stream_state: Mapping[str, Any], next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, next_page_token=next_page_token, **kwargs)
        params["MarketplaceIds"] = self.marketplace_id
        return params

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        **kwargs: Any,
    ) -> Iterable[Mapping]:
        yield from response.json().get(self.data_field, {}).get(self.name, [])

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        rate_limit = response.headers.get("x-amzn-RateLimit-Limit", 0)
        if rate_limit:
            return 1 / float(rate_limit)
        else:
            return self.default_backoff_time


class OrderItems(IncrementalAmazonSPStream):
    """
    API docs: https://developer-docs.amazon.com/sp-api/docs/orders-api-v0-reference#getorderitems
    API model: https://developer-docs.amazon.com/sp-api/docs/orders-api-v0-reference#orderitemslist
    """

    name = "OrderItems"
    primary_key = "OrderItemId"
    cursor_field = "LastUpdateDate"
    parent_cursor_field = "LastUpdateDate"
    next_page_token_field = "NextToken"
    stream_slice_cursor_field = "AmazonOrderId"
    replication_start_date_field = "LastUpdatedAfter"
    replication_end_date_field = "LastUpdatedBefore"
    page_size_field = None
    default_backoff_time = 10
    default_stream_slice_delay_time = 1
    cached_state: Dict = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stream_kwargs = kwargs

    def path(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        return f"orders/{ORDERS_API_VERSION}/orders/{stream_slice[self.stream_slice_cursor_field]}/orderItems"

    def request_params(
        self, stream_state: Mapping[str, Any], next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        if next_page_token:
            return dict(next_page_token)
        return {}

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        orders = Orders(**self.stream_kwargs)
        for order_record in orders.read_records(sync_mode=SyncMode.incremental, stream_state=stream_state):
            self.cached_state[self.parent_cursor_field] = order_record[self.parent_cursor_field]
            time.sleep(self.default_stream_slice_delay_time)
            yield {
                self.stream_slice_cursor_field: order_record[self.stream_slice_cursor_field],
                self.parent_cursor_field: order_record[self.parent_cursor_field],
            }

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        stream_data = response.json()
        next_page_token = stream_data.get("payload").get(self.next_page_token_field)
        if next_page_token:
            return {self.next_page_token_field: next_page_token}

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        rate_limit = response.headers.get("x-amzn-RateLimit-Limit", 0)
        if rate_limit:
            return 1 / float(rate_limit)
        else:
            return self.default_backoff_time

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        **kwargs: Any,
    ) -> Iterable[Mapping]:
        order_items_list = response.json().get(self.data_field, {})
        if order_items_list.get(self.next_page_token_field) is None:
            self.cached_state[self.parent_cursor_field] = stream_slice[self.parent_cursor_field]
        for order_item in order_items_list.get(self.name, []):
            order_item[self.cursor_field] = stream_slice.get(self.parent_cursor_field)
            order_item[self.stream_slice_cursor_field] = order_items_list.get(self.stream_slice_cursor_field)
            yield order_item


class LedgerDetailedViewReports(IncrementalReportsAmazonSPStream):
    """
    API docs: https://developer-docs.amazon.com/sp-api/docs/report-type-values
    """

    report_name = "GET_LEDGER_DETAIL_VIEW_DATA"
    cursor_field = "Date"
    transformer: TypeTransformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization | TransformConfig.CustomSchemaNormalization)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.transformer.registerCustomTransform(self.get_transform_function())

    @staticmethod
    def get_transform_function():
        def transform_function(original_value: str, field_schema: Dict[str, Any]) -> str:
            if original_value and field_schema.get("format") == "date":
                date_format = "MM/YYYY" if len(original_value) <= 7 else "MM/DD/YYYY"
                try:
                    transformed_value = pendulum.from_format(original_value, date_format).to_date_string()
                    return transformed_value
                except ValueError:
                    pass
            return original_value

        return transform_function


class LedgerSummaryViewReport(LedgerDetailedViewReports):
    report_name = "GET_LEDGER_SUMMARY_VIEW_DATA"


class VendorFulfillment(IncrementalAmazonSPStream, ABC):
    primary_key = "purchaseOrderNumber"
    next_page_token_field = "nextToken"
    page_size_field = "limit"

    @property
    @abstractmethod
    def records_path(self) -> str:
        pass

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        stream_data = response.json()
        next_page_token = stream_data.get(self.data_field, {}).get("pagination", {}).get(self.next_page_token_field)
        if next_page_token:
            return {self.next_page_token_field: next_page_token}

    def stream_slices(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        start_date = pendulum.parse(self._replication_start_date)
        end_date = pendulum.parse(self._replication_end_date) if self._replication_end_date else pendulum.now("utc")

        stream_state = stream_state or {}
        if state_value := stream_state.get(self.cursor_field):
            start_date = max(start_date, pendulum.parse(state_value))

        start_date = min(start_date, end_date)
        while start_date < end_date:
            end_date_slice = start_date.add(days=7)
            yield {
                self.replication_start_date_field: start_date.strftime(DATE_TIME_FORMAT),
                self.replication_end_date_field: min(end_date_slice, end_date).strftime(DATE_TIME_FORMAT),
            }
            start_date = end_date_slice

    def request_params(
        self,
        stream_state: Optional[Mapping[str, Any]],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        stream_slice = stream_slice or {}
        if next_page_token:
            stream_slice.update(next_page_token)

        return stream_slice

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping]:
        params = self.request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        for record in response.json().get(self.data_field, {}).get(self.records_path, []):
            record[self.replication_end_date_field] = params.get(self.replication_end_date_field)
            yield record


class VendorDirectFulfillmentShipping(VendorFulfillment):
    """
    API docs: https://developer-docs.amazon.com/sp-api/docs/vendor-direct-fulfillment-shipping-api-v1-reference
    API model: https://github.com/amzn/selling-partner-api-models/blob/main/models/vendor-direct-fulfillment-shipping-api-model/vendorDirectFulfillmentShippingV1.json

    Returns a list of shipping labels created during the time frame that you specify.
    Both createdAfter and createdBefore parameters required to select the time frame.
    The date range to search must not be more than 7 days.
    """

    name = "VendorDirectFulfillmentShipping"
    records_path = "shippingLabels"
    replication_start_date_field = "createdAfter"
    replication_end_date_field = "createdBefore"
    cursor_field = "createdBefore"

    def path(self, **kwargs: Any) -> str:
        return f"vendor/directFulfillment/shipping/{VENDORS_API_VERSION}/shippingLabels"


class VendorOrders(VendorFulfillment):
    """
    API docs:
    https://developer-docs.amazon.com/sp-api/docs/vendor-orders-api-v1-reference#get-vendorordersv1purchaseorders

    API model:
    https://github.com/amzn/selling-partner-api-models/blob/main/models/vendor-orders-api-model/vendorOrders.json
    """

    name = "VendorOrders"
    records_path = "orders"
    replication_start_date_field = "changedAfter"
    replication_end_date_field = "changedBefore"
    cursor_field = "changedBefore"

    def path(self, **kwargs: Any) -> str:
        return f"vendor/orders/{VENDOR_ORDERS_API_VERSION}/purchaseOrders"


class FinanceStream(IncrementalAmazonSPStream, ABC):
    next_page_token_field = "NextToken"
    page_size_field = "MaxResultsPerPage"
    page_size = 50 #Testing fewer records to avoid TTL error for next_token: https://developer-docs.amazon.com/sp-api/docs/fba-inventory-api-v1-use-case-guide
    default_backoff_time = 60
    primary_key = None

    @property
    @abstractmethod
    def replication_start_date_field(self) -> str:
        pass

    @property
    @abstractmethod
    def replication_end_date_field(self) -> str:
        pass

    def request_params(
        self, stream_state: Mapping[str, Any], next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        if next_page_token:
            return dict(next_page_token)

        # for finance APIs, end date-time must be no later than two minutes before the request was submitted
        end_date = pendulum.now("utc").subtract(minutes=5).strftime(DATE_TIME_FORMAT)
        if self._replication_end_date:
            end_date = self._replication_end_date

        # start date and end date should not be more than 180 days apart.
        start_date = max(pendulum.parse(self._replication_start_date), pendulum.parse(end_date).subtract(days=180)).strftime(
            DATE_TIME_FORMAT
        )

        stream_state = stream_state or {}
        if stream_state_value := stream_state.get(self.cursor_field):
            start_date = max(stream_state_value, start_date)

        # logging to make sure user knows taken start date
        logger.info("start date used: %s", start_date)

        params = {
            self.replication_start_date_field: start_date,
            self.replication_end_date_field: end_date,
            self.page_size_field: self.page_size,
        }
        return params

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        stream_data = response.json()
        next_page_token = stream_data.get("payload").get(self.next_page_token_field)
        if next_page_token:
            return {self.next_page_token_field: next_page_token}

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        rate_limit = response.headers.get("x-amzn-RateLimit-Limit", 0)
        if rate_limit:
            return 1 / float(rate_limit)
        else:
            return self.default_backoff_time


class ListFinancialEventGroups(FinanceStream):
    """
    API docs: https://developer-docs.amazon.com/sp-api/docs/finances-api-reference#get-financesv0financialeventgroups
    API model: https://github.com/amzn/selling-partner-api-models/blob/main/models/finances-api-model/financesV0.json
    """

    name = "ListFinancialEventGroups"
    primary_key = "FinancialEventGroupId"
    replication_start_date_field = "FinancialEventGroupStartedAfter"
    replication_end_date_field = "FinancialEventGroupStartedBefore"
    cursor_field = "FinancialEventGroupStart"

    def path(self, **kwargs) -> str:
        return f"finances/{FINANCES_API_VERSION}/financialEventGroups"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        **kwargs: Any,
    ) -> Iterable[Mapping]:
        yield from response.json().get(self.data_field, {}).get("FinancialEventGroupList", [])


class ListFinancialEvents(FinanceStream):
    """
    API docs: https://developer-docs.amazon.com/sp-api/docs/finances-api-reference#get-financesv0financialevents
    API model: https://github.com/amzn/selling-partner-api-models/blob/main/models/finances-api-model/financesV0.json
    """

    name = "ListFinancialEvents"
    replication_start_date_field = "PostedAfter"
    replication_end_date_field = "PostedBefore"
    cursor_field = "PostedBefore"

    def path(self, **kwargs) -> str:
        return f"finances/{FINANCES_API_VERSION}/financialEvents"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        **kwargs: Any,
    ) -> Iterable[Mapping]:
        params = self.request_params(stream_state)
        events = response.json().get(self.data_field, {}).get("FinancialEvents", {})
        events[self.replication_end_date_field] = params.get(self.replication_end_date_field)
        yield from [events]


class FbaCustomerReturnsReports(IncrementalReportsAmazonSPStream):
    report_name = "GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA"


class FlatFileSettlementV2Reports(IncrementalReportsAmazonSPStream):
    report_name = "GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE"
    transformer: TypeTransformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization | TransformConfig.CustomSchemaNormalization)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.transformer.registerCustomTransform(self.get_transform_function())

    @staticmethod
    def get_transform_function():
        def transform_function(original_value: Any, field_schema: Dict[str, Any]) -> Any:
            if original_value == "" and field_schema.get("format") == "date-time":
                return None
            return original_value

        return transform_function

    def _create_report(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Mapping[str, Any]:
        # For backwards
        return {"reportId": stream_slice.get("report_id")}

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        From https://developer-docs.amazon.com/sp-api/docs/report-type-values
        documentation:
        ```Settlement reports cannot be requested or scheduled.
            They are automatically scheduled by Amazon.
            You can search for these reports using the getReports operation.
        ```
        """
        strict_start_date = pendulum.now("utc").subtract(days=90)
        utc_now = pendulum.now("utc").date().to_date_string()

        create_date = max(pendulum.parse(self._replication_start_date), strict_start_date)
        end_date = pendulum.parse(self._replication_end_date or utc_now)

        stream_state = stream_state or {}
        if cursor_value := stream_state.get(self.cursor_field):
            create_date = pendulum.parse(min(cursor_value, utc_now))

        if end_date < strict_start_date:
            end_date = pendulum.now("utc")

        params = {
            "reportTypes": self.name,
            "pageSize": 100,
            "createdSince": create_date.strftime(DATE_TIME_FORMAT),
            "createdUntil": end_date.strftime(DATE_TIME_FORMAT),
        }
        unique_records = list()
        complete = False

        while not complete:
            request_headers = self.request_headers()
            get_reports = self._create_prepared_request(
                path=f"{self.path_prefix}/reports",
                headers=dict(request_headers, **self.authenticator.get_auth_header()),
                params=params,
            )
            report_response = self._send_request(get_reports, {})
            response = report_response.json()
            data = response.get("reports", list())
            records = [e.get("reportId") for e in data if e and e.get("reportId") not in unique_records]
            unique_records += records
            reports = [{"report_id": report_id} for report_id in records]

            yield from reports

            next_value = response.get("nextToken", None)
            params = {"nextToken": next_value}
            if not next_value:
                complete = True


class FbaReimbursementsReports(IncrementalReportsAmazonSPStream):
    """
    Field definitions: https://sellercentral.amazon.com/help/hub/reference/G200732720
    """

    report_name = "GET_FBA_REIMBURSEMENTS_DATA"
