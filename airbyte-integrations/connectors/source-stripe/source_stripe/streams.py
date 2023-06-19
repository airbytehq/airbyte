#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import math
from abc import ABC, abstractmethod
from itertools import chain
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Type

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from source_stripe.availability_strategy import StripeSubStreamAvailabilityStrategy

STRIPE_ERROR_CODES: List = [
    # stream requires additional permissions
    "more_permissions_required",
    # account_id doesn't have the access to the stream
    "account_invalid",
]


class StripeStream(HttpStream, ABC):
    url_base = "https://api.stripe.com/v1/"
    primary_key = "id"
    DEFAULT_SLICE_RANGE = 365
    transformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)

    def __init__(self, start_date: int, account_id: str, slice_range: int = DEFAULT_SLICE_RANGE, **kwargs):
        super().__init__(**kwargs)
        self.account_id = account_id
        self.start_date = start_date
        self.slice_range = slice_range or self.DEFAULT_SLICE_RANGE

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        decoded_response = response.json()
        if "has_more" in decoded_response and decoded_response["has_more"] and decoded_response.get("data", []):
            last_object_id = decoded_response["data"][-1]["id"]
            return {"starting_after": last_object_id}

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        # Stripe default pagination is 10, max is 100
        params = {"limit": 100}
        # Handle pagination by inserting the next page's token in the request parameters
        if next_page_token:
            params.update(next_page_token)

        return params

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        if self.account_id:
            return {"Stripe-Account": self.account_id}
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        yield from response_json.get("data", [])  # Stripe puts records in a container array "data"

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        try:
            yield from super().read_records(sync_mode, cursor_field, stream_slice, stream_state)
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            parsed_error = e.response.json()
            error_code = parsed_error.get("error", {}).get("code")
            error_message = parsed_error.get("message")
            # if the API Key doesn't have required permissions to particular stream, this stream will be skipped
            if status_code == 403 and error_code in STRIPE_ERROR_CODES:
                self.logger.warn(f"Stream {self.name} is skipped, due to {error_code}. Full message: {error_message}")
                pass
            else:
                self.logger.error(f"Syncing stream {self.name} is failed, due to {error_code}. Full message: {error_message}")


class BasePaginationStripeStream(StripeStream, ABC):
    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        for key in ("created[gte]", "created[lte]"):
            if key in stream_slice:
                params[key] = stream_slice[key]
        return params

    def chunk_dates(self, start_date_ts: int) -> Iterable[Tuple[int, int]]:
        now = pendulum.now().int_timestamp
        step = int(pendulum.duration(days=self.slice_range).total_seconds())
        after_ts = start_date_ts
        while after_ts < now:
            before_ts = min(now, after_ts + step)
            yield after_ts, before_ts
            after_ts = before_ts + 1

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        for start, end in self.chunk_dates(self.start_date):
            yield {"created[gte]": start, "created[lte]": end}

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        if stream_slice is None:
            return []

        yield from super().read_records(sync_mode, cursor_field, stream_slice, stream_state)


class IncrementalStripeStream(BasePaginationStripeStream, ABC):
    # Stripe returns most recently created objects first, so we don't want to persist state until the entire stream has been read
    state_checkpoint_interval = math.inf

    def __init__(self, lookback_window_days: int = 0, **kwargs):
        super().__init__(**kwargs)
        self.lookback_window_days = lookback_window_days

    @property
    @abstractmethod
    def cursor_field(self) -> str:
        """
        Defining a cursor field indicates that a stream is incremental, so any incremental stream must extend this class
        and define a cursor field.
        """
        pass

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        return {self.cursor_field: max(latest_record.get(self.cursor_field), current_stream_state.get(self.cursor_field, 0))}

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        start_ts = self.get_start_timestamp(stream_state)
        if start_ts >= pendulum.now().int_timestamp:
            # if the state is in the future - this will produce a state message but not make an API request
            yield None
        else:
            for start, end in self.chunk_dates(start_ts):
                yield {"created[gte]": start, "created[lte]": end}

    def get_start_timestamp(self, stream_state) -> int:
        start_point = self.start_date
        if stream_state and self.cursor_field in stream_state:
            start_point = max(start_point, stream_state[self.cursor_field])

        if start_point and self.lookback_window_days:
            self.logger.info(f"Applying lookback window of {self.lookback_window_days} days to stream {self.name}")
            start_point = int(pendulum.from_timestamp(start_point).subtract(days=abs(self.lookback_window_days)).timestamp())

        return start_point


