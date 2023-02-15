#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import math
from abc import ABC, abstractmethod
from itertools import chain
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
import uuid
import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams import IncrementalMixin
from datetime import datetime

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
    NOW_TIMESTAMP = pendulum.now().int_timestamp
    def __init__(self, start_date: int, account_id: str, slice_range: int = DEFAULT_SLICE_RANGE, **kwargs):
        super().__init__(**kwargs)
        self.account_id = account_id
        self.start_date = start_date
        self.slice_range = slice_range or self.DEFAULT_SLICE_RANGE

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        decoded_response = response.json()
        if bool(decoded_response.get("has_more", "False")) and decoded_response.get("data", []):
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
        for key in ("created[gte]", "created[lte]"):
            if key in stream_slice:
                params[key] = stream_slice[key]

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

    def chunk_dates(self, start_date_ts: int) -> Iterable[Tuple[int, int]]:
        now = self.NOW_TIMESTAMP
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


class SingleEmptySliceMixin(object):
    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        return [{}]


class IncrementalStripeStream(StripeStream, ABC):
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
        if start_ts >= self.NOW_TIMESTAMP:
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

class IncrementalStripeStreamWithUpdates(IncrementalStripeStream):
    """
        This is a base class for incremental streams that support updates using the events API
        In first sync it will not get any updates as the records are already updated
        After first sync it will get all updates starting from date of the last sync
    """
    event_types = None
    update_field = "event_created"
    state_lastSync_key = "lastSync"
    state_completed_key = "completed"
    completed = False
    last_stream_slice = None
    last_record = None
    def isLastSlice(self,currentSlice):
        return self.last_stream_slice == currentSlice
    def setLastSlice(self,stream_state):
        if(self.last_stream_slice==None):
            *_, last = self.stream_slices(sync_mode='incremental', stream_state=stream_state)
            self.last_stream_slice = last

    def lookahead(self,stream_slice, iterable):
        """Pass through all values from the given iterable, to check
        if there are more values to come after the current one,
        or if it is the last value. Helps to define in the last state the completed flag. 
        """
        # Get an iterator and pull the first value.
        it = iter(iterable)
        last = next(it, None)
        if not last:
            if self.last_record and self.completed == False:
                self.completed = True
                yield self.last_record
            return
        # Run the iterator to exhaustion (starting from the second value).
        for val in it:
            yield last
            last = val
        if self.isLastSlice(stream_slice):
            self.completed = True
        self.last_record = last
        yield last

    def shouldFetchFromOriginalResource (self,stream_state = None):
        durationInDaysFromLastSync = 0
        hasState = bool(stream_state)
        self.completed = stream_state and stream_state.get(self.state_completed_key) or False
        if hasState and self.completed:
            then = datetime.fromtimestamp(stream_state.get(self.state_lastSync_key)) 
            now  = datetime.utcnow()
            duration = now - then
            durationInDaysFromLastSync = duration.days
        # If last state is not present or the main sync didn't complete or the last sync was more than 30 days ago
        # Fetch data from original stream else fetch data from events
        shouldResetState = durationInDaysFromLastSync >= 30
        return hasState == False or self.completed is False or shouldResetState
    def read_records(self, stream_slice, stream_state = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        shouldFetchFromOriginalResource = self.shouldFetchFromOriginalResource(stream_state)
        if shouldFetchFromOriginalResource:
            self.logger.info("Fetching from original source")
            self.setLastSlice(stream_state)
            self.completed = False
            yield from self.lookahead(stream_slice, super().read_records(stream_slice=stream_slice, stream_state=None, **kwargs))
        else:
            self.logger.info("Fetching from events")
            yield from self.get_updates(stream_state, **kwargs)

    def get_updates(self, stream_state, **kwargs)-> Iterable[Mapping[str, Any]]:
        update_stream = Updates(event_types=self.event_types, authenticator=self.authenticator, account_id=self.account_id, start_date=self.start_date)
        slice = update_stream.stream_slices(sync_mode="incremental", stream_state=stream_state)
        for _slice in slice:
            for event in update_stream.read_records(stream_slice=_slice,stream_state=stream_state, **kwargs):
                self.set_record_id(event)
                yield event

    def set_record_id(self, record):
        """
         Sets the primary_key of the record to a new field (i.e. {subscription_id: "..."}) and replace
         the actual id with a unique value
        """
        record["record_id"] = record[self.primary_key]
        # Change the original id to random uuid to avoid warehouse deduplication
        record[self.primary_key] = uuid.uuid1()

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        for item in super().parse_response(response, **kwargs):
            if item.get(self.update_field) is None:
                # set event_created as the cursor field value in case it is not set 
                item[self.update_field] = item[self.cursor_field]
                self.set_record_id(item)
            yield item

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        streamState = max(latest_record.get(self.cursor_field), current_stream_state.get(self.cursor_field, 0))
        # We set the state for updates to current time
        lastSyncAt = pendulum.now().int_timestamp
        if self.completed:
            # If the main sync is completed we use the event created to store events state
            updateState = max(latest_record.get(self.update_field), current_stream_state.get(self.update_field, 0))
        else:
            # If the main sync is not completed we get events from the beginning to ensure no data loss
            updateState = 0
        latestState  = { self.update_field:updateState, self.cursor_field: streamState, self.state_completed_key: self.completed, self.state_lastSync_key:lastSyncAt }
        return latestState

class Customers(IncrementalStripeStreamWithUpdates):
    """
    API docs: https://stripe.com/docs/api/customers/list
    """
    event_types = ["customer.created", "customer.updated"]
    cursor_field = "created"

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


class Charges(IncrementalStripeStreamWithUpdates):
    """
    API docs: https://stripe.com/docs/api/charges/list
    """
    event_types = ["charge.created","charge.updated"]
    cursor_field = "created"

    def path(self, **kwargs) -> str:
        return "charges"


class CustomerBalanceTransactions(SingleEmptySliceMixin, StripeStream):
    """
    API docs: https://stripe.com/docs/api/customer_balance_transactions/list
    """

    name = "customer_balance_transactions"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs):
        customer_id = stream_slice["customer_id"]
        return f"customers/{customer_id}/balance_transactions"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        customers_stream = Customers(authenticator=self.authenticator, account_id=self.account_id, start_date=self.start_date)
        slices = customers_stream.stream_slices(sync_mode=SyncMode.full_refresh)
        for _slice in slices:
            for customer in customers_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=_slice):
                yield from super().read_records(stream_slice={"customer_id": customer["record_id"]}, **kwargs)


