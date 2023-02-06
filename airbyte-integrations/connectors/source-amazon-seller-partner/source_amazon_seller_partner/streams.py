#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import csv
import json as json_lib
import time
import zlib
from abc import ABC, abstractmethod
from io import StringIO
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Union
from urllib.parse import urljoin

import pendulum
import requests
import xmltodict
from airbyte_cdk.entrypoint import logger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException, RequestBodyException
from airbyte_cdk.sources.streams.http.http import BODY_REQUEST_METHODS
from airbyte_cdk.sources.streams.http.rate_limiting import default_backoff_handler
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from source_amazon_seller_partner.auth import AWSSignature

REPORTS_API_VERSION = "2021-06-30"  # 2020-09-04
ORDERS_API_VERSION = "v0"
VENDORS_API_VERSION = "v1"
FINANCES_API_VERSION = "v0"

DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


class AmazonSPStream(HttpStream, ABC):
    data_field = "payload"

    def __init__(
        self,
        url_base: str,
        aws_signature: AWSSignature,
        replication_start_date: str,
        marketplace_id: str,
        period_in_days: Optional[int],
        report_options: Optional[str],
        max_wait_seconds: Optional[int],
        replication_end_date: Optional[str],
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self._url_base = url_base.rstrip("/") + "/"
        self._replication_start_date = replication_start_date
        self._replication_end_date = replication_end_date
        self.marketplace_id = marketplace_id
        self._session.auth = aws_signature

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

        params = {self.replication_start_date_field: self._replication_start_date, self.page_size_field: self.page_size}

        if self._replication_start_date and self.cursor_field:
            start_date = max(stream_state.get(self.cursor_field, self._replication_start_date), self._replication_start_date)
            params.update({self.replication_start_date_field: start_date})

        if self._replication_end_date:
            params[self.replication_end_date_field] = self._replication_end_date

        return params

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        stream_data = response.json()
        next_page_token = stream_data.get("payload").get(self.next_page_token_field)
        if next_page_token:
            return {self.next_page_token_field: next_page_token}

    def parse_response(
        self, response: requests.Response, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, **kwargss
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


class ReportsAmazonSPStream(Stream, ABC):
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
        aws_signature: AWSSignature,
        replication_start_date: str,
        marketplace_id: str,
        period_in_days: Optional[int],
        report_options: Optional[str],
        max_wait_seconds: Optional[int],
        replication_end_date: Optional[str],
        authenticator: HttpAuthenticator = None,
    ):
        self._authenticator = authenticator
        self._session = requests.Session()
        self._url_base = url_base.rstrip("/") + "/"
        self._session.auth = aws_signature
        self._replication_start_date = replication_start_date
        self._replication_end_date = replication_end_date
        self.marketplace_id = marketplace_id
        self.period_in_days = max(period_in_days, self.replication_start_date_limit_in_days)  # ensure old configs work as well
        self._report_options = report_options or "{}"
        self.max_wait_seconds = max_wait_seconds

    @property
    def url_base(self) -> str:
        return self._url_base

    @property
    def authenticator(self) -> HttpAuthenticator:
        return self._authenticator

    def request_params(self) -> MutableMapping[str, Any]:
        return {"MarketplaceIds": self.marketplace_id}

    def request_headers(self) -> Mapping[str, Any]:
        return {"content-type": "application/json"}

    def path(self, document_id: str) -> str:
        return f"{self.path_prefix}/documents/{document_id}"

    def should_retry(self, response: requests.Response) -> bool:
        return response.status_code == 429 or 500 <= response.status_code < 600

    @default_backoff_handler(max_tries=5, factor=5)
    def _send_request(self, request: requests.PreparedRequest) -> requests.Response:
        response: requests.Response = self._session.send(request)
        if self.should_retry(response):
            raise DefaultBackoffException(request=request, response=response)
        else:
            response.raise_for_status()
        return response

    def _create_prepared_request(
        self, path: str, http_method: str = "GET", headers: Mapping = None, params: Mapping = None, json: Any = None, data: Any = None
    ) -> requests.PreparedRequest:
        """
        Override to make http_method configurable per method call
        """
        args = {"method": http_method, "url": urljoin(self.url_base, path), "headers": headers, "params": params}
        if http_method.upper() in BODY_REQUEST_METHODS:
            if json and data:
                raise RequestBodyException(
                    "At the same time only one of the 'request_body_data' and 'request_body_json' functions can return data"
                )
            elif json:
                args["json"] = json
            elif data:
                args["data"] = data

        return self._session.prepare_request(requests.Request(**args))

    def _report_data(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Mapping[str, Any]:
        return {"reportType": self.name, "marketplaceIds": [self.marketplace_id], **stream_slice}

    def _create_report(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Mapping[str, Any]:
        request_headers = self.request_headers()
        report_data = self._report_data(sync_mode, cursor_field, stream_slice, stream_state)
        create_report_request = self._create_prepared_request(
            http_method="POST",
            path=f"{self.path_prefix}/reports",
            headers=dict(request_headers, **self.authenticator.get_auth_header()),
            data=json_lib.dumps(report_data),
        )
        report_response = self._send_request(create_report_request)
        return report_response.json()

    def _retrieve_report(self, report_id: str) -> Mapping[str, Any]:
        request_headers = self.request_headers()
        retrieve_report_request = self._create_prepared_request(
            path=f"{self.path_prefix}/reports/{report_id}",
            headers=dict(request_headers, **self.authenticator.get_auth_header()),
        )
        retrieve_report_response = self._send_request(retrieve_report_request)
        report_payload = retrieve_report_response.json()

        return report_payload

    def decompress_report_document(self, url, payload):
        """
        Unpacks a report document
        """
        report = requests.get(url).content
        if "compressionAlgorithm" in payload:
            return zlib.decompress(bytearray(report), 15 + 32).decode("iso-8859-1")
        return report.decode("iso-8859-1")

    def parse_response(
        self, response: requests.Response, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, **kwargs
    ) -> Iterable[Mapping]:
        payload = response.json()

        document = self.decompress_report_document(payload.get("url"), payload)

        document_records = self.parse_document(document)
        yield from document_records

    def parse_document(self, document):
        return csv.DictReader(StringIO(document), delimiter="\t")

    def report_options(self) -> Mapping[str, Any]:
        if self._report_options is not None:
            return json_lib.loads(self._report_options).get(self.name)
        else:
            return {}

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        start_date = max(pendulum.parse(self._replication_start_date), pendulum.now("utc").subtract(days=90))
        end_date = pendulum.now()
        if self._replication_end_date and sync_mode == SyncMode.full_refresh:
            # if replication_start_date is older than 90 days(from current date), we are overriding the value above.
            # when replication_end_date is present, we should use the user provided replication_start_date.
            # user may provide a date range which is older than 90 days.
            end_date = min(end_date, pendulum.parse(self._replication_end_date))
            start_date = pendulum.parse(self._replication_start_date)

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
        is_processed = False
        is_done = False
        start_time = pendulum.now("utc")
        seconds_waited = 0
        report_id = self._create_report(sync_mode, cursor_field, stream_slice, stream_state)["reportId"]

        # create and retrieve the report
        while not is_processed and seconds_waited < self.max_wait_seconds:
            report_payload = self._retrieve_report(report_id=report_id)
            seconds_waited = (pendulum.now("utc") - start_time).seconds
            is_processed = report_payload.get("processingStatus") not in ["IN_QUEUE", "IN_PROGRESS"]
            is_done = report_payload.get("processingStatus") == "DONE"
            is_cancelled = report_payload.get("processingStatus") == "CANCELLED"
            is_fatal = report_payload.get("processingStatus") == "FATAL"
            time.sleep(self.sleep_seconds)

        if is_done:
            # retrieve and decrypt the report document
            document_id = report_payload["reportDocumentId"]
            request_headers = self.request_headers()
            request = self._create_prepared_request(
                path=self.path(document_id=document_id),
                headers=dict(request_headers, **self.authenticator.get_auth_header()),
                params=self.request_params(),
            )
            response = self._send_request(request)
            yield from self.parse_response(response, stream_state, stream_slice)
        elif is_fatal:
            raise Exception(f"The report for stream '{self.name}' was aborted due to a fatal error")
        elif is_cancelled:
            logger.warn(f"The report for stream '{self.name}' was cancelled or there is no data to return")
        else:
            raise Exception(f"Unknown response for stream `{self.name}`. Response body {report_payload}")


class MerchantListingsReports(ReportsAmazonSPStream):
    name = "GET_MERCHANT_LISTINGS_ALL_DATA"


class FlatFileOrdersReports(ReportsAmazonSPStream):
    """
    Field definitions: https://sellercentral.amazon.com/gp/help/help.html?itemID=201648780
    """

    name = "GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL"


class FbaAfnInventoryReports(ReportsAmazonSPStream):
    """
    Field definitions: https://developer-docs.amazon.com/sp-api/docs/report-type-values#inventory-reports
    Report does seem to have an long-running issue (sometimes failing without a reason): https://github.com/amzn/selling-partner-api-docs/issues/2231
    """

    name = "GET_AFN_INVENTORY_DATA"


class FbaAfnInventoryByCountryReports(ReportsAmazonSPStream):
    """
    Field definitions: https://developer-docs.amazon.com/sp-api/docs/report-type-values#inventory-reports
    Report does seem to have an long-running issue (sometimes failing without a reason): https://github.com/amzn/selling-partner-api-docs/issues/2231
    """

    name = "GET_AFN_INVENTORY_DATA_BY_COUNTRY"


class FbaStorageFeesReports(ReportsAmazonSPStream):
    """
    Field definitions: https://sellercentral.amazon.com/help/hub/reference/G202086720
    """

    name = "GET_FBA_STORAGE_FEE_CHARGES_DATA"


class FulfilledShipmentsReports(ReportsAmazonSPStream):
    """
    Field definitions: https://sellercentral.amazon.com/gp/help/help.html?itemID=200453120
    """

    name = "GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL"

    replication_start_date_limit_in_days = 30


class FlatFileOpenListingsReports(ReportsAmazonSPStream):
    name = "GET_FLAT_FILE_OPEN_LISTINGS_DATA"


class FbaOrdersReports(ReportsAmazonSPStream):
    """
    Field definitions: https://sellercentral.amazon.com/gp/help/help.html?itemID=200989110
    """

    name = "GET_FBA_FULFILLMENT_REMOVAL_ORDER_DETAIL_DATA"


class FbaShipmentsReports(ReportsAmazonSPStream):
    """
    Field definitions: https://sellercentral.amazon.com/gp/help/help.html?itemID=200989100
    """

    name = "GET_FBA_FULFILLMENT_REMOVAL_SHIPMENT_DETAIL_DATA"


class FbaReplacementsReports(ReportsAmazonSPStream):
    """
    Field definitions: https://sellercentral.amazon.com/help/hub/reference/200453300
    """

    name = "GET_FBA_FULFILLMENT_CUSTOMER_SHIPMENT_REPLACEMENT_DATA"


class RestockInventoryReports(ReportsAmazonSPStream):
    """
    Field definitions: 	https://sellercentral.amazon.com/help/hub/reference/202105670
    """

    name = "GET_RESTOCK_INVENTORY_RECOMMENDATIONS_REPORT"


class GetXmlBrowseTreeData(ReportsAmazonSPStream):
    def parse_document(self, document):
        parsed = xmltodict.parse(
            document, dict_constructor=dict, attr_prefix="", cdata_key="text", force_list={"attribute", "id", "refinementField"}
        )
        return parsed.get("Result", {}).get("Node", [])

    name = "GET_XML_BROWSE_TREE_DATA"


class FbaEstimatedFbaFeesTxtReport(ReportsAmazonSPStream):
    name = "GET_FBA_ESTIMATED_FBA_FEES_TXT_DATA"


class FbaFulfillmentCurrentInventoryReport(ReportsAmazonSPStream):
    name = "GET_FBA_FULFILLMENT_CURRENT_INVENTORY_DATA"


class FbaFulfillmentCustomerShipmentPromotionReport(ReportsAmazonSPStream):
    name = "GET_FBA_FULFILLMENT_CUSTOMER_SHIPMENT_PROMOTION_DATA"


class FbaFulfillmentInventoryAdjustReport(ReportsAmazonSPStream):
    name = "GET_FBA_FULFILLMENT_INVENTORY_ADJUSTMENTS_DATA"


class FbaFulfillmentInventoryReceiptsReport(ReportsAmazonSPStream):
    name = "GET_FBA_FULFILLMENT_INVENTORY_RECEIPTS_DATA"


class FbaFulfillmentInventorySummaryReport(ReportsAmazonSPStream):
    name = "GET_FBA_FULFILLMENT_INVENTORY_SUMMARY_DATA"


class FbaMyiUnsuppressedInventoryReport(ReportsAmazonSPStream):
    name = "GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA"


class MerchantListingsReport(ReportsAmazonSPStream):
    name = "GET_MERCHANT_LISTINGS_DATA"


class MerchantListingsInactiveData(ReportsAmazonSPStream):
    name = "GET_MERCHANT_LISTINGS_INACTIVE_DATA"


class StrandedInventoryUiReport(ReportsAmazonSPStream):
    name = "GET_STRANDED_INVENTORY_UI_DATA"


class XmlAllOrdersDataByOrderDataGeneral(ReportsAmazonSPStream):
    def parse_document(self, document):
        parsed = xmltodict.parse(document, attr_prefix="", cdata_key="value", force_list={"Message", "OrderItem"})
        orders = parsed.get("AmazonEnvelope", {}).get("Message", [])
        result = []
        if isinstance(orders, list):
            for order in orders:
                result.append(order.get("Order", {}))

        return result

    name = "GET_XML_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL"


class MerchantListingsReportBackCompat(ReportsAmazonSPStream):
    def _report_data(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Mapping[str, Any]:
        params = super()._report_data(sync_mode, cursor_field, stream_slice, stream_state)
        options = self.report_options()
        if options is not None:
            params.update({"reportOptions": options})
        return params

    name = "GET_MERCHANT_LISTINGS_DATA_BACK_COMPAT"


class MerchantCancelledListingsReport(ReportsAmazonSPStream):
    def _report_data(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Mapping[str, Any]:
        params = super()._report_data(sync_mode, cursor_field, stream_slice, stream_state)
        options = self.report_options()
        if options is not None:
            params.update({"reportOptions": options})
        return params

    name = "GET_MERCHANT_CANCELLED_LISTINGS_DATA"


class FbaFulfillmentMonthlyInventoryReport(ReportsAmazonSPStream):
    name = "GET_FBA_FULFILLMENT_MONTHLY_INVENTORY_DATA"


class MerchantListingsFypReport(ReportsAmazonSPStream):
    name = "GET_MERCHANTS_LISTINGS_FYP_REPORT"


class FbaSnsForecastReport(ReportsAmazonSPStream):
    name = "GET_FBA_SNS_FORECAST_DATA"


class FbaSnsPerformanceReport(ReportsAmazonSPStream):
    name = "GET_FBA_SNS_PERFORMANCE_DATA"


class FlatFileArchivedOrdersDataByOrderDate(ReportsAmazonSPStream):
    name = "GET_FLAT_FILE_ARCHIVED_ORDERS_DATA_BY_ORDER_DATE"


class FlatFileReturnsDataByReturnDate(ReportsAmazonSPStream):
    name = "GET_FLAT_FILE_RETURNS_DATA_BY_RETURN_DATE"

    replication_start_date_limit_in_days = 60


class FbaInventoryPlaningReport(ReportsAmazonSPStream):
    name = "GET_FBA_INVENTORY_PLANNING_DATA"


class LedgerSummaryViewReport(ReportsAmazonSPStream):
    def _report_data(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Mapping[str, Any]:
        params = super()._report_data(sync_mode, cursor_field, stream_slice, stream_state)
        options = self.report_options()
        if options is not None:
            params.update({"reportOptions": options})
        return params

    name = "GET_LEDGER_SUMMARY_VIEW_DATA"


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
        if options is not None:
            data.update(self._augmented_data(self, options))
        return data

    @staticmethod
    def _augmented_data(self, report_options) -> Mapping[str, Any]:
        if report_options.get("reportPeriod") is None:
            return {"reportOptions": report_options}
        else:
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


class BrandAnalyticsMarketBasketReports(AnalyticsStream):
    name = "GET_BRAND_ANALYTICS_MARKET_BASKET_REPORT"
    result_key = "dataByAsin"


class BrandAnalyticsSearchTermsReports(AnalyticsStream):
    """
    Field definitions: https://sellercentral.amazon.co.uk/help/hub/reference/G5NXWNY8HUD3VDCW
    """

    name = "GET_BRAND_ANALYTICS_SEARCH_TERMS_REPORT"
    result_key = "dataByDepartmentAndSearchTerm"


class BrandAnalyticsRepeatPurchaseReports(AnalyticsStream):
    name = "GET_BRAND_ANALYTICS_REPEAT_PURCHASE_REPORT"
    result_key = "dataByAsin"


class BrandAnalyticsAlternatePurchaseReports(AnalyticsStream):
    name = "GET_BRAND_ANALYTICS_ALTERNATE_PURCHASE_REPORT"
    result_key = "dataByAsin"


class BrandAnalyticsItemComparisonReports(AnalyticsStream):
    name = "GET_BRAND_ANALYTICS_ITEM_COMPARISON_REPORT"
    result_key = "dataByAsin"


class VendorInventoryReports(AnalyticsStream):
    """
    Field definitions: https://developer-docs.amazon.com/sp-api/docs/report-type-values#vendor-retail-analytics-reports
    """

    name = "GET_VENDOR_INVENTORY_REPORT"
    result_key = "inventoryByAsin"
    availability_sla_days = 3


class IncrementalReportsAmazonSPStream(ReportsAmazonSPStream):
    @property
    @abstractmethod
    def cursor_field(self) -> Union[str, List[str]]:
        pass

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        latest_benchmark = latest_record[self.cursor_field]
        if current_stream_state.get(self.cursor_field):
            return {self.cursor_field: max(latest_benchmark, current_stream_state[self.cursor_field])}
        return {self.cursor_field: latest_benchmark}


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
    # but columns come in the same order
    # so we set fieldnames to our custom ones
    # and raise error if original and custom header field count does not match
    @staticmethod
    def parse_document(document):
        reader = csv.DictReader(StringIO(document), delimiter="\t", fieldnames=SellerFeedbackReports.NORMALIZED_FIELD_NAMES)
        original_fieldnames = next(reader)
        if len(original_fieldnames) != len(SellerFeedbackReports.NORMALIZED_FIELD_NAMES):
            raise ValueError("Original and normalized header field count does not match")

        return reader


class FlatFileOrdersReportsByLastUpdate(IncrementalReportsAmazonSPStream):
    """
    Field definitions: https://sellercentral.amazon.com/gp/help/help.html?itemID=201648780
    """

    name = "GET_FLAT_FILE_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL"
    cursor_field = "last-updated-date"


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

    def path(self, **kwargs) -> str:
        return f"orders/{ORDERS_API_VERSION}/orders"

    def request_params(
        self, stream_state: Mapping[str, Any], next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, next_page_token=next_page_token, **kwargs)
        params.update({"MarketplaceIds": self.marketplace_id})
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

    def get_transform_function(self):
        def transform_function(original_value: Any, field_schema: Dict[str, Any]) -> Any:
            if original_value and field_schema.get("format") == "date":
                transformed_value = pendulum.from_format(original_value, "MM/DD/YYYY").to_date_string()
                return transformed_value
            return original_value

        return transform_function


class IncrementalAnalyticsStream(AnalyticsStream):

    fixed_period_in_days = 0

    @property
    @abstractmethod
    def cursor_field(self) -> Union[str, List[str]]:
        pass

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

        document = self.decompress_report_document(
            payload.get("url"),
            payload,
        )
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
        end_date = pendulum.now().subtract(days=self.availability_sla_days)

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
    cursor_field = "endDate"
    availability_sla_days = 4  # Data is only available after 4 days


class VendorDirectFulfillmentShipping(AmazonSPStream):
    """
    API docs: https://github.com/amzn/selling-partner-api-docs/blob/main/references/vendor-direct-fulfillment-shipping-api/vendorDirectFulfillmentShippingV1.md
    API model: https://github.com/amzn/selling-partner-api-models/blob/main/models/vendor-direct-fulfillment-shipping-api-model/vendorDirectFulfillmentShippingV1.json

    Returns a list of shipping labels created during the time frame that you specify.
    Both createdAfter and createdBefore parameters required to select the time frame.
    The date range to search must not be more than 7 days.
    """

    name = "VendorDirectFulfillmentShipping"
    primary_key = None
    replication_start_date_field = "createdAfter"
    replication_end_date_field = "createdBefore"
    next_page_token_field = "nextToken"
    page_size_field = "limit"
    time_format = "%Y-%m-%dT%H:%M:%SZ"

    def path(self, **kwargs) -> str:
        return f"vendor/directFulfillment/shipping/{VENDORS_API_VERSION}/shippingLabels"

    def request_params(
        self, stream_state: Mapping[str, Any], next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, next_page_token=next_page_token, **kwargs)
        if not next_page_token:
            end_date = pendulum.now("utc").strftime(self.time_format)
            if self._replication_end_date:
                end_date = self._replication_end_date

            start_date = max(pendulum.parse(self._replication_start_date), pendulum.parse(end_date).subtract(days=7, hours=1)).strftime(
                self.time_format
            )

            params.update({self.replication_start_date_field: start_date, self.replication_end_date_field: end_date})
        return params

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        yield from response.json().get(self.data_field, {}).get("shippingLabels", [])


class FinanceStream(AmazonSPStream, ABC):
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
        end_date = pendulum.now("utc").subtract(minutes=2, seconds=10).strftime(DATE_TIME_FORMAT)
        if self._replication_end_date:
            end_date = self._replication_end_date

        # start date and end date should not be more than 180 days apart.
        start_date = max(pendulum.parse(self._replication_start_date), pendulum.parse(end_date).subtract(days=180)).strftime(
            DATE_TIME_FORMAT
        )

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
    replication_start_date_field = "FinancialEventGroupStartedAfter"
    replication_end_date_field = "FinancialEventGroupStartedBefore"

    def path(self, **kwargs) -> str:
        return f"finances/{FINANCES_API_VERSION}/financialEventGroups"

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        yield from response.json().get(self.data_field, {}).get("FinancialEventGroupList", [])


class ListFinancialEvents(FinanceStream):
    """
    API docs: https://github.com/amzn/selling-partner-api-docs/blob/main/references/finances-api/financesV0.md#listfinancialevents
    API model: https://github.com/amzn/selling-partner-api-models/blob/main/models/finances-api-model/financesV0.json
    """

    name = "ListFinancialEvents"
    replication_start_date_field = "PostedAfter"
    replication_end_date_field = "PostedBefore"

    def path(self, **kwargs) -> str:
        return f"finances/{FINANCES_API_VERSION}/financialEvents"

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        yield from [response.json().get(self.data_field, {}).get("FinancialEvents", {})]


class FbaCustomerReturnsReports(ReportsAmazonSPStream):

    name = "GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA"


class FlatFileSettlementV2Reports(ReportsAmazonSPStream):

    name = "GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE"

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
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
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

        create_date = max(pendulum.parse(self._replication_start_date), strict_start_date)
        end_date = pendulum.parse(self._replication_end_date or pendulum.now("utc").date().to_date_string())

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
                http_method="GET",
                path=f"{self.path_prefix}/reports",
                headers=dict(request_headers, **self.authenticator.get_auth_header()),
                params=params,
            )
            report_response = self._send_request(get_reports)
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