class Authorizations(IncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/issuing/authorizations/list
    """

    cursor_field = "created"

    def path(self, **kwargs) -> str:
        return "issuing/authorizations"


class Customers(IncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/customers/list
    """

    cursor_field = "created"
    use_cache = True

    def path(self, **kwargs) -> str:
        return "customers"


class BalanceTransactions(IncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/balance_transactions/list
    """

    cursor_field = "created"
    name = "balance_transactions"

    def path(self, **kwargs) -> str:
        return "balance_transactions"


class Cardholders(IncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/issuing/cardholders/list
    """

    cursor_field = "created"

    def path(self, **kwargs) -> str:
        return "issuing/cardholders"


class Charges(IncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/charges/list
    """

    cursor_field = "created"

    def path(self, **kwargs) -> str:
        return "charges"


class CustomerBalanceTransactions(BasePaginationStripeStream):
    """
    API docs: https://stripe.com/docs/api/customer_balance_transactions/list
    """

    name = "customer_balance_transactions"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs):
        return f"customers/{stream_slice['id']}/balance_transactions"

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        parent_stream = Customers(authenticator=self.authenticator, account_id=self.account_id, start_date=self.start_date)
        slices = parent_stream.stream_slices(sync_mode=SyncMode.full_refresh)
        for _slice in slices:
            for customer in parent_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=_slice):
                # we use `get` here because some attributes may not be returned by some API versions
                if customer.get("next_invoice_sequence") == 1 and customer.get("balance") == 0:
                    # We're making this check in order to speed up a sync. if a customer's balance is 0 and there are no
                    # associated invoices, he shouldn't have any balance transactions. So we're saving time of one API call per customer.
                    continue
                yield customer


class Coupons(IncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/coupons/list
    """

    cursor_field = "created"

    def path(self, **kwargs):
        return "coupons"


class Disputes(IncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/disputes/list
    """

    cursor_field = "created"

    def path(self, **kwargs):
        return "disputes"


class EarlyFraudWarnings(StripeStream):
    """
    API docs: https://stripe.com/docs/api/radar/early_fraud_warnings/list
    """

    def path(self, **kwargs):
        return "radar/early_fraud_warnings"


class Events(IncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/events/list
    """

    cursor_field = "created"

    def path(self, **kwargs):
        return "events"


class StripeSubStream(BasePaginationStripeStream, ABC):
    """
    Research shows that records related to SubStream can be extracted from Parent streams which already
    contain 1st page of needed items. Thus, it significantly decreases a number of requests needed to get
    all item in parent stream, since parent stream returns 100 items per request.
    Note, in major cases, pagination requests are not performed because sub items are fully reported in parent streams

    For example:
    Line items are part of each 'invoice' record, so use Invoices stream because
    it allows bulk extraction:
        0.1.28 and below - 1 request extracts line items for 1 invoice (+ pagination reqs)
        0.1.29 and above - 1 request extracts line items for 100 invoices (+ pagination reqs)

    if line items object has indication for next pages ('has_more' attr)
    then use current stream to extract next pages. In major cases pagination requests
    are not performed because line items are fully reported in 'invoice' record

    Example for InvoiceLineItems and parent Invoice streams, record from Invoice stream:
        {
          "created": 1641038947,    <--- 'Invoice' record
          "customer": "cus_HezytZRkaQJC8W",
          "id": "in_1KD6OVIEn5WyEQxn9xuASHsD",    <---- value for 'parent_id' attribute
          "object": "invoice",
          "total": 0,
          ...
          "lines": {    <---- sub_items_attr
            "data": [
              {
                "id": "il_1KD6OVIEn5WyEQxnm5bzJzuA",    <---- 'Invoice' line item record
                "object": "line_item",
                ...
              },
              {...}
            ],
            "has_more": false,    <---- next pages from 'InvoiceLineItemsPaginated' stream
            "object": "list",
            "total_count": 2,
            "url": "/v1/invoices/in_1KD6OVIEn5WyEQxn9xuASHsD/lines"
          }
        }
    """

    filter: Optional[Mapping[str, Any]] = None
    add_parent_id: bool = False

    @property
    @abstractmethod
    def parent(self) -> Type[StripeStream]:
        """
        :return: parent stream which contains needed records in <sub_items_attr>
        """

    @property
    @abstractmethod
    def parent_id(self) -> str:
        """
        :return: string with attribute name
        """

    @property
    @abstractmethod
    def sub_items_attr(self) -> str:
        """
        :return: string if single primary key, list of strings if composite primary key, list of list of strings if composite primary key consisting of nested fields.
          If the stream has no primary keys, return None.
        """

    @property
    def availability_strategy(self) -> Optional[AvailabilityStrategy]:
        return StripeSubStreamAvailabilityStrategy()

    def request_params(self, stream_slice: Mapping[str, Any] = None, **kwargs):
        params = super().request_params(stream_slice=stream_slice, **kwargs)

        # add 'starting_after' param
        if not params.get("starting_after") and stream_slice and stream_slice.get("starting_after"):
            params["starting_after"] = stream_slice["starting_after"]

        return params

    def get_parent_stream_instance(self):
        return self.parent(authenticator=self.authenticator, account_id=self.account_id, start_date=self.start_date)

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        parent_stream = self.get_parent_stream_instance()
        slices = parent_stream.stream_slices(sync_mode=SyncMode.full_refresh)
        for _slice in slices:
            yield from parent_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=_slice)

    def read_records(self, sync_mode: SyncMode, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        parent_record = stream_slice
        items_obj = parent_record.get(self.sub_items_attr, {})
        if not items_obj:
            return

        items = items_obj.get("data", [])
        if self.filter:
            items = [i for i in items if i.get(self.filter["attr"]) == self.filter["value"]]

        # get next pages
        items_next_pages = []
        if items_obj.get("has_more") and items:
            stream_slice = {self.parent_id: parent_record["id"], "starting_after": items[-1]["id"]}
            items_next_pages = super().read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice, **kwargs)

        for item in chain(items, items_next_pages):
            if self.add_parent_id:
                # add reference to parent object when item doesn't have it already
                item[self.parent_id] = parent_record["id"]
            yield item


class ApplicationFees(IncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/application_fees
    """

    cursor_field = "created"

    def path(self, **kwargs):
        return "application_fees"


class ApplicationFeesRefunds(StripeSubStream):
    """
    API docs: https://stripe.com/docs/api/fee_refunds/list
    """

    name = "application_fees_refunds"

    parent = ApplicationFees
    parent_id: str = "refund_id"
    sub_items_attr = "refunds"
    add_parent_id = True

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs):
        return f"application_fees/{stream_slice[self.parent_id]}/refunds"


class Invoices(IncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/invoices/list
    """

    cursor_field = "created"

    def path(self, **kwargs):
        return "invoices"


class InvoiceLineItems(StripeSubStream):
    """
    API docs: https://stripe.com/docs/api/invoices/invoice_lines
    """

    name = "invoice_line_items"

    parent = Invoices
    parent_id: str = "invoice_id"
    sub_items_attr = "lines"
    add_parent_id = True

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs):
        return f"invoices/{stream_slice[self.parent_id]}/lines"


class InvoiceItems(IncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/invoiceitems/list
    """

    cursor_field = "date"
    name = "invoice_items"

    def path(self, **kwargs):
        return "invoiceitems"


class Payouts(IncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/payouts/list
    """

    cursor_field = "created"

    def path(self, **kwargs):
        return "payouts"


class Plans(IncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/plans/list
    """

    cursor_field = "created"

    def path(self, **kwargs):
        return "plans"

    def request_params(self, stream_slice: Mapping[str, Any] = None, **kwargs):
        params = super().request_params(stream_slice=stream_slice, **kwargs)
        params["expand[]"] = ["data.tiers"]
        return params


class Products(IncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/products/list
    """

    cursor_field = "created"

    def path(self, **kwargs):
        return "products"


class Reviews(IncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/radar/reviews/list
    """

    cursor_field = "created"

    def path(self, **kwargs):
        return "reviews"


class Subscriptions(IncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/subscriptions/list
    """

    use_cache = True
    cursor_field = "created"
    status = "all"

    def path(self, **kwargs):
        return "subscriptions"

    def request_params(self, stream_state=None, **kwargs):
        stream_state = stream_state or {}
        params = super().request_params(stream_state=stream_state, **kwargs)
        params["status"] = self.status
        return params


class SubscriptionItems(StripeSubStream):
    """
    API docs: https://stripe.com/docs/api/subscription_items/list
    """

    use_cache = True

    name = "subscription_items"

    parent: StripeStream = Subscriptions
    parent_id: str = "subscription_id"
    sub_items_attr: str = "items"

    def path(self, **kwargs):
        return "subscription_items"

    def request_params(self, stream_slice: Mapping[str, Any] = None, **kwargs):
        params = super().request_params(stream_slice=stream_slice, **kwargs)
        params["subscription"] = stream_slice[self.parent_id]
        return params


class SubscriptionSchedule(IncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/subscription_schedules
    """

    cursor_field = "created"

    def path(self, **kwargs):
        return "subscription_schedules"


class Transfers(IncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/transfers/list
    """
    use_cache = True
    cursor_field = "created"

    def path(self, **kwargs):
        return "transfers"


class Refunds(IncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/refunds/list
    """

    cursor_field = "created"

    def path(self, **kwargs):
        return "refunds"


class PaymentIntents(IncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/payment_intents/list
    """

    cursor_field = "created"

    def path(self, **kwargs):
        return "payment_intents"


class PaymentMethods(StripeStream):
    """
    API docs: https://stripe.com/docs/api/payment_methods/list
    """

    def path(self, **kwargs):
        return "payment_methods"


class BankAccounts(StripeSubStream):
    """
    API docs: https://stripe.com/docs/api/customer_bank_accounts/list
    """

    name = "bank_accounts"

    parent = Customers
    parent_id = "customer_id"
    sub_items_attr = "sources"
    filter = {"attr": "object", "value": "bank_account"}

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs):
        return f"customers/{stream_slice[self.parent_id]}/sources"

    def request_params(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(stream_slice=stream_slice, **kwargs)
        params["object"] = "bank_account"
        return params


class CheckoutSessions(IncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/checkout/sessions/list
    """

    name = "checkout_sessions"

    cursor_field = "expires_at"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # https://stripe.com/docs/api/checkout/sessions/create#create_checkout_session-expires_at
        # 'expires_at' - can be anywhere from 1 to 24 hours after Checkout Session creation.
        # thus we should always add 1 day to lookback window to avoid possible checkout_sessions losses
        self.lookback_window_days = self.lookback_window_days + 1

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        yield from [{}]

    def path(self, **kwargs):
        return "checkout/sessions"

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping]:
        since_date = self.get_start_timestamp(stream_state)
        for item in super().parse_response(response, **kwargs):
            # Filter out too old items
            expires_at = item.get(self.cursor_field)
            if expires_at and expires_at > since_date:
                yield item


class CheckoutSessionsLineItems(IncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/checkout/sessions/line_items
    """

    name = "checkout_sessions_line_items"

    cursor_field = "checkout_session_expires_at"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # https://stripe.com/docs/api/checkout/sessions/create#create_checkout_session-expires_at
        # 'expires_at' - can be anywhere from 1 to 24 hours after Checkout Session creation.
        # thus we should always add 1 day to lookback window to avoid possible checkout_sessions losses
        self.lookback_window_days = self.lookback_window_days + 1

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs):
        return f"checkout/sessions/{stream_slice['checkout_session_id']}/line_items"

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        checkout_session_state = None
        if stream_state:
            checkout_session_state = {"expires_at": stream_state["checkout_session_expires_at"]}
        checkout_session_stream = CheckoutSessions(authenticator=self.authenticator, account_id=self.account_id, start_date=self.start_date)
        for checkout_session in checkout_session_stream.read_records(
            sync_mode=SyncMode.full_refresh, stream_state=checkout_session_state, stream_slice={}
        ):
            yield {
                "checkout_session_id": checkout_session["id"],
                "expires_at": checkout_session["expires_at"],
            }

    def request_params(self, stream_slice: Mapping[str, Any] = None, **kwargs):
        params = super().request_params(stream_slice=stream_slice, **kwargs)
        params["expand[]"] = ["data.discounts", "data.taxes"]
        return params

    @property
    def raise_on_http_errors(self):
        return False

    def parse_response(self, response: requests.Response, stream_slice: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping]:
        if response.status_code == 404:
            self.logger.warning(response.json())
            return
        response.raise_for_status()

        response_json = response.json()
        data = response_json.get("data", [])
        if data and stream_slice:
            self.logger.info(f"stream_slice: {stream_slice}")
            cs_id = stream_slice.get("checkout_session_id", None)
            cs_expires_at = stream_slice.get("expires_at", None)
            for e in data:
                e["checkout_session_id"] = cs_id
                e["checkout_session_expires_at"] = cs_expires_at
        yield from data


class PromotionCodes(IncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/promotion_codes/list
    """

    cursor_field = "created"

    def path(self, **kwargs):
        return "promotion_codes"


class ExternalAccount(BasePaginationStripeStream, ABC):
    """
    Bank Accounts and Cards are separate streams because they have different schemas
    """

    object = ""

    def path(self, **kwargs):
        return f"accounts/{self.account_id}/external_accounts"

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        yield from [{}]

    def request_params(self, **kwargs):
        params = super().request_params(**kwargs)
        return {**params, **{"object": self.object}}


class ExternalAccountBankAccounts(ExternalAccount):
    """
    https://stripe.com/docs/api/external_account_bank_accounts/list
    """

    object = "bank_account"


class ExternalAccountCards(ExternalAccount):
    """
    https://stripe.com/docs/api/external_account_cards/list
    """

    object = "card"


class SetupIntents(IncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/setup_intents/list
    """

    cursor_field = "created"

    def path(self, **kwargs):
        return "setup_intents"


class Accounts(BasePaginationStripeStream):
    """
    Docs: https://stripe.com/docs/api/accounts/list
    Even the endpoint allow to filter based on created the data usually don't have this field.
    """

    def path(self, **kwargs):
        return "accounts"


class Cards(IncrementalStripeStream):
    """
    Docs: https://stripe.com/docs/api/issuing/cards/list
    """

    cursor_field = "created"

    def path(self, **kwargs):
        return "issuing/cards"


class TopUps(IncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/topups/list
    """

    name = "top_ups"
    cursor_field = "created"

    def path(self, **kwargs) -> str:
        return "topups"


class Files(IncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/files/list
    """

    name = "files"
    cursor_field = "created"

    def path(self, **kwargs) -> str:
        return "files"


class FileLinks(IncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/file_links/list
    """

    name = "file_links"
    cursor_field = "created"

    def path(self, **kwargs) -> str:
        return "file_links"


class SetupAttempts(IncrementalStripeStream, HttpSubStream):
    """
    Docs: https://stripe.com/docs/api/setup_attempts/list
    """

    cursor_field = "created"

    def __init__(self, **kwargs):
        parent = SetupIntents(**kwargs)
        super().__init__(parent=parent, **kwargs)

    def path(self, **kwargs) -> str:
        return "setup_attempts"

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        incremental_slices = list(
            IncrementalStripeStream.stream_slices(self, sync_mode=sync_mode, cursor_field=cursor_field, stream_state=stream_state)
        )
        if incremental_slices:
            parent_records = HttpSubStream.stream_slices(self, sync_mode=sync_mode, cursor_field=cursor_field, stream_state=stream_state)
            yield from (slice | rec for rec in parent_records for slice in incremental_slices)
        else:
            yield None

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        setup_intent_id = stream_slice.get("parent", {}).get("id")
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        params.update(setup_intent=setup_intent_id)
        return params


class UsageRecords(StripeStream, HttpSubStream):
    """
    Docs: https://stripe.com/docs/api/usage_records/subscription_item_summary_list
    """

    primary_key = None

    def __init__(self, **kwargs):
        parent = SubscriptionItems(**kwargs)
        super().__init__(parent=parent, **kwargs)

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        subscription_item_id = stream_slice.get("parent", {}).get("id")
        return f"subscription_items/{subscription_item_id}/usage_record_summaries"


class TransferReversals(StripeStream, HttpSubStream):
    """
    Docs: https://stripe.com/docs/api/transfer_reversals/list
    """

    def __init__(self, **kwargs):
        parent = Transfers(**kwargs)
        super().__init__(parent=parent, **kwargs)

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        transfer_id = stream_slice.get("parent", {}).get("id")
        return f"transfers/{transfer_id}/reversals"


class Transactions(IncrementalStripeStream):
    """
    Docs: https://stripe.com/docs/api/issuing/transactions/list
    """

    cursor_field = "created"

    def path(self, **kwargs) -> str:
        return "issuing/transactions"
