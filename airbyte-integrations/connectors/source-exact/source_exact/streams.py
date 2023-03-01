#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import random
import re
import time
from typing import Any, Iterable, Mapping, MutableMapping, Optional
from urllib.parse import unquote

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import IncrementalMixin
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import SingleUseRefreshTokenOauth2Authenticator


# TEMP: patch SingleUseRefreshTokenOauth2Authenticator to mitigate expires_in bug
# See https://github.com/airbytehq/airbyte/pull/20301
class MySingleUseRefreshTokenOauth2Authenticator(SingleUseRefreshTokenOauth2Authenticator):
    def refresh_access_token(self):
        access_token, expires_in, refresh_token = super().refresh_access_token()
        return access_token, int(expires_in), refresh_token


class ExactStream(HttpStream, IncrementalMixin):
    def __init__(self, config: Mapping[str, Any]):
        self._divisions = config["divisions"]

        self._state_per_division = {}
        for division in self._divisions:
            self._state_per_division[str(division)] = {}

        self._single_refresh_token_authenticator = MySingleUseRefreshTokenOauth2Authenticator(
            connector_config=config,
            token_refresh_endpoint="https://start.exactonline.nl/api/oauth2/token",
        )
        self._single_refresh_token_authenticator.access_token = config["credentials"]["access_token"]

        super().__init__(self._single_refresh_token_authenticator)

    @property
    def url_base(self) -> str:
        """Overridden as the base url depends on the config (passed at __init__)."""

        return self._url_base

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self._state_per_division

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        if not value:
            return

        self._state_per_division = value

    def path(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> str:
        """
        Returns the URL to call. On first call uses the property `endpoint` of subclass. For subsequent
        pages, `next_page_token` is used.
        """

        if not self.endpoint:
            raise RuntimeError("Subclass is missing endpoint")

        if next_page_token:
            return next_page_token["next_url"]

        self.logger.info(f"Syncing endpoint {self.endpoint}...")
        return self.endpoint

    def request_headers(self, **kwargs) -> MutableMapping[str, Any]:
        """
        Overridden to request JSON response (default for Exact is XML).
        """

        return {"Accept": "application/json"}

    def request_params(
        self, next_page_token: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
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

        division = str(stream_slice["division"])
        state = self._state_per_division[division]
        cursor_value = state.get(self.cursor_field)

        if cursor_value:
            if self.cursor_field == "Timestamp":
                params["$filter"] = f"Timestamp gt {cursor_value}L"
            elif self.cursor_field == "Modified":
                # value is a timestamp stored as string in UTC e.g., 2022-12-12T00:00:00.00000+00:00 (see _parse_item)
                # The Exact API (OData format) doesn't accept timezone info. Instead, we parse the timestamp into
                # the API's local timezone (CET) without timezone info.

                tz_cet = pendulum.timezone("CET")
                timestamp = pendulum.parse(cursor_value)
                timestamp = tz_cet.convert(timestamp)
                timestamp_str = timestamp.isoformat().split("+")[0]

                params["$filter"] = f"Modified gt datetime'{timestamp_str}'"
            else:
                raise RuntimeError(f"Source not capable of incremental syncing with cursor field '{self.cursor_field}'")

        if self.cursor_field == "Modified":
            params["$orderby"] = "Modified asc"

        return params

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        If response contains the __next property, there are more pages. This property contains the full url to
        call next including endpoint and all query parameters.
        """

        response_json = response.json()
        next_url = response_json.get("d", {}).get("__next")

        return {"next_url": next_url} if next_url else None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """Overridden to parse results from the nested array."""

        response_json = response.json()
        results = response_json.get("d", {}).get("results", [])

        return [self._parse_item(x) for x in results]

    def read_records(self, sync_mode: SyncMode, stream_slice: Mapping[str, Any] = None, **kwargs) -> Iterable[StreamData]:
        """Overridden to change the url_base based on the current division, and to keep track of the cursor."""

        division = str(stream_slice["division"])
        self._url_base = f"https://start.exactonline.nl/api/v1/{division}/"

        self.logger.info(f"Syncing division {division}...")

        # Reset state for full refresh
        if sync_mode == SyncMode.full_refresh:
            self._state_per_division[division] = {}

        for record in super().read_records(sync_mode=sync_mode, stream_slice=stream_slice, **kwargs):
            # Track the largest cursor value
            if self.cursor_field and sync_mode == SyncMode.incremental:
                cursor_value = record[self.cursor_field]
                current_cursor_value = self._state_per_division[division].get(self.cursor_field)
                current_cursor_value = cursor_value if not current_cursor_value else current_cursor_value

                if current_cursor_value:
                    self._state_per_division[division].update({self.cursor_field: max(cursor_value, current_cursor_value)})

            yield record

    def _is_token_expired(self, response: requests.Response):
        if response.status_code == 401:
            error_reason = response.headers.get("WWW-Authenticate", "")
            error_reason = unquote(error_reason)

            if "message expired" in error_reason or "access token expired" in error_reason:
                return True

            raise RuntimeError(f"Unexpected forbidden error: {error_reason}")

        return False

    def _parse_item(self, obj: dict):
        """
        Parses single result item:
        - OData dates (/Date(1672531200000)/) are parsed to iso formatted timestamps 2022-12-12T12:00:00
        - int, float and booleans are casted based on the JSON Schema type field
        """

        # Get the first not null type -> i.e., the expected type of the property
        property_type_lookup = {k: next(x for x in v["type"] if x != "null") for k, v in self.get_json_schema()["properties"].items()}

        regex_timestamp = re.compile(r"^\/Date\((\d+)\)\/$")
        tz_utc = pendulum.timezone("UTC")

        def parse_value(key, value):
            if isinstance(value, dict):
                return {k: parse_value(k, v) for k, v in value.items()}

            if isinstance(value, list):
                return [parse_value(key, v) for v in value]

            if isinstance(value, str):
                # Exact returns timestamps in following format: /Date(1672531200000)/ (OData date format).
                # The value is in seconds since Epoch (UNIX time). Note, the time is in CET and not in GMT/UTC.
                # https://support.exactonline.com/community/s/knowledge-base#All-All-DNO-Content-faq-rest-api
                match_timestamp = regex_timestamp.match(value)
                if match_timestamp:
                    unix_seconds = int(match_timestamp.group(1)) / 1000

                    timestamp = pendulum.from_timestamp(unix_seconds, "CET")
                    timestamp = tz_utc.convert(timestamp)

                    return timestamp.isoformat()

                expected_type = property_type_lookup.get(key)
                if expected_type == "number":
                    return float(value)
                elif expected_type == "integer":
                    return int(value)
                elif expected_type == "boolean":
                    return value and value.lower() == "true"

            return value

        return parse_value(None, obj)

    def _send_request(self, request: requests.PreparedRequest, request_kwargs: Mapping[str, Any]) -> requests.Response:
        """
        Overwrite the default _send_request. This allows to automatically refresh the access token when it is
        expired.
        """

        for num_retry in range(self.max_retries):
            try:
                response = self._send(request, request_kwargs)
                return response

            # Retry on timeout
            except requests.exceptions.Timeout:
                pass

            # On other exceptions, we possibly refresh the token and retry
            except requests.RequestException as exc:
                response: requests.Response = exc.response
                if response is None:
                    raise exc

                # Retry on server exceptions
                if 500 <= response.status_code < 600:
                    time.sleep(2**num_retry + random.random())
                    continue

                # Retry on 429 (Too Many Requests)
                # Exact rate limit resets after 1 minute, so we just wait 1 minute and retry
                if response.status_code == 429:
                    self.logger.debug("Rate limit exceeded: will retry after 1 minute")
                    time.sleep(61)
                    continue

                if not self._is_token_expired(response):
                    raise exc

                self.logger.info("Access token expired: will retry after refresh")

                try:
                    # mark the token as expired and overwrite thea authorization header
                    self._single_refresh_token_authenticator.set_token_expiry_date(pendulum.now().subtract(minutes=1))
                    request.headers.update(self._single_refresh_token_authenticator.get_auth_header())

                except Exception as exc:
                    raise Exception("Failed to refresh expired access token") from exc

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        """Overridden to return a list of divisions to extract endpoints for."""

        return [{"division": x} for x in self._divisions]


class ExactSyncStream(ExactStream):
    """
    Exact Sync endpoints paginate by 1000 items. They have a column named Timestamp which denotes a entity version,
    the value has no real correlation with a natural datetime. It allows for getting changes since the last sync.
    """

    state_checkpoint_interval = 1000
    primary_key = "Timestamp"
    cursor_field = "Timestamp"


class ExactOtherStream(ExactStream):
    """
    Exact non-sync endpoints paginate by 60 items. Often they denote regular entities which have a ID as primary
    key, and modified field to get changes since last sync.
    """

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
