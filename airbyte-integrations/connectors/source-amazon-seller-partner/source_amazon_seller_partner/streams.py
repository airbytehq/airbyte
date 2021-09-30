#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import base64
import csv
import json as json_lib
import time
import zlib
from abc import ABC, abstractmethod
from io import StringIO
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union

import pendulum
import requests
from airbyte_cdk.entrypoint import logger
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator, NoAuth
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException, RequestBodyException
from airbyte_cdk.sources.streams.http.http import BODY_REQUEST_METHODS
from airbyte_cdk.sources.streams.http.rate_limiting import default_backoff_handler
from Crypto.Cipher import AES
from source_amazon_seller_partner.auth import AWSSignature

REPORTS_API_VERSION = "2020-09-04"
ORDERS_API_VERSION = "v0"
VENDORS_API_VERSION = "v1"

REPORTS_MAX_WAIT_SECONDS = 50


class AmazonSPStream(HttpStream, ABC):
    data_field = "payload"

    def __init__(
        self, url_base: str, aws_signature: AWSSignature, replication_start_date: str, marketplace_ids: List[str], *args, **kwargs
    ):
        super().__init__(*args, **kwargs)

        self._url_base = url_base
        self._replication_start_date = replication_start_date
        self.marketplace_ids = marketplace_ids
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
        return params

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        stream_data = response.json()
        next_page_token = stream_data.get(self.next_page_token_field)
        if next_page_token:
            return {self.next_page_token_field: next_page_token}

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
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

    primary_key = None
    path_prefix = f"/reports/{REPORTS_API_VERSION}"
    sleep_seconds = 30
    data_field = "payload"

    def __init__(
        self,
        url_base: str,
        aws_signature: AWSSignature,
        replication_start_date: str,
        marketplace_ids: List[str],
        authenticator: HttpAuthenticator = NoAuth(),
    ):
        self._authenticator = authenticator
        self._session = requests.Session()
        self._url_base = url_base
        self._session.auth = aws_signature
        self._replication_start_date = replication_start_date
        self.marketplace_ids = marketplace_ids

    @property
    def url_base(self) -> str:
        return self._url_base

    @property
    def authenticator(self) -> HttpAuthenticator:
        return self._authenticator

    def request_params(self) -> MutableMapping[str, Any]:
        return {"MarketplaceIds": ",".join(self.marketplace_ids)}

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
        args = {"method": http_method, "url": self.url_base + path, "headers": headers, "params": params}
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

    def _create_report(self) -> Mapping[str, Any]:
        request_headers = self.request_headers()
        replication_start_date = max(pendulum.parse(self._replication_start_date), pendulum.now("utc").subtract(days=90))
        report_data = {
            "reportType": self.name,
            "marketplaceIds": self.marketplace_ids,
            "createdSince": replication_start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        create_report_request = self._create_prepared_request(
            http_method="POST",
            path=f"{self.path_prefix}/reports",
            headers=dict(request_headers, **self.authenticator.get_auth_header()),
            data=json_lib.dumps(report_data),
        )
        report_response = self._send_request(create_report_request)
        return report_response.json()[self.data_field]

    def _retrieve_report(self, report_id: str) -> Mapping[str, Any]:
        request_headers = self.request_headers()
        retrieve_report_request = self._create_prepared_request(
            path=f"{self.path_prefix}/reports/{report_id}",
            headers=dict(request_headers, **self.authenticator.get_auth_header()),
        )
        retrieve_report_response = self._send_request(retrieve_report_request)
        report_payload = retrieve_report_response.json().get(self.data_field, {})
        return report_payload

    @staticmethod
    def decrypt_aes(content, key, iv):
        key = base64.b64decode(key)
        iv = base64.b64decode(iv)
        decrypter = AES.new(key, AES.MODE_CBC, iv)
        decrypted = decrypter.decrypt(content)
        padding_bytes = decrypted[-1]
        return decrypted[:-padding_bytes]

    def decrypt_report_document(self, url, initialization_vector, key, encryption_standard, payload):
        """
        Decrypts and unpacks a report document, currently AES encryption is implemented
        """
        if encryption_standard == "AES":
            decrypted = self.decrypt_aes(requests.get(url).content, key, initialization_vector)
            if "compressionAlgorithm" in payload:
                return zlib.decompress(bytearray(decrypted), 15 + 32).decode("iso-8859-1")
            return decrypted.decode("iso-8859-1")
        raise Exception([{"message": "Only AES decryption is implemented."}])

    def parse_response(self, response: requests.Response) -> Iterable[Mapping]:
        payload = response.json().get(self.data_field, {})
        document = self.decrypt_report_document(
            payload.get("url"),
            payload.get("encryptionDetails", {}).get("initializationVector"),
            payload.get("encryptionDetails", {}).get("key"),
            payload.get("encryptionDetails", {}).get("standard"),
            payload,
        )

        document_records = csv.DictReader(StringIO(document), delimiter="\t")
        yield from document_records

    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        """
        Create and retrieve the report.
        Decrypt and parse the report is its fully proceed, then yield the report document records.
        """
        report_payload = {}
        is_processed = False
        is_done = False
        start_time = pendulum.now("utc")
        seconds_waited = 0
        report_id = self._create_report()["reportId"]

        # create and retrieve the report
        while not is_processed and seconds_waited < REPORTS_MAX_WAIT_SECONDS:
            report_payload = self._retrieve_report(report_id=report_id)
            seconds_waited = (pendulum.now("utc") - start_time).seconds
            is_processed = report_payload.get("processingStatus") not in ["IN_QUEUE", "IN_PROGRESS"]
            is_done = report_payload.get("processingStatus") == "DONE"
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
            yield from self.parse_response(response)
        else:
            logger.warn(f"There are no report document related in stream `{self.name}`. Report body {report_payload}")


class MerchantListingsReports(ReportsAmazonSPStream):
    name = "GET_MERCHANT_LISTINGS_ALL_DATA"


class FlatFileOrdersReports(ReportsAmazonSPStream):
    """
    Field definitions: https://sellercentral.amazon.com/gp/help/help.html?itemID=201648780
    """

    name = "GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL"


class FbaInventoryReports(ReportsAmazonSPStream):
    """
    Field definitions: https://sellercentral.amazon.com/gp/help/200740930
    """

    name = "GET_FBA_INVENTORY_AGED_DATA"


class FulfilledShipmentsReports(ReportsAmazonSPStream):
    """
    Field definitions: https://sellercentral.amazon.com/gp/help/help.html?itemID=200453120
    """

    name = "GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL"


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


class VendorInventoryHealthReports(ReportsAmazonSPStream):
    name = "GET_VENDOR_INVENTORY_HEALTH_AND_PLANNING_REPORT"


class Orders(IncrementalAmazonSPStream):
    """
    API docs: https://github.com/amzn/selling-partner-api-docs/blob/main/references/orders-api/ordersV0.md
    API model: https://github.com/amzn/selling-partner-api-models/blob/main/models/orders-api-model/ordersV0.json
    """

    name = "Orders"
    primary_key = "AmazonOrderId"
    cursor_field = "LastUpdateDate"
    replication_start_date_field = "LastUpdatedAfter"
    next_page_token_field = "NextToken"
    page_size_field = "MaxResultsPerPage"

    def path(self, **kwargs) -> str:
        return f"/orders/{ORDERS_API_VERSION}/orders"

    def request_params(
        self, stream_state: Mapping[str, Any], next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, next_page_token=next_page_token, **kwargs)
        if not next_page_token:
            params.update({"MarketplaceIds": ",".join(self.marketplace_ids)})
        return params

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        yield from response.json().get(self.data_field, {}).get(self.name, [])


class VendorDirectFulfillmentShipping(AmazonSPStream):
    """
    API docs: https://github.com/amzn/selling-partner-api-docs/blob/main/references/vendor-direct-fulfillment-shipping-api/vendorDirectFulfillmentShippingV1.md
    API model: https://github.com/amzn/selling-partner-api-models/blob/main/models/vendor-direct-fulfillment-shipping-api-model/vendorDirectFulfillmentShippingV1.json

    Returns a list of shipping labels created during the time frame that you specify.
    Both createdAfter and createdBefore parameters required to select the time frame.
    The date range to search must not be more than 7 days.
    """

    name = "VendorDirectFulfillmentShipping"
    primary_key = [["labelData", "packageIdentifier"]]
    replication_start_date_field = "createdAfter"
    next_page_token_field = "nextToken"
    page_size_field = "limit"
    time_format = "%Y-%m-%dT%H:%M:%SZ"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.replication_start_date_field = max(
            pendulum.parse(self._replication_start_date), pendulum.now("utc").subtract(days=7, hours=1)
        ).strftime(self.time_format)

    def path(self, **kwargs) -> str:
        return f"/vendor/directFulfillment/shipping/{VENDORS_API_VERSION}/shippingLabels"

    def request_params(
        self, stream_state: Mapping[str, Any], next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, next_page_token=next_page_token, **kwargs)
        if not next_page_token:
            params.update({"createdBefore": pendulum.now("utc").strftime(self.time_format)})
        return params

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        yield from response.json().get(self.data_field, {}).get("shippingLabels", [])
