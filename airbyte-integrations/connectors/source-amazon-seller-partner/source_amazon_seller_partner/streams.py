#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import csv
import gzip
import json as json_lib
import time
from abc import ABC, abstractmethod
from io import StringIO
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Union

import dateparser
import pendulum
import requests
import xmltodict
from airbyte_cdk.entrypoint import logger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException
from airbyte_cdk.sources.streams.http.rate_limiting import default_backoff_handler
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from airbyte_cdk.utils.traced_exception import AirbyteTracedException

REPORTS_API_VERSION = "2021-06-30"
ORDERS_API_VERSION = "v0"
VENDORS_API_VERSION = "v1"
FINANCES_API_VERSION = "v0"

DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
DATE_FORMAT = "%Y-%m-%d"


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


class IncrementalAmazonSPStream(AmazonSPStream, ABC):
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
        self, response: requests.Response, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, **kwargs
    ) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        yield from response.json().get(self.data_field, [])

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        latest_benchmark = latest_record[self.cursor_field]
        if current_stream_state.get(self.cursor_field):
            return {self.cursor_field: max(latest_benchmark, current_stream_state[self.cursor_field])}
        return {self.cursor_field: latest_benchmark}


class ReportsAmazonSPStream(HttpStream, ABC):
    max_wait_seconds = 3600
    """
    API docs: https://github.com/amzn/selling-partner-api-docs/blob/main/references/reports-api/reports_2020-09-04.md
    API model: https://github.com/amzn/selling-partner-api-models/blob/main/models/reports-api-model/reports_2020-09-04.json

    Report streams are intended to work as following:
        - create a new report;
        - retrieve the report;
        - retry the retrieval if the report is still not fully processed;
        - retrieve the report document (if report processing status is `DONE`);
        - decrypt the report document (if report processing status is `DONE`);
        - yield the report document (if report processing status is `DONE`)
    """

    replication_start_date_limit_in_days = 90

    primary_key = None
    path_prefix = f"reports/{REPORTS_API_VERSION}"
    sleep_seconds = 30
    data_field = "payload"
    result_key = None
    availability_sla_days = (
        1  # see data availability sla at https://developer-docs.amazon.com/sp-api/docs/report-type-values#vendor-retail-analytics-reports
    )

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
        self.period_in_days = max(period_in_days, self.replication_start_date_limit_in_days)  # ensure old configs work as well
        self._report_options = report_options
        self._http_method = "GET"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    @property
    def http_method(self) -> str:
        return self._http_method

    @http_method.setter
    def http_method(self, value: str):
        self._http_method = value

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
            data=json_lib.dumps(report_data),
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

    @default_backoff_handler(factor=5, max_tries=5)
    def download_and_decompress_report_document(self, payload: dict) -> str:
        """
        Unpacks a report document
        """
        report = requests.get(payload.get("url"))
        report.raise_for_status()
        if "compressionAlgorithm" in payload:
            return gzip.decompress(report.content).decode("iso-8859-1")
        return report.content.decode("iso-8859-1")

    def parse_response(
        self, response: requests.Response, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, **kwargs
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

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """
        Create and retrieve the report.
        Decrypt and parse the report is its fully proceed, then yield the report document records.
        """
        report_payload = {}
        stream_slice = stream_slice or {}
        is_processed = False
        start_time = pendulum.now("utc")
        seconds_waited = 0
        try:
            report_id = self._create_report(sync_mode, cursor_field, stream_slice, stream_state)["reportId"]
        except DefaultBackoffException as e:
            logger.warning(f"The report for stream '{self.name}' was cancelled due to several failed retry attempts. {e}")
            return []

        # create and retrieve the report
        while not is_processed and seconds_waited < self.max_wait_seconds:
            report_payload = self._retrieve_report(report_id=report_id)
            seconds_waited = (pendulum.now("utc") - start_time).seconds
            is_processed = report_payload.get("processingStatus") not in ["IN_QUEUE", "IN_PROGRESS"]
            time.sleep(self.sleep_seconds)

        is_done = report_payload.get("processingStatus") == "DONE"
        is_cancelled = report_payload.get("processingStatus") == "CANCELLED"
        is_fatal = report_payload.get("processingStatus") == "FATAL"
        report_end_date = pendulum.parse(report_payload.get("dataEndTime", stream_slice.get("dataEndTime")))

        if is_done:
            # retrieve and decrypt the report document
            document_id = report_payload["reportDocumentId"]
            request_headers = self.request_headers()
            request = self._create_prepared_request(
                path=self.path(document_id=document_id),
                headers=dict(request_headers, **self.authenticator.get_auth_header()),
                params=self.request_params(),
            )
            response = self._send_request(request, {})
            for record in self.parse_response(response, stream_state, stream_slice):
                if report_end_date:
                    record["dataEndTime"] = report_end_date.strftime(DATE_FORMAT)
                yield record
        elif is_fatal:
            raise AirbyteTracedException(message=f"The report for stream '{self.name}' was not created - skip reading")
        elif is_cancelled:
            logger.warning(f"The report for stream '{self.name}' was cancelled or there is no data to return")
        else:
            raise Exception(f"Unknown response for stream `{self.name}`. Response body {report_payload}")


class IncrementalReportsAmazonSPStream(ReportsAmazonSPStream):
    @property
    def cursor_field(self) -> Union[str, List[str]]:
        return "dataEndTime"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        latest_benchmark = latest_record[self.cursor_field]
        if current_stream_state.get(self.cursor_field):
            return {self.cursor_field: max(latest_benchmark, current_stream_state[self.cursor_field])}
        return {self.cursor_field: latest_benchmark}


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
    name = "GET_MERCHANT_LISTINGS_ALL_DATA"
    primary_key = "listing-id"


class NetPureProductMarginReport(IncrementalReportsAmazonSPStream):
    name = "GET_VENDOR_NET_PURE_PRODUCT_MARGIN_REPORT"


class RapidRetailAnalyticsInventoryReport(IncrementalReportsAmazonSPStream):
    name = "GET_VENDOR_REAL_TIME_INVENTORY_REPORT"


class FlatFileOrdersReports(IncrementalReportsAmazonSPStream):
    """
    Field definitions: https://sellercentral.amazon.com/gp/help/help.html?itemID=201648780
    """

    name = "GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL"
    primary_key = "amazon-order-id"
    cursor_field = "last-updated-date"


class FbaStorageFeesReports(IncrementalReportsAmazonSPStream):
    """
    Field definitions: https://sellercentral.amazon.com/help/hub/reference/G202086720
    """

    name = "GET_FBA_STORAGE_FEE_CHARGES_DATA"


class FulfilledShipmentsReports(IncrementalReportsAmazonSPStream):
    """
    Field definitions: https://sellercentral.amazon.com/gp/help/help.html?itemID=200453120
    """

    name = "GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL"

    replication_start_date_limit_in_days = 30


class FlatFileOpenListingsReports(IncrementalReportsAmazonSPStream):
    name = "GET_FLAT_FILE_OPEN_LISTINGS_DATA"


class FbaOrdersReports(IncrementalReportsAmazonSPStream):
    """
    Field definitions: https://sellercentral.amazon.com/gp/help/help.html?itemID=200989110
    """

    name = "GET_FBA_FULFILLMENT_REMOVAL_ORDER_DETAIL_DATA"
    cursor_field = "last-updated-date"


class FlatFileActionableOrderDataShipping(IncrementalReportsAmazonSPStream):
    """
    Field definitions: https://developer-docs.amazon.com/sp-api/docs/order-reports-attributes#get_flat_file_actionable_order_data_shipping
    """

    name = "GET_FLAT_FILE_ACTIONABLE_ORDER_DATA_SHIPPING"


class OrderReportDataShipping(IncrementalReportsAmazonSPStream):
    """
    Field definitions: https://developer-docs.amazon.com/sp-api/docs/order-reports-attributes#get_order_report_data_shipping
    """

    name = "GET_ORDER_REPORT_DATA_SHIPPING"

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

    name = "GET_FBA_FULFILLMENT_REMOVAL_SHIPMENT_DETAIL_DATA"


class FbaReplacementsReports(IncrementalReportsAmazonSPStream):
    """
    Field definitions: https://sellercentral.amazon.com/help/hub/reference/200453300
    """

    name = "GET_FBA_FULFILLMENT_CUSTOMER_SHIPMENT_REPLACEMENT_DATA"


class RestockInventoryReports(IncrementalReportsAmazonSPStream):
    """
    Field definitions: 	https://sellercentral.amazon.com/help/hub/reference/202105670
    """

    name = "GET_RESTOCK_INVENTORY_RECOMMENDATIONS_REPORT"


class GetXmlBrowseTreeData(IncrementalReportsAmazonSPStream):
    def parse_document(self, document):
        try:
            parsed = xmltodict.parse(
                document, dict_constructor=dict, attr_prefix="", cdata_key="text", force_list={"attribute", "id", "refinementField"}
            )
        except Exception as e:
            self.logger.warning(f"Unable to parse the report for the stream {self.name}, error: {str(e)}")
            return []

        return parsed.get("Result", {}).get("Node", [])

    name = "GET_XML_BROWSE_TREE_DATA"
    primary_key = "browseNodeId"


class FbaEstimatedFbaFeesTxtReport(IncrementalReportsAmazonSPStream):
    name = "GET_FBA_ESTIMATED_FBA_FEES_TXT_DATA"


class FbaFulfillmentCustomerShipmentPromotionReport(IncrementalReportsAmazonSPStream):
    name = "GET_FBA_FULFILLMENT_CUSTOMER_SHIPMENT_PROMOTION_DATA"


class FbaMyiUnsuppressedInventoryReport(IncrementalReportsAmazonSPStream):
    name = "GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA"


class MerchantListingsReport(MerchantReports):
    name = "GET_MERCHANT_LISTINGS_DATA"
    primary_key = "listing-id"


class MerchantListingsInactiveData(MerchantReports):
    name = "GET_MERCHANT_LISTINGS_INACTIVE_DATA"
    primary_key = "listing-id"


class StrandedInventoryUiReport(IncrementalReportsAmazonSPStream):
    name = "GET_STRANDED_INVENTORY_UI_DATA"


class XmlAllOrdersDataByOrderDataGeneral(IncrementalReportsAmazonSPStream):
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

    name = "GET_XML_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL"
    primary_key = "AmazonOrderID"
    cursor_field = "LastUpdatedDate"


class MerchantListingsReportBackCompat(MerchantReports):
    name = "GET_MERCHANT_LISTINGS_DATA_BACK_COMPAT"
    primary_key = "listing-id"


class MerchantCancelledListingsReport(IncrementalReportsAmazonSPStream):
    name = "GET_MERCHANT_CANCELLED_LISTINGS_DATA"


class MerchantListingsFypReport(IncrementalReportsAmazonSPStream):
    name = "GET_MERCHANTS_LISTINGS_FYP_REPORT"
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
    name = "GET_FBA_SNS_FORECAST_DATA"


class FbaSnsPerformanceReport(IncrementalReportsAmazonSPStream):
    name = "GET_FBA_SNS_PERFORMANCE_DATA"


class FlatFileArchivedOrdersDataByOrderDate(IncrementalReportsAmazonSPStream):
    name = "GET_FLAT_FILE_ARCHIVED_ORDERS_DATA_BY_ORDER_DATE"
    cursor_field = "last-updated-date"


class FlatFileReturnsDataByReturnDate(IncrementalReportsAmazonSPStream):
    name = "GET_FLAT_FILE_RETURNS_DATA_BY_RETURN_DATE"

    replication_start_date_limit_in_days = 60


class FbaInventoryPlaningReport(IncrementalReportsAmazonSPStream):
    name = "GET_FBA_INVENTORY_PLANNING_DATA"


class AnalyticsStream(ReportsAmazonSPStream):
    def parse_document(self, document):
        parsed = json_lib.loads(document)
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
        if options and options.get("reportPeriod") is not None:
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


class IncrementalAnalyticsStream(AnalyticsStream):

    fixed_period_in_days = 0

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        return "endDate"

    def _report_data(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Mapping[str, Any]:
        data = super()._report_data(sync_mode, cursor_field, stream_slice, stream_state)
        if stream_slice:
            data_times = {}
            if stream_slice.get("dataStartTime"):
                data_times["dataStartTime"] = stream_slice["dataStartTime"]
            if stream_slice.get("dataEndTime"):
                data_times["dataEndTime"] = stream_slice["dataEndTime"]
            data.update(data_times)

        return data

    def parse_response(
        self, response: requests.Response, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, **kwargs
    ) -> Iterable[Mapping]:

        payload = response.json()

        document = self.download_and_decompress_report_document(payload)
        document_records = self.parse_document(document)

        # Not all (partial) responses include the request date, so adding it manually here
        for record in document_records:
            if stream_slice.get("dataEndTime"):
                record["queryEndDate"] = pendulum.parse(stream_slice["dataEndTime"]).strftime("%Y-%m-%d")
            yield record

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        latest_benchmark = latest_record[self.cursor_field]
        if current_stream_state.get(self.cursor_field):
            return {self.cursor_field: max(latest_benchmark, current_stream_state[self.cursor_field])}
        return {self.cursor_field: latest_benchmark}

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
        slices = []

        while start_date < end_date:
            # If request only returns data on day level
            if self.fixed_period_in_days != 0:
                slice_range = self.fixed_period_in_days
            else:
                slice_range = self.period_in_days

            end_date_slice = start_date.add(days=slice_range)
            slices.append(
                {
                    "dataStartTime": start_date.strftime(DATE_TIME_FORMAT),
                    "dataEndTime": min(end_date_slice.subtract(seconds=1), end_date).strftime(DATE_TIME_FORMAT),
                }
            )
            start_date = end_date_slice

        return slices


class BrandAnalyticsMarketBasketReports(IncrementalAnalyticsStream):
    name = "GET_BRAND_ANALYTICS_MARKET_BASKET_REPORT"
    result_key = "dataByAsin"


class BrandAnalyticsSearchTermsReports(IncrementalAnalyticsStream):
    """
    Field definitions: https://sellercentral.amazon.co.uk/help/hub/reference/G5NXWNY8HUD3VDCW
    """

    name = "GET_BRAND_ANALYTICS_SEARCH_TERMS_REPORT"
    result_key = "dataByDepartmentAndSearchTerm"
    cursor_field = "queryEndDate"


class BrandAnalyticsRepeatPurchaseReports(IncrementalAnalyticsStream):
    name = "GET_BRAND_ANALYTICS_REPEAT_PURCHASE_REPORT"
    result_key = "dataByAsin"


class BrandAnalyticsAlternatePurchaseReports(IncrementalAnalyticsStream):
    name = "GET_BRAND_ANALYTICS_ALTERNATE_PURCHASE_REPORT"
    result_key = "dataByAsin"


class BrandAnalyticsItemComparisonReports(IncrementalAnalyticsStream):
    name = "GET_BRAND_ANALYTICS_ITEM_COMPARISON_REPORT"
    result_key = "dataByAsin"


class VendorInventoryReports(IncrementalAnalyticsStream):
    """
    Field definitions: https://developer-docs.amazon.com/sp-api/docs/report-type-values#vendor-retail-analytics-reports
    """

    name = "GET_VENDOR_INVENTORY_REPORT"
    result_key = "inventoryByAsin"
    availability_sla_days = 3


class VendorTrafficReport(IncrementalAnalyticsStream):
    name = "GET_VENDOR_TRAFFIC_REPORT"
    result_key = "trafficByAsin"


class SellerAnalyticsSalesAndTrafficReports(IncrementalAnalyticsStream):
    """
    Field definitions: https://developer-docs.amazon.com/sp-api/docs/report-type-values#seller-retail-analytics-reports
    """

    name = "GET_SALES_AND_TRAFFIC_REPORT"
    result_key = "salesAndTrafficByAsin"
    cursor_field = "queryEndDate"
    fixed_period_in_days = 1


class VendorSalesReports(IncrementalAnalyticsStream):
    name = "GET_VENDOR_SALES_REPORT"
    result_key = "salesByAsin"
    availability_sla_days = 4  # Data is only available after 4 days


class SellerFeedbackReports(IncrementalReportsAmazonSPStream):
    """
    Field definitions: https://sellercentral.amazon.com/help/hub/reference/G202125660
    """

    # The list of MarketplaceIds can be found here https://docs.developer.amazonservices.com/en_UK/dev_guide/DG_Endpoints.html
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

    name = "GET_SELLER_FEEDBACK_DATA"
    cursor_field = "date"
    transformer: TypeTransformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization | TransformConfig.CustomSchemaNormalization)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.transformer.registerCustomTransform(self.get_transform_function())

    def get_transform_function(self):
        def transform_function(original_value: Any, field_schema: Dict[str, Any]) -> Any:
            if original_value and "format" in field_schema and field_schema["format"] == "date":
                date_format = self.MARKETPLACE_DATE_FORMAT_MAP.get(self.marketplace_id)
                if not date_format:
                    raise KeyError(f"Date format not found for Markeplace ID: {self.marketplace_id}")
                transformed_value = pendulum.from_format(original_value, date_format).to_date_string()
                return transformed_value

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
    Report has a long-running issue (fails when requested frequently): https://github.com/amzn/selling-partner-api-docs/issues/2231
    """

    name = "GET_AFN_INVENTORY_DATA"


class FbaAfnInventoryByCountryReports(IncrementalReportsAmazonSPStream):
    """
    Field definitions: https://developer-docs.amazon.com/sp-api/docs/report-type-values#inventory-reports
    Report has a long-running issue (fails when requested frequently): https://github.com/amzn/selling-partner-api-docs/issues/2231
    """

    name = "GET_AFN_INVENTORY_DATA_BY_COUNTRY"


class FlatFileOrdersReportsByLastUpdate(IncrementalReportsAmazonSPStream):
    """
    Field definitions: https://sellercentral.amazon.com/gp/help/help.html?itemID=201648780
    """

    name = "GET_FLAT_FILE_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL"
    primary_key = "amazon-order-id"
    cursor_field = "last-updated-date"
    replication_start_date_limit_in_days = 30


class Orders(IncrementalAmazonSPStream):
    """
    API docs: https://github.com/amzn/selling-partner-api-docs/blob/main/references/orders-api/ordersV0.md
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
        self, response: requests.Response, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, **kwargs
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
        self, response: requests.Response, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, **kwargs
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

    name = "GET_LEDGER_DETAIL_VIEW_DATA"
    cursor_field = "Date"
    transformer: TypeTransformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization | TransformConfig.CustomSchemaNormalization)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.transformer.registerCustomTransform(self.get_transform_function())

    @staticmethod
    def get_transform_function():
        def transform_function(original_value: Any, field_schema: Dict[str, Any]) -> Any:
            if original_value and field_schema.get("format") == "date":
                try:
                    transformed_value = pendulum.from_format(original_value, "MM/DD/YYYY").to_date_string()
                    return transformed_value
                except ValueError:
                    pass
            return original_value

        return transform_function