class Coupons(IncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/coupons/list
    """

    cursor_field = "created"

    def path(self, **kwargs):
        return "coupons"


class Disputes(IncrementalStripeStreamWithUpdates):
    """
    API docs: https://stripe.com/docs/api/disputes/list
    """
    event_types = ["charge.dispute.created", "charge.dispute.updated"]
    cursor_field = "created"

    def path(self, **kwargs):
        return "disputes"


class Events(IncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/events/list
    """

    cursor_field = "created"

    def path(self, **kwargs):
        return "events"

class Updates(Events):
    """
    A class for getting updated records using the event stream
    """
    cursor_field = "event_created"
    def __init__(self, event_types=None, **kwargs):
        super().__init__(**kwargs)
        # event_types defines the types of the events that will be used to fetch the specified updated
        # example: event_types = "subscription.updated" will be used for the Charges stream
        if not event_types:
            raise Exception("event_types is required for the Updates stream")
        self.event_types = event_types

    def request_params(self, stream_slice: Mapping[str, Any] = None, **kwargs):
        params = super().request_params(stream_slice=stream_slice, **kwargs)
        if self.event_types:
            params["types[]"] = self.event_types
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        for event in super().parse_response(response, **kwargs):
            # The actual record exist in the data object
            # example {"object": "event","data": {"object": {...} } }
            eventData = event.get("data",{}).get("object",{})
            # Add event_created field to the record using the created date of the event
            eventData[self.cursor_field] = event.get("created")
            yield eventData

class StripeSubStream(SingleEmptySliceMixin, StripeStream, ABC):
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
    def parent(self) -> StripeStream:
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

    def request_params(self, stream_slice: Mapping[str, Any] = None, **kwargs):
        params = super().request_params(stream_slice=stream_slice, **kwargs)

        # add 'starting_after' param
        if not params.get("starting_after") and stream_slice and stream_slice.get("starting_after"):
            params["starting_after"] = stream_slice["starting_after"]

        return params

    def read_records(self, sync_mode: SyncMode, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        parent_stream = self.parent(authenticator=self.authenticator, account_id=self.account_id, start_date=self.start_date)
        slices = parent_stream.stream_slices(sync_mode=SyncMode.full_refresh)
        for _slice in slices:
            for record in parent_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=_slice):

                items_obj = record.get(self.sub_items_attr, {})
                if not items_obj:
                    continue

                items = items_obj.get("data", [])

                # non-generic filter, mainly for BankAccounts stream only
                if self.filter:
                    items = [i for i in items if i.get(self.filter["attr"]) == self.filter["value"]]

                # get next pages
                items_next_pages = []
                if items_obj.get("has_more") and items:
                    stream_slice = {self.parent_id: record["record_id"], "starting_after": items[-1]["id"]}
                    items_next_pages = super().read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice, **kwargs)

                for item in chain(items, items_next_pages):
                    if self.add_parent_id:
                        # add reference to parent object when item doesn't have it already
                        item[self.parent_id] = record["record_id"]
                    yield item


