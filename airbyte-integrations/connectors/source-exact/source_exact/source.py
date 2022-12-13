#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
import random
import re
import json
import time
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import unquote

import pendulum
import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import IncrementalMixin, Stream
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import SingleUseRefreshTokenOauth2Authenticator


class ExactStream(HttpStream, IncrementalMixin):
    _cursor_value = None

    def __init__(self, config: Mapping[str, Any]):
        self._url_base = f"https://start.exactonline.nl/api/v1/{config['division']}/"

        auth = SingleUseRefreshTokenOauth2Authenticator(
            connector_config=config,
            token_refresh_endpoint="https://start.exactonline.nl/api/oauth2/token",
            token_expiry_date=pendulum.now().add(minutes=11),
        )
        auth.access_token = config["credentials"]["access_token"]

        super().__init__(auth)

    @property
    def url_base(self) -> str:
        return self._url_base

    @property
    def state(self) -> MutableMapping[str, Any]:
        return {
            self.cursor_field: self._cursor_value,
        }

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        if not value:
            return

        if self.cursor_field in value:
            self._cursor_value = value[self.cursor_field]

    def read_records(self, *args, **kwargs) -> Iterable[StreamData]:
        for record in super().read_records(*args, **kwargs):
            # Track the largest cursor value
            cursor_value = record[self.cursor_field]
            self._cursor_value = max(cursor_value, self._cursor_value) if self._cursor_value else cursor_value

            yield record

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        If response contains the __next property, there are more pages. This property contains the full url to
        call next including endpoint and all query parameters.
        """

        response_json = response.json()
        next_url = response_json.get("d", {}).get("__next")

        return {"next_url": next_url} if next_url else None

    def request_headers(self, **kwargs) -> MutableMapping[str, Any]:
        """
        Default response type is XML, this is overriden to return JSON.
        """

        return {"Accept": "application/json"}

    def request_params(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        """
        The sync endpoints requires selection of fields to return. We use the configured catalog to make selection
        of fields we want to have.
        """

        # Contains the full next page, so don't append new query params
        if next_page_token:
            return {}

        configured_properties = list(self.get_json_schema()["properties"].keys())
        params = {
            "$select": ",".join(configured_properties),
        }

        if self._cursor_value:
            if self.cursor_field == "Timestamp":
                params["$filter"] = f"Timestamp gt {self._cursor_value}L"
            elif self.cursor_field == "Modified":
                # value is a timestamp stored as string in UTC e.g., 2022-12-12T00:00:00.00000+00:00 (see _parse_timestamps)
                # The Exact API (OData format) doesn't accept timezone info. Instead, we parse the timestamp into
                # the API's local timezone (CET) without timezone info.

                tz_cet = pendulum.timezone("CET")
                timestamp = pendulum.parse(self._cursor_value)
                timestamp = tz_cet.convert(timestamp)
                timestamp_str = timestamp.isoformat().split("+")[0]

                params["$filter"] = f"Modified gt datetime'{timestamp_str}'"
            else:
                raise RuntimeError(f"Source not capable of incremental syncing with cursor field '{self.cursor_field}'")

        return params

    def _send_request(self, request: requests.PreparedRequest, request_kwargs: Mapping[str, Any]) -> requests.Response:
        """
        Overwrite the default _send_request. This allows to automatically refresh the access token when it is
        expired.
        """

        logger = logging.getLogger("airbyte")

        for num_retry in range(self.max_retries):
            try:
                response = self._send(request, request_kwargs)
                return response

            except requests.RequestException as exc:
                response: requests.Response = exc.response
                if response is None:
                    raise exc

                # Retry on server exceptions
                if 500 <= response.status_code < 600:
                    time.sleep(2**num_retry + random.random())
                    continue

                # Check for expired access token
                if response.status_code == 401:
                    error_reason = response.headers.get("WWW-Authenticate", "")
                    error_reason = unquote(error_reason)

                    if "access token expired" in error_reason:
                        logger.info("Access token expired: will retry after refresh")

                        # mark the token as expired and overwrite thea authorization header
                        self._auth.set_token_expiry_date(pendulum.now().subtract(minutes=1))
                        request.headers.update(self._auth.get_auth_header())

                        continue

                raise exc

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        # Parse the results array from returned object
        response_json = response.json()
        results = response_json.get("d", {}).get("results")

        return [self._parse_timestamps(x) for x in results]

    def path(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> str:
        """
        Returns the URL to call. On first call uses the property `endpoint` of subclass. For subsequent
        pages, `next_page_token` is used.
        """

        if not self.endpoint:
            raise RuntimeError("Subclass is missing endpoint")

        if next_page_token:
            return next_page_token["next_url"]

        return self.endpoint

    @property
    def _auth(self) -> SingleUseRefreshTokenOauth2Authenticator:
        """Helper property to return the Authenticator in the right type."""

        return self._session.auth

    def _is_token_expired(self, response: requests.Response):
        if response.status_code == 401:
            error_reason = response.headers.get("WWW-Authenticate", "")
            error_reason = unquote(error_reason)

            if "message expired" in error_reason or "access token expired" in error_reason:
                return True

            raise RuntimeError(f"Unexpected forbidden error: {error_reason}")

        return False

    def _parse_timestamps(self, obj: dict):
        """
        Exact returns timestamps in following format: /Date(1672531200000)/ (OData date format).
        The value is in seconds since Epoch (UNIX time). Note, the time is in CET and not in GMT/UTC.
        https://support.exactonline.com/community/s/knowledge-base#All-All-DNO-Content-faq-rest-api
        """

        regex_timestamp = re.compile(r"^\/Date\((\d+)\)\/$")
        tz_utc = pendulum.timezone("UTC")

        def parse_value(value):
            if isinstance(value, dict):
                return {k: parse_value(v) for k, v in value.items()}

            if isinstance(value, list):
                return [parse_value(v) for v in value]

            if isinstance(value, str):
                match = regex_timestamp.match(value)
                if match:
                    unix_seconds = int(match.group(1)) / 1000

                    timestamp = pendulum.from_timestamp(unix_seconds, "CET")
                    timestamp = tz_utc.convert(timestamp)

                    return timestamp.isoformat()

            return value

        return {k: parse_value(v) for k, v in obj.items()}


class ExactSyncStream(ExactStream):
    # Exact Sync endpoints paginate by 1000 items. They have a column named Timestamp which denotes a entity version,
    # the value has no real correlation with a natural datetime. It allows for getting changes since the last sync.
    state_checkpoint_interval = 1000
    primary_key = "Timestamp"
    cursor_field = "Timestamp"


class ExactOtherStream(ExactStream):
    # Exact non-sync endpoints paginate by 60 items. Often they denote regular entities which have a ID as primary
    # key, and modified field to get changes since last sync.
    state_checkpoint_interval = 60
    primary_key = "ID"
    cursor_field = "Modified"


class SyncCashflowPaymentTerms(ExactSyncStream):
    endpoint = "sync/Cashflow/PaymentTerms"


class SyncCRMAccounts(ExactSyncStream):
    endpoint = "sync/CRM/Accounts"


class SyncCRMAddresses(ExactSyncStream):
    endpoint = "sync/CRM/Addresses"


class SyncCRMContacts(ExactSyncStream):
    endpoint = "sync/CRM/Contacts"


class SyncCRMQuotationHeaders(ExactSyncStream):
    endpoint = "sync/CRM/QuotationHeaders"


class SyncCRMQuotationLines(ExactSyncStream):
    endpoint = "sync/CRM/QuotationLines"


class SyncCRMQuotations(ExactSyncStream):
    endpoint = "sync/CRM/Quotations"


class SyncDeleted(ExactSyncStream):
    endpoint = "sync/Deleted"


class SyncDocumentsDocumentAttachments(ExactSyncStream):
    endpoint = "sync/Documents/DocumentAttachments"


class SyncDocumentsDocuments(ExactSyncStream):
    endpoint = "sync/Documents/Documents"


class SyncFinancialGLAccounts(ExactSyncStream):
    endpoint = "sync/Financial/GLAccounts"


class SyncFinancialGLClassifications(ExactSyncStream):
    endpoint = "sync/Financial/GLClassifications"


class SyncFinancialTransactionLines(ExactSyncStream):
    endpoint = "sync/Financial/TransactionLines"


class SyncHRMLeaveAbsenceHoursByDay(ExactSyncStream):
    endpoint = "sync/HRM/LeaveAbsenceHoursByDay"


class SyncInventoryItemWarehouses(ExactSyncStream):
    endpoint = "sync/Inventory/ItemWarehouses"


class SyncInventorySerialBatchNumbers(ExactSyncStream):
    endpoint = "sync/Inventory/SerialBatchNumbers"


class SyncInventoryStockPositions(ExactSyncStream):
    endpoint = "sync/Inventory/StockPositions"


class SyncInventoryStockSerialBatchNumbers(ExactSyncStream):
    endpoint = "sync/Inventory/StockSerialBatchNumbers"


class SyncInventoryStorageLocationStockPositions(ExactSyncStream):
    endpoint = "sync/Inventory/StorageLocationStockPositions"


class SyncLogisticsItems(ExactSyncStream):
    endpoint = "sync/Logistics/Items"


class SyncLogisticsPurchaseItemPrices(ExactSyncStream):
    endpoint = "sync/Logistics/PurchaseItemPrices"


class SyncLogisticsSalesItemPrices(ExactSyncStream):
    endpoint = "sync/Logistics/SalesItemPrices"


class SyncLogisticsSupplierItem(ExactSyncStream):
    endpoint = "sync/Logistics/SupplierItem"


class SyncProjectProjectPlanning(ExactSyncStream):
    endpoint = "sync/Project/ProjectPlanning"


class SyncProjectProjects(ExactSyncStream):
    endpoint = "sync/Project/Projects"


class SyncProjectProjectWBS(ExactSyncStream):
    endpoint = "sync/Project/ProjectWBS"


class SyncProjectTimeCostTransactions(ExactSyncStream):
    endpoint = "sync/Project/TimeCostTransactions"


class SyncPurchaseOrderPurchaseOrders(ExactSyncStream):
    endpoint = "sync/PurchaseOrder/PurchaseOrders"


class SyncSalesSalesPriceListVolumeDiscounts(ExactSyncStream):
    endpoint = "sync/Sales/SalesPriceListVolumeDiscounts"


class SyncSalesInvoiceSalesInvoices(ExactSyncStream):
    endpoint = "sync/SalesInvoice/SalesInvoices"


class SyncSalesOrderGoodsDeliveries(ExactSyncStream):
    endpoint = "sync/SalesOrder/GoodsDeliveries"


class SyncSalesOrderGoodsDeliveryLines(ExactSyncStream):
    endpoint = "sync/SalesOrder/GoodsDeliveryLines"


class SyncSalesOrderSalesOrderHeaders(ExactSyncStream):
    endpoint = "sync/SalesOrder/SalesOrderHeaders"


class SyncSalesOrderSalesOrderLines(ExactSyncStream):
    endpoint = "sync/SalesOrder/SalesOrderLines"


class SyncSalesOrderSalesOrders(ExactSyncStream):
    endpoint = "sync/SalesOrder/SalesOrders"


class SyncSubscriptionSubscriptionLines(ExactSyncStream):
    endpoint = "sync/Subscription/SubscriptionLines"


class SyncSubscriptionSubscriptions(ExactSyncStream):
    endpoint = "sync/Subscription/Subscriptions"

class CRMAccountClassifications(ExactOtherStream):
    endpoint = "crm/AccountClassifications"


class CRMAccountClassificationNames(ExactOtherStream):
    endpoint = "crm/AccountClassificationNames"


# Source
class SourceExact(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        access_token = config.get("credentials", {}).get("access_token")
        refresh_token = config.get("credentials", {}).get("refresh_token")

        if not access_token or not refresh_token:
            return False, "Missing access or refresh token"

        try:
            headers = ExactStream.request_headers(None)
            headers["Authorization"] = f"Bearer {access_token}"

            response = requests.get(
                "https://start.exactonline.nl/api/v1/current/Me",
                headers=headers,
                timeout=15,
            )

            response.raise_for_status()
            logger.info(f"Connection check successful. Details:\n{json.dumps(response.json())}")
        except requests.RequestException as exc:
            return False, f"Check if access_token is still valid at this point. Details\n{exc}"

        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [
            SyncCashflowPaymentTerms(config),
            SyncCRMAccounts(config),
            SyncCRMAddresses(config),
            SyncCRMContacts(config),
            SyncCRMQuotationHeaders(config),
            SyncCRMQuotationLines(config),
            SyncCRMQuotations(config),
            SyncDeleted(config),
            SyncDocumentsDocumentAttachments(config),
            SyncDocumentsDocuments(config),
            SyncFinancialGLAccounts(config),
            SyncFinancialGLClassifications(config),
            SyncFinancialTransactionLines(config),
            SyncHRMLeaveAbsenceHoursByDay(config),
            SyncInventoryItemWarehouses(config),
            SyncInventorySerialBatchNumbers(config),
            SyncInventoryStockPositions(config),
            SyncInventoryStockSerialBatchNumbers(config),
            SyncInventoryStorageLocationStockPositions(config),
            SyncLogisticsItems(config),
            SyncLogisticsPurchaseItemPrices(config),
            SyncLogisticsSalesItemPrices(config),
            SyncLogisticsSupplierItem(config),
            SyncProjectProjectPlanning(config),
            SyncProjectProjects(config),
            SyncProjectProjectWBS(config),
            SyncProjectTimeCostTransactions(config),
            SyncPurchaseOrderPurchaseOrders(config),
            SyncSalesSalesPriceListVolumeDiscounts(config),
            SyncSalesInvoiceSalesInvoices(config),
            SyncSalesOrderGoodsDeliveries(config),
            SyncSalesOrderGoodsDeliveryLines(config),
            SyncSalesOrderSalesOrderHeaders(config),
            SyncSalesOrderSalesOrderLines(config),
            SyncSalesOrderSalesOrders(config),
            SyncSubscriptionSubscriptionLines(config),
            SyncSubscriptionSubscriptions(config),
            CRMAccountClassifications(config),
            CRMAccountClassificationNames(config),
        ]
