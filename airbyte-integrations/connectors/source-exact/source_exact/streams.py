# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import re
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

import pendulum
import requests
from pendulum.datetime import DateTime

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import CheckpointMixin
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.streams.http import HttpStream
from source_exact.api import ExactAPI


class ExactStream(HttpStream, CheckpointMixin, ABC):
    """
    Base stream to sync endpoints from Exact, build upon HttpStream.

    It supports both full refresh and incremental sync. The cursor field is either `Timestamp` or `Modified` depending
    on the endpoint (see `ExactSyncStream` and `ExactOtherStream`). The cursor field is used to get changes since the
    last sync.

    A `division` is a separate administration within the Exact Online environment. The API requires to specify the
    division in the URL. The stream supports syncing multiple divisions.

    For each division, the state is stored separately. The state is a dictionary containing the cursor value for the
    last sync. The cursor value is the largest value of the cursor field seen so far.

    Exact enforces strict rate limits. The rate limit is 60 requests per minute. The rate limit is enforced by the API
    and is not configurable. The stream will automatically wait for 1 minute if the rate limit is exceeded.
    In addition, Exact enforces single use refresh tokens. The stream will automatically refresh the access token when
    it is expired.
    """

    endpoint: str

    def __init__(self, config):
        self._divisions = config["divisions"]
        self._base_url = config["base_url"]
        self.token_refresh_endpoint = f"{self._base_url}/api/oauth/token"
        self.api = ExactAPI(config)

        self._active_division = self._divisions[0]
        """The current division being synced."""

        # State per division, simple dictionary with the format {division: {cursor_field: cursor_value}}
        # Note: implemented state properties return the full state (i.e., all divisions)
        self._state_per_division = {}
        for division in self._divisions:
            self._state_per_division[str(division)] = {}

        super().__init__(authenticator=self.api.authenticator)

    @property
    def url_base(self) -> str:
        """URL base depends on the current division being synced."""

        return f"{self._base_url}/api/v1/{self._active_division}/"

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self._state_per_division

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        if not value:
            return

        self._state_per_division = value

    def path(
        self,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        """
        Returns the URL to call. On first call uses the property `endpoint` of subclass.
        For subsequent pages, `next_page_token` is used.
        """

        if not self.endpoint:
            raise RuntimeError("Subclass is missing endpoint")

        if next_page_token:
            return next_page_token["next_url"]

        self.logger.info(f"Syncing endpoint {self.endpoint}...")
        return self.endpoint

    def request_params(  # type: ignore[override]
        self,
        stream_state: Optional[Mapping[str, Any]],
        stream_slice: Mapping[str, Any],
        next_page_token: Optional[Mapping[str, Any]] = None,
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
        state = self._state_per_division.get(division, {})
        # TODO: how to handle case if a division is removed from the config? Keep the state of that division or delete it?
        cursor_value = state.get(self.cursor_field)

        if cursor_value:
            params["$filter"] = self._get_param_filter(cursor_value)

        if self.cursor_field == "Modified":
            params["$orderby"] = "Modified asc"

        return params

    def request_headers(
        self,
        stream_state: Optional[Mapping[str, Any]],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        """
        Overridden to request JSON response (default for Exact is XML).
        """

        return {"Accept": "application/json"}

    def _get_param_filter(self, cursor_value: str):
        """Returns the $filter clause for the cursor field."""

        if self.cursor_field == "Timestamp":
            return f"Timestamp gt {cursor_value}L"

        elif self.cursor_field != "Modified":
            raise RuntimeError(f"Source not capable of incremental syncing with cursor field '{self.cursor_field}'")

        # else: cursor_field == "Modified"

        # cursor_value is a timestamp stored as string in real UTC e.g., 2022-12-12T00:00:00.00000+00:00 (see _parse_item)
        # The Exact API (OData format) doesn't accept timezone info. Instead, we parse the timestamp into
        # the API's local timezone (CET +1h in winter and +2h in summer) without timezone info.
        # More details about the API's timezone: see _parse_item.
        utc_timestamp: DateTime = pendulum.parse(cursor_value)  # type: ignore
        if utc_timestamp.timezone_name not in ["UTC", "+00:00"]:
            self.logger.warning(
                f"The value of the cursor field 'Modified' is not detected as a UTC timestamp: {cursor_value}. "
                f"This might lead to an incorrect $filter clause and unexpected records."
            )

        tz_cet = pendulum.timezone("CET")
        cet_timestamp = tz_cet.convert(utc_timestamp)
        cet_timestamp_str = cet_timestamp.isoformat().split("+")[0]

        return f"Modified gt datetime'{cet_timestamp_str}'"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        If the response contains the __next property, there are more pages. This property contains the full url to
        call next including endpoint and all query parameters.
        """

        response_json = response.json()
        next_url = response_json.get("d", {}).get("__next")

        return {"next_url": next_url} if next_url else None

    def parse_response(self, response: requests.Response, **kwargs):
        """Overridden to parse results from the nested array."""

        response_json = response.json()
        results = response_json.get("d", {}).get("results", [])

        return [self._parse_item(x) for x in results]

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        """Implements the actual syncing of a division of the current stream."""
        # This function is called per division (each division as returned by `stream_slices`), from `read_full_refresh`
        # or `read_incremental` (at the base `Stream`).
        #
        # It is overridden to update the current division, as this needs to be updated in the `url_base` property.
        # It also keeps track of the cursor value for the current division.

        division = str(stream_slice["division"])
        self._active_division = division

        self.logger.info(f"Syncing division {division}...")

        # Reset state if full refresh
        if sync_mode == SyncMode.full_refresh:
            self._state_per_division[division] = {}

        # Perform the actual sync, and update the latest cursor value
        division_state = self._state_per_division[division]
        for record in super().read_records(
            sync_mode=sync_mode,
            cursor_field=cursor_field,
            stream_slice=stream_slice,
        ):
            if self.cursor_field and sync_mode == SyncMode.incremental:
                current_value = division_state.get(self.cursor_field)
                updated_value = record[self.cursor_field]

                if current_value is None:
                    division_state[self.cursor_field] = updated_value
                else:
                    division_state[self.cursor_field] = max(current_value, updated_value)

            yield record

    def _parse_item(self, obj: dict):
        """
        Parses response from Exact. It converts the OData date format (e.g., `/Date(1672531200000)/`) to an ISO formatted
        timestamp and casts the values to the expected type based on the JSON Schema (`int`, `float` and `bool`).
        """

        # Get the first not null type -> i.e., the expected type of the property
        property_type_lookup = {k: next(x for x in v["type"] if x != "null") for k, v in self.get_json_schema()["properties"].items()}

        regex_timestamp = re.compile(r"^\/Date\((\d+)\)\/$")

        # Recursively parse the value
        def parse_value(key, value):
            if isinstance(value, dict):
                return {k: parse_value(k, v) for k, v in value.items()}

            if isinstance(value, list):
                return [parse_value(key, v) for v in value]

            if isinstance(value, str):
                # Exact returns timestamps in the following format: /Date(1672531200000)/ (OData date format).
                # The value is in seconds since Epoch (UNIX time) format.
                # NOTE that the time is in Dutch timezone:
                # - CET (UTC+01.00) in the winter
                # - CET (UTC+02.00) in the summer
                # The `pendulum.from_timestamp(x, 'CET')` takes into account both summer and winter time.
                # A timestamp x in the winter is read as UTC+01.00, and a timestamp x in the summer is read as UTC+02.00.
                #
                # Exact API docs: https://support.exactonline.com/community/s/knowledge-base#All-All-DNO-Content-faq-rest-api
                match_timestamp = regex_timestamp.match(value)
                if match_timestamp:
                    cet_unix_seconds = int(match_timestamp.group(1)) / 1000
                    cet_offset = pendulum.from_timestamp(cet_unix_seconds, "CET").offset  # either 3600 or 7200

                    # Convert CET (+1 or +2) to UTC
                    utc_unix_seconds = cet_unix_seconds - cet_offset

                    # Create timestamp in UTC
                    timestamp = pendulum.from_timestamp(utc_unix_seconds)

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

    def test_access(self) -> bool:
        """Checks if the user has access to the specific API."""

        try:
            self.read_records(sync_mode=SyncMode.full_refresh)
            return True
            # Forbidden, user does not have access to the API
        except requests.RequestException:
            return False

    @staticmethod
    def must_deduplicate_query_params() -> bool:
        return False

    def stream_slices(
        self,
        *,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        Override the default stream_slices method to include the division in each slice.
        This is required because the request_params method expects a 'division' key in the stream slice.
        """
        return [{"division": x} for x in self._divisions]


class ExactSyncStream(ExactStream):
    """
    Exact Sync endpoints paginate by 1000 items.
    They have a column named Timestamp which denotes an entity version.
    The Timestamp value has no real correlation with a natural datetime.
    It allows for getting changes since the last sync.
    """

    state_checkpoint_interval = 1000
    primary_key = "Timestamp"
    cursor_field = "Timestamp"


class ExactOtherStream(ExactStream):
    """
    Exact non-sync endpoints paginate by 60 items.
    Often they denote regular entities which have an ID as primary key,
    and modified field to get changes since last sync.
    """

    state_checkpoint_interval = 60
    primary_key = "ID"
    cursor_field = "Modified"


class BudgetBudgets(ExactOtherStream):
    """Stream to sync to the endpoint `budget/Budgets`"""

    endpoint = "budget/Budgets"


class FinancialReceivablesList(ExactOtherStream):
    """Stream to sync the endpoint `read/financial/ReceivablesList`"""

    endpoint = "read/financial/ReceivablesList"
    primary_key = "HID"
    cursor_field = None


class HRMDepartments(ExactOtherStream):
    """Stream to sync the endpoint `hrm/departments`"""

    endpoint = "hrm/Departments"


class OpeningbalanceCurrentYearAfterEntry(ExactOtherStream):
    """Stream to sync the endpoint `openingbalance/CurrentYear/AfterEntry`"""

    endpoint = "openingbalance/CurrentYear/AfterEntry"


class PayrollActiveEmployments(ExactOtherStream):
    """Stream to sync the endpoint `payroll/ActiveEmployments`"""

    endpoint = "payroll/ActiveEmployments"


class SyncCashflowPaymentTerms(ExactSyncStream):
    """Stream to sync the endpoint `sync/Cashflow/PaymentTerms`"""

    endpoint = "sync/Cashflow/PaymentTerms"


class SyncCRMAccounts(ExactSyncStream):
    """Stream to sync the endpoint `sync/CRM/Accounts`"""

    endpoint = "sync/CRM/Accounts"


class SyncCRMAddresses(ExactSyncStream):
    """Stream to sync the endpoint `sync/CRM/Addresses`"""

    endpoint = "sync/CRM/Addresses"


class SyncCRMContacts(ExactSyncStream):
    """Stream to sync the endpoint `sync/CRM/Contacts`"""

    endpoint = "sync/CRM/Contacts"


class SyncCRMQuotationHeaders(ExactSyncStream):
    """Stream to sync the endpoint `sync/CRM/QuotationHeaders`"""

    endpoint = "sync/CRM/QuotationHeaders"


class SyncCRMQuotationLines(ExactSyncStream):
    """Stream to sync the endpoint `sync/CRM/QuotationLines`"""

    endpoint = "sync/CRM/QuotationLines"


class SyncDeleted(ExactSyncStream):
    """Stream to sync the endpoint `sync/Deleted`"""

    endpoint = "sync/Deleted"


class SyncDocumentsDocumentAttachments(ExactSyncStream):
    """Stream to sync the endpoint `sync/Documents/DocumentAttachments`"""

    endpoint = "sync/Documents/DocumentAttachments"


class SyncDocumentsDocuments(ExactSyncStream):
    """Stream to sync the endpoint `sync/Documents/Documents`"""

    endpoint = "sync/Documents/Documents"


class SyncFinancialGLAccounts(ExactSyncStream):
    """Stream to sync the endpoint `sync/Financial/GLAccounts`"""

    endpoint = "sync/Financial/GLAccounts"


class SyncFinancialGLClassifications(ExactSyncStream):
    """Stream to sync the endpoint `sync/Financial/GLClassifications`"""

    endpoint = "sync/Financial/GLClassifications"


class SyncFinancialTransactionLines(ExactSyncStream):
    """Stream to sync the endpoint `sync/Financial/TransactionLines`"""

    endpoint = "sync/Financial/TransactionLines"


class SyncHRMLeaveAbsenceHoursByDay(ExactSyncStream):
    """Stream to sync the endpoint `sync/HRM/LeaveAbsenceHoursByDay`"""

    endpoint = "sync/HRM/LeaveAbsenceHoursByDay"


class SyncHRMScheduleEntries(ExactSyncStream):
    """Stream to sync the endpoint `sync/HRM/ScheduleEntries`"""

    endpoint = "sync/HRM/ScheduleEntries"


class SyncHRMSchedules(ExactSyncStream):
    """Stream to sync the endpoint `sync/HRM/Schedules`"""

    endpoint = "sync/HRM/Schedules"


class SyncInventoryItemStorageLocations(ExactSyncStream):
    """Stream to sync the endpoint `sync/Inventory/ItemStorageLocations`"""

    endpoint = "sync/Inventory/ItemStorageLocations"


class SyncInventoryItemWarehouses(ExactSyncStream):
    """Stream to sync the endpoint `sync/Inventory/ItemWarehouses`"""

    endpoint = "sync/Inventory/ItemWarehouses"


class SyncInventorySerialBatchNumbers(ExactSyncStream):
    """Stream to sync the endpoint `sync/Inventory/SerialBatchNumbers`"""

    endpoint = "sync/Inventory/SerialBatchNumbers"


class SyncInventoryStockPositions(ExactSyncStream):
    """Stream to sync the endpoint `sync/Inventory/StockPositions`"""

    endpoint = "sync/Inventory/StockPositions"


class SyncInventoryStockSerialBatchNumbers(ExactSyncStream):
    """Stream to sync the endpoint `sync/Inventory/StockSerialBatchNumbers`"""

    endpoint = "sync/Inventory/StockSerialBatchNumbers"


class SyncInventoryStorageLocationStockPositions(ExactSyncStream):
    """Stream to sync the endpoint `sync/Inventory/StorageLocationStockPositions`"""

    endpoint = "sync/Inventory/StorageLocationStockPositions"


class SyncLogisticsItems(ExactSyncStream):
    """Stream to sync the endpoint `sync/Logistics/Items`"""

    endpoint = "sync/Logistics/Items"


class SyncLogisticsPurchaseItemPrices(ExactSyncStream):
    """Stream to sync the endpoint `sync/Logistics/PurchaseItemPrices`"""

    endpoint = "sync/Logistics/PurchaseItemPrices"


class SyncLogisticsSalesItemPrices(ExactSyncStream):
    """Stream to sync the endpoint `sync/Logistics/SalesItemPrices`"""

    endpoint = "sync/Logistics/SalesItemPrices"


class SyncLogisticsSupplierItem(ExactSyncStream):
    """Stream to sync the endpoint `sync/Logistics/SupplierItem`"""

    endpoint = "sync/Logistics/SupplierItem"


class SyncManufacturingShopOrderMaterialPlans(ExactSyncStream):
    """Stream to sync the endpoint `sync/Manufacturing/ShopOrderMaterialPlans`"""

    endpoint = "sync/Manufacturing/ShopOrderMaterialPlans"


class SyncManufacturingShopOrderRoutingStepPlans(ExactSyncStream):
    """Stream to sync the endpoint `sync/Manufacturing/ShopOrderRoutingStepPlans`"""

    endpoint = "sync/Manufacturing/ShopOrderRoutingStepPlans"


class SyncManufacturingShopOrders(ExactSyncStream):
    """Stream to sync the endpoint `sync/Manufacturing/ShopOrders`"""

    endpoint = "sync/Manufacturing/ShopOrders"


class SyncPayrollEmployees(ExactSyncStream):
    """Stream to sync the endpoint `/sync/Payroll/Employees`"""

    endpoint = "/sync/Payroll/Employees"


class SyncPayrollEmploymentOrganisations(ExactSyncStream):
    """Stream to sync the endpoint `/sync/Payroll/EmploymentOrganizations`"""

    endpoint = "sync/Payroll/EmploymentOrganizations"


class SyncPayrollEmployments(ExactSyncStream):
    """Stream to sync the endpoint `sync/Payroll/Employments`"""

    endpoint = "/sync/Payroll/Employments"


class SyncProjectProjectPlanning(ExactSyncStream):
    """Stream to sync the endpoint `sync/Project/ProjectPlanning`"""

    endpoint = "sync/Project/ProjectPlanning"


class SyncProjectProjects(ExactSyncStream):
    """Stream to sync the endpoint `sync/Project/Projects`"""

    endpoint = "sync/Project/Projects"


class SyncProjectProjectWBS(ExactSyncStream):
    """Stream to sync the endpoint `sync/Project/ProjectWBS`"""

    endpoint = "sync/Project/ProjectWBS"


class SyncProjectTimeCostTransactions(ExactSyncStream):
    """Stream to sync the endpoint `sync/Project/TimeCostTransactions`"""

    endpoint = "sync/Project/TimeCostTransactions"


class SyncPurchaseOrderPurchaseOrders(ExactSyncStream):
    """Stream to sync the endpoint `sync/PurchaseOrder/PurchaseOrders`"""

    endpoint = "sync/PurchaseOrder/PurchaseOrders"


class SyncSalesSalesPriceListVolumeDiscounts(ExactSyncStream):
    """Stream to sync the endpoint `sync/Sales/SalesPriceListVolumeDiscounts`"""

    endpoint = "sync/Sales/SalesPriceListVolumeDiscounts"


class SyncSalesInvoiceSalesInvoices(ExactSyncStream):
    """Stream to sync the endpoint `sync/SalesInvoice/SalesInvoices`"""

    endpoint = "sync/SalesInvoice/SalesInvoices"


class SyncSalesOrderGoodsDeliveries(ExactSyncStream):
    """Stream to sync the endpoint `sync/SalesOrder/GoodsDeliveries`"""

    endpoint = "sync/SalesOrder/GoodsDeliveries"


class SyncSalesOrderGoodsDeliveryLines(ExactSyncStream):
    """Stream to sync the endpoint `sync/SalesOrder/GoodsDeliveryLines`"""

    endpoint = "sync/SalesOrder/GoodsDeliveryLines"


class SyncSalesOrderSalesOrderHeaders(ExactSyncStream):
    """Stream to sync the endpoint `sync/SalesOrder/SalesOrderHeaders`"""

    endpoint = "sync/SalesOrder/SalesOrderHeaders"


class SyncSalesOrderSalesOrderLines(ExactSyncStream):
    """Stream to sync the endpoint `sync/SalesOrder/SalesOrderLines`"""

    endpoint = "sync/SalesOrder/SalesOrderLines"


class SyncSubscriptionSubscriptionLines(ExactSyncStream):
    """Stream to sync the endpoint `sync/Subscription/SubscriptionLines`"""

    endpoint = "sync/Subscription/SubscriptionLines"


class SyncSubscriptionSubscriptions(ExactSyncStream):
    """Stream to sync the endpoint `sync/Subscription/Subscriptions`"""

    endpoint = "sync/Subscription/Subscriptions"


class CRMAccountClassifications(ExactOtherStream):
    """Stream to sync the endpoint `crm/AccountClassifications`"""

    endpoint = "crm/AccountClassifications"


class CRMAccountClassificationNames(ExactOtherStream):
    """Stream to sync the endpoint `crm/AccountClassificationNames`"""

    endpoint = "crm/AccountClassificationNames"


class ProjectInvoiceTerms(ExactOtherStream):
    """Stream to sync the endpoint `project/ProjectInvoiceTerms`"""

    endpoint = "project/InvoiceTerms"


class RequestBodyException(Exception):
    """
    Raised when there are issues in configuring a request body
    Exception could probably be removed by using HttpStreamAdapterHttpStatusErrorHandler
    or similar exception
    """