class LedgerSummaryViewReport(LedgerDetailedViewReports):
    name = "GET_LEDGER_SUMMARY_VIEW_DATA"


class VendorDirectFulfillmentShipping(IncrementalAmazonSPStream):
    """
    API docs: https://github.com/amzn/selling-partner-api-docs/blob/main/references/vendor-direct-fulfillment-shipping-api/vendorDirectFulfillmentShippingV1.md
    API model: https://github.com/amzn/selling-partner-api-models/blob/main/models/vendor-direct-fulfillment-shipping-api-model/vendorDirectFulfillmentShippingV1.json

    Returns a list of shipping labels created during the time frame that you specify.
    Both createdAfter and createdBefore parameters required to select the time frame.
    The date range to search must not be more than 7 days.
    """

    name = "VendorDirectFulfillmentShipping"
    primary_key = "purchaseOrderNumber"
    replication_start_date_field = "createdAfter"
    replication_end_date_field = "createdBefore"
    next_page_token_field = "nextToken"
    page_size_field = "limit"
    time_format = "%Y-%m-%dT%H:%M:%SZ"
    cursor_field = "createdBefore"

    def path(self, **kwargs) -> str:
        return f"vendor/directFulfillment/shipping/{VENDORS_API_VERSION}/shippingLabels"

    def request_params(
        self, stream_state: Mapping[str, Any], next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        if next_page_token:
            return dict(next_page_token)

        end_date = pendulum.now("utc").strftime(self.time_format)
        if self._replication_end_date:
            end_date = self._replication_end_date
        # The date range to search must not be more than 7 days - see docs
        # https://developer-docs.amazon.com/sp-api/docs/vendor-direct-fulfillment-shipping-api-v1-reference
        start_date = max(pendulum.parse(self._replication_start_date), pendulum.parse(end_date).subtract(days=7, hours=1)).strftime(
            self.time_format
        )
        if stream_state_value := stream_state.get(self.cursor_field):
            start_date = max(stream_state_value, start_date)
        return {self.replication_start_date_field: start_date, self.replication_end_date_field: end_date}

    def parse_response(
        self, response: requests.Response, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, **kwargs
    ) -> Iterable[Mapping]:
        params = self.request_params(stream_state)
        for record in response.json().get(self.data_field, {}).get("shippingLabels", []):
            record[self.replication_end_date_field] = params.get(self.replication_end_date_field)
            yield record


class FinanceStream(IncrementalAmazonSPStream, ABC):
    next_page_token_field = "NextToken"
    page_size_field = "MaxResultsPerPage"
    page_size = 100
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
    API docs: https://github.com/amzn/selling-partner-api-docs/blob/main/references/finances-api/financesV0.md#listfinancialeventgroups
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
        self, response: requests.Response, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, **kwargs
    ) -> Iterable[Mapping]:
        yield from response.json().get(self.data_field, {}).get("FinancialEventGroupList", [])


class ListFinancialEvents(FinanceStream):
    """
    API docs: https://github.com/amzn/selling-partner-api-docs/blob/main/references/finances-api/financesV0.md#listfinancialevents
    API model: https://github.com/amzn/selling-partner-api-models/blob/main/models/finances-api-model/financesV0.json
    """

    name = "ListFinancialEvents"
    replication_start_date_field = "PostedAfter"
    replication_end_date_field = "PostedBefore"
    cursor_field = "PostedBefore"

    def path(self, **kwargs) -> str:
        return f"finances/{FINANCES_API_VERSION}/financialEvents"

    def parse_response(
        self, response: requests.Response, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, **kwargs
    ) -> Iterable[Mapping]:
        params = self.request_params(stream_state)
        events = response.json().get(self.data_field, {}).get("FinancialEvents", {})
        events[self.replication_end_date_field] = params.get(self.replication_end_date_field)
        yield from [events]


class FbaCustomerReturnsReports(IncrementalReportsAmazonSPStream):

    name = "GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA"


class FlatFileSettlementV2Reports(IncrementalReportsAmazonSPStream):

    name = "GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE"
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

    name = "GET_FBA_REIMBURSEMENTS_DATA"