class Invoices(IncrementalStripeStreamWithUpdates):
    """
    API docs: https://stripe.com/docs/api/invoices/list
    """
    event_types = ["invoice.created", "invoice.updated"]
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


class InvoiceItems(IncrementalStripeStreamWithUpdates):
    """
    API docs: https://stripe.com/docs/api/invoiceitems/list
    """
    event_types = ["invoiceitem.created", "invoiceitem.updated"]
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


class Plans(IncrementalStripeStreamWithUpdates):
    """
    API docs: https://stripe.com/docs/api/plans/list
    """
    event_types = ["plan.created", "plan.updated"]
    cursor_field = "created"

    def path(self, **kwargs):
        return "plans"


class Products(IncrementalStripeStreamWithUpdates):
    """
    API docs: https://stripe.com/docs/api/products/list
    """

    event_types = ["product.created", "product.updated"]
    cursor_field = "created"

    def path(self, **kwargs):
        return "products"


class Subscriptions(IncrementalStripeStreamWithUpdates):
    """
    API docs: https://stripe.com/docs/api/subscriptions/list
    """
    event_types = ["customer.subscription.created", "customer.subscription.updated"]
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


class Transfers(IncrementalStripeStreamWithUpdates):
    """
    API docs: https://stripe.com/docs/api/transfers/list
    """
    event_types = ["transfer.created", "transfer.updated"]
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


class CheckoutSessions(SingleEmptySliceMixin, IncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/checkout/sessions/list
    """

    name = "checkout_sessions"

    cursor_field = "expires_at"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # https://stripe.com/docs/api/checkout/sessions/create#create_checkout_session-expires_at
        # 'expires_at' - can be anywhere from 1 to 24 hours after Checkout Session creation.
        # thus we should always add 1 day to lookback window to avoid possible checkout_sessions losses
        self.lookback_window_days = self.lookback_window_days + 1

    def path(self, **kwargs):
        return "checkout/sessions"

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping]:
        since_date = self.get_start_timestamp(stream_state)
        for item in super().parse_response(response, **kwargs):
            # Filter out too old items
            expires_at = item.get(self.cursor_field)
            if expires_at and expires_at > since_date:
                yield item


class CheckoutSessionsLineItems(SingleEmptySliceMixin, IncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/checkout/sessions/line_items
    """

    name = "checkout_sessions_line_items"

    cursor_field = "checkout_session_expires_at"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # https://stripe.com/docs/api/checkout/sessions/create#create_checkout_session-expires_at
        # 'expires_at' - can be anywhere from 1 to 24 hours after Checkout Session creation.
        # thus we should always add 1 day to lookback window to avoid possible checkout_sessions losses
        self.lookback_window_days = self.lookback_window_days + 1

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs):
        return f"checkout/sessions/{stream_slice['checkout_session_id']}/line_items"

    def read_records(
        self, stream_slice: Optional[Mapping[str, Any]] = None, stream_state: Mapping[str, Any] = None, **kwargs
    ) -> Iterable[Mapping[str, Any]]:
        checkout_session_stream = CheckoutSessions(authenticator=self.authenticator, account_id=self.account_id, start_date=self.start_date)

        checkout_session_state = None
        if stream_state:
            checkout_session_state = {"expires_at": stream_state["checkout_session_expires_at"]}

        for checkout_session in checkout_session_stream.read_records(
            sync_mode=SyncMode.full_refresh, stream_state=checkout_session_state, stream_slice={}
        ):
            stream_slice = {
                "checkout_session_id": checkout_session["id"],
                "expires_at": checkout_session["expires_at"],
            }
            yield from super().read_records(stream_slice=stream_slice, **kwargs)

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


class ExternalAccount(SingleEmptySliceMixin, StripeStream, ABC):
    """
    Bank Accounts and Cards are separate streams because they have different schemas
    """

    object = ""

    def path(self, **kwargs):
        return f"accounts/{self.account_id}/external_accounts"

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
