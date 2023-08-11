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
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from source_stripe.availability_strategy import StripeAvailabilityStrategy, StripeSubStreamAvailabilityStrategy

STRIPE_API_VERSION = "2022-11-15"


class StripeStream(HttpStream, ABC):
    url_base = "https://api.stripe.com/v1/"
    primary_key = "id"
    extra_request_params = {}
    DEFAULT_SLICE_RANGE = 365
    transformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)

    @property
    def availability_strategy(self) -> Optional[AvailabilityStrategy]:
        return StripeAvailabilityStrategy()

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
        params = {"limit": 100, **self.extra_request_params}
        # Handle pagination by inserting the next page's token in the request parameters
        if next_page_token:
            params.update(next_page_token)

        return params

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        headers = {"Stripe-Version": STRIPE_API_VERSION}
        if self.account_id:
            headers["Stripe-Account"] = self.account_id
        return headers

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        yield from response_json.get("data", [])  # Stripe puts records in a container array "data"


class NormalIncrementalStripeStream(StripeStream, ABC):
    # Stripe returns most recently created objects first, so we don't want to persist state until the entire stream has been read
    state_checkpoint_interval = math.inf
    cursor_field = "created"

    def __init__(self, *args, lookback_window_days: int = 0, **kwargs):
        super().__init__(*args, **kwargs)
        self.lookback_window_days = lookback_window_days

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        state_cursor_value = self.get_state_cursor_value(current_stream_state)
        latest_record_value = latest_record.get(self.cursor_field)
        return {self.cursor_field: max(latest_record_value, state_cursor_value)}

    def request_params(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        return {"created[gte]": stream_slice["created[gte]"], "created[lte]": stream_slice["created[lte]"], **params}

    def chunk_dates(self, start_date_ts: int) -> Iterable[Tuple[int, int]]:
        now = pendulum.now().int_timestamp
        step = int(pendulum.duration(days=self.slice_range).total_seconds())
        after_ts = start_date_ts
        while after_ts < now:
            before_ts = min(now, after_ts + step)
            yield after_ts, before_ts
            after_ts = before_ts + 1

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        stream_state = stream_state or {}
        start_ts = self.get_start_timestamp(stream_state)
        if start_ts >= pendulum.now().int_timestamp:
            return []
        for start, end in self.chunk_dates(start_ts):
            yield {"created[gte]": start, "created[lte]": end}

    def get_state_cursor_value(self, stream_state) -> int:
        return stream_state.get(self.cursor_field, 0)

    def get_start_timestamp(self, stream_state) -> int:
        start_point = self.start_date
        start_point = max(start_point, self.get_state_cursor_value(stream_state))

        if start_point and self.lookback_window_days:
            self.logger.info(f"Applying lookback window of {self.lookback_window_days} days to stream {self.name}")
            start_point = int(pendulum.from_timestamp(start_point).subtract(days=abs(self.lookback_window_days)).timestamp())

        return start_point


class Events(NormalIncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/events/list
    """

    def path(self, **kwargs):
        return "events"


class EventProxy(Events):
    """
    This is an auxiliary class to read incremental data from the Events API.
    Not designed to be exposed to the end user.
    """

    cursor_field = "updated"

    def __init__(self, *args, legacy_cursor_field: str, event_types: Optional[Iterable[str]] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_types = event_types
        self.legacy_cursor_field = legacy_cursor_field

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        # set the record updated date = date of event creation
        for instance in response_json.get("data", []):
            record = instance["data"]["object"]
            record["updated"] = instance["created"]
            yield record

    def get_state_cursor_value(self, stream_state) -> int:
        return stream_state.get(self.cursor_field, stream_state.get(self.legacy_cursor_field, 0))

    def request_params(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        if self.event_types:
            params["types[]"] = self.event_types
        return params


class EventIncrementalStripeStream(StripeStream, ABC):
    """
    Normal incremental stream does not provide a way to read updated data since given date because the API does not allow to do this.
    It only returns newly created entities since given date. So to have all the updated data as well we need to make use of the Events API,
    which allows to retrieve updated data since given date for a number of predefined events which are associated with the corresponding
    entities.
    """

    cursor_field = "updated"
    legacy_cursor_field = "created"

    @property
    @abstractmethod
    def event_types(self) -> Iterable[str]:
        """A list of event types that are associated with entity."""

    def __init__(self, *args, lookback_window_days: int = 0, **kwargs):
        super().__init__(*args, **kwargs)
        self.lookback_window_days = lookback_window_days
        self.events_stream = EventProxy(
            authenticator=self.authenticator,
            lookback_window_days=self.lookback_window_days,
            account_id=self.account_id,
            start_date=self.start_date,
            slice_range=self.slice_range,
            event_types=self.event_types,
            legacy_cursor_field=self.legacy_cursor_field,
        )

    def get_state_cursor_value(self, stream_state) -> int:
        # support for both legacy and new cursor fields
        return stream_state.get(self.cursor_field, stream_state.get(self.legacy_cursor_field, 0))

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        latest_record_value = latest_record.get(self.cursor_field)
        state_value = self.get_state_cursor_value(current_stream_state)
        return {self.cursor_field: max(latest_record_value, state_value)}

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        # When reading from a stream, a `read_records` is called once per slice.
        # We yield a single slice here because we don't want to make duplicate calls for event based incremental syncs.
        yield {}

    def read_event_increments(
        self, cursor_field: Optional[List[str]] = None, stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[StreamData]:
        for event_slice in self.events_stream.stream_slices(
            sync_mode=SyncMode.incremental, cursor_field=cursor_field, stream_state=stream_state
        ):
            yield from self.events_stream.read_records(
                SyncMode.incremental, cursor_field=cursor_field, stream_slice=event_slice, stream_state=stream_state
            )

    @classmethod
    def set_updated_timestamp(cls, records: Iterable[MutableMapping]) -> Iterable[MutableMapping]:
        for record in records:
            # need to fill in the `updated` timestamp for consistency
            if "updated" not in record:
                record["updated"] = record[cls.legacy_cursor_field]
            yield record

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        if not stream_state:
            # both full refresh and initial incremental sync should use usual endpoints
            yield from self.set_updated_timestamp(
                super().read_records(sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state)
            )
            return
        yield from self.read_event_increments(cursor_field=cursor_field, stream_state=stream_state)


class SlicedEventIncrementalStripeStream(EventIncrementalStripeStream, NormalIncrementalStripeStream, ABC):
    """
    This class combines both normal incremental sync and event based sync. It uses common endpoints for sliced data syncs in
    the full refresh sync mode and initial incremental sync. For incremental syncs with a state, event based sync comes into action.
    """

    cursor_field = "updated"

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        parent = EventIncrementalStripeStream if stream_state else NormalIncrementalStripeStream
        return parent.stream_slices(self, sync_mode, cursor_field=cursor_field, stream_state=stream_state)

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        parent_read_records = EventIncrementalStripeStream.read_records if stream_state else NormalIncrementalStripeStream.read_records
        parent_records = parent_read_records(
            self, sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
        )
        if not stream_state:
            parent_records = self.set_updated_timestamp(parent_records)
        yield from parent_records


class Authorizations(SlicedEventIncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/issuing/authorizations/list
    """

    event_types = ["issuing_authorization.created", "issuing_authorization.request", "issuing_authorization.updated"]

    def path(self, **kwargs) -> str:
        return "issuing/authorizations"


class Customers(SlicedEventIncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/customers/list
    """

    use_cache = True
    event_types = ["customer.created", "customer.updated"]

    def path(self, **kwargs) -> str:
        return "customers"


class BalanceTransactions(NormalIncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/balance_transactions/list
    """

    def path(self, **kwargs) -> str:
        return "balance_transactions"


class Cardholders(SlicedEventIncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/issuing/cardholders/list
    """

    event_types = ["issuing_cardholder.created", "issuing_cardholder.updated"]

    def path(self, **kwargs) -> str:
        return "issuing/cardholders"


class Charges(SlicedEventIncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/charges/list
    """

    extra_request_params = {"expand[]": ["data.refunds"]}
    event_types = [
        "charge.captured",
        "charge.expired",
        "charge.failed",
        "charge.pending",
        "charge.refunded",
        "charge.succeeded",
        "charge.updated",
    ]

    def path(self, **kwargs) -> str:
        return "charges"


class CustomerBalanceTransactions(StripeStream):
    """
    API docs: https://stripe.com/docs/api/customer_balance_transactions/list
    """

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs):
        return f"customers/{stream_slice['id']}/balance_transactions"

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
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


class Coupons(SlicedEventIncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/coupons/list
    """

    event_types = ["coupon.created", "coupon.updated"]

    def path(self, **kwargs):
        return "coupons"


class Disputes(SlicedEventIncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/disputes/list
    """

    event_types = [
        "charge.dispute.closed",
        "charge.dispute.created",
        "charge.dispute.funds_reinstated",
        "charge.dispute.funds_withdrawn",
        "charge.dispute.updated",
    ]

    def path(self, **kwargs):
        return "disputes"


class EarlyFraudWarnings(EventIncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/radar/early_fraud_warnings/list
    """

    event_types = ["radar.early_fraud_warning.created", "radar.early_fraud_warning.updated"]

    def path(self, **kwargs):
        return "radar/early_fraud_warnings"


class StripeLazySubStream(StripeStream, HttpSubStream, ABC):
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, parent=self.parent_cls(*args, **kwargs))

    @property
    @abstractmethod
    def parent_cls(self) -> Type[StripeStream]:
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

    def read_records(self, sync_mode: SyncMode, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        parent_record = stream_slice["parent"]
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


class EventIncrementalStripeLazySubStream(EventIncrementalStripeStream, StripeLazySubStream, ABC):
    """
    Identical to the `SlicedEventIncrementalStripeStream` class, this class defines how stateless syncs should be made
    using common endpoints on one hand (`StripeLazySubStream`),
    and stateful syncs - using event-based approach (`EventIncrementalStripeStream`) on the other.
    """

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        parent = StripeLazySubStream if not stream_state else EventIncrementalStripeStream
        return parent.stream_slices(self, sync_mode, cursor_field=cursor_field, stream_state=stream_state)

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        parent = StripeLazySubStream if not stream_state else EventIncrementalStripeStream
        yield from parent.read_records(self, sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state)


class EventIncrementalStripeSubStream(EventIncrementalStripeStream, HttpSubStream, ABC):
    """
    Identical to the `SlicedEventIncrementalStripeStream` class, this class defines how stateless syncs should be made
    using common endpoints on one hand (`HttpSubStream`),
    and stateful syncs - using event-based approach (`EventIncrementalStripeStream`) on the other.
    """

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        parent = HttpSubStream if not stream_state else EventIncrementalStripeStream
        return parent.stream_slices(self, sync_mode, cursor_field=cursor_field, stream_state=stream_state)


class ApplicationFees(SlicedEventIncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/application_fees
    """

    use_cache = True
    event_types = ["application_fee.created", "application_fee.refunded"]

    def path(self, **kwargs):
        return "application_fees"


class ApplicationFeesRefunds(EventIncrementalStripeLazySubStream):
    """
    API docs: https://stripe.com/docs/api/fee_refunds/list
    """

    event_types = ["application_fee.refund.updated"]

    parent_cls = ApplicationFees
    parent_id: str = "refund_id"
    sub_items_attr = "refunds"
    add_parent_id = True

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs):
        return f"application_fees/{stream_slice[self.parent_id]}/refunds"


class Invoices(SlicedEventIncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/invoices/list
    """

    use_cache = True
    event_types = [
        "invoice.created",
        "invoice.finalization_failed",
        "invoice.finalized",
        "invoice.marked_uncollectible",
        "invoice.paid",
        "invoice.payment_action_required",
        "invoice.payment_failed",
        "invoice.payment_succeeded",
        "invoice.sent",
        "invoice.upcoming",
        "invoice.updated",
        "invoice.voided",
    ]

    def path(self, **kwargs):
        return "invoices"


class InvoiceLineItems(StripeLazySubStream):
    """
    API docs: https://stripe.com/docs/api/invoices/invoice_lines
    """

    parent_cls = Invoices
    parent_id: str = "invoice_id"
    sub_items_attr = "lines"
    add_parent_id = True

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs):
        return f"invoices/{stream_slice[self.parent_id]}/lines"


class InvoiceItems(SlicedEventIncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/invoiceitems/list
    """

    legacy_cursor_field = "date"
    event_types = ["invoiceitem.created", "invoiceitem.updated"]

    def path(self, **kwargs):
        return "invoiceitems"


class Payouts(SlicedEventIncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/payouts/list
    """

    event_types = ["payout.canceled", "payout.created", "payout.failed", "payout.paid", "payout.reconciliation_completed", "payout.updated"]

    def path(self, **kwargs):
        return "payouts"


class Plans(SlicedEventIncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/plans/list
    """

    extra_request_params = {"expand[]": ["data.tiers"]}
    event_types = ["plan.created", "plan.updated"]

    def path(self, **kwargs):
        return "plans"


class Prices(SlicedEventIncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/prices/list
    """

    event_types = ["price.created", "price.updated"]

    def path(self, **kwargs):
        return "prices"


class Products(SlicedEventIncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/products/list
    """

    event_types = ["product.created", "product.updated"]

    def path(self, **kwargs):
        return "products"


class ShippingRates(NormalIncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/shipping_rates/list
    """

    def path(self, **kwargs):
        return "shipping_rates"


class Reviews(SlicedEventIncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/radar/reviews/list
    """

    event_types = ["review.closed", "review.opened"]

    def path(self, **kwargs):
        return "reviews"


class Subscriptions(SlicedEventIncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/subscriptions/list
    """

    use_cache = True
    extra_request_params = {"status": "all"}
    event_types = [
        "customer.subscription.created",
        "customer.subscription.paused",
        "customer.subscription.pending_update_applied",
        "customer.subscription.pending_update_expired",
        "customer.subscription.resumed",
        "customer.subscription.trial_will_end",
        "customer.subscription.updated",
    ]

    def path(self, **kwargs):
        return "subscriptions"


class SubscriptionItems(StripeLazySubStream):
    """
    API docs: https://stripe.com/docs/api/subscription_items/list
    """

    use_cache = True

    parent_cls: StripeStream = Subscriptions
    parent_id: str = "subscription_id"
    sub_items_attr: str = "items"

    def path(self, **kwargs):
        return "subscription_items"

    def request_params(self, stream_slice: Mapping[str, Any] = None, **kwargs):
        params = super().request_params(stream_slice=stream_slice, **kwargs)
        params["subscription"] = stream_slice[self.parent_id]
        return params


class SubscriptionSchedule(SlicedEventIncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/subscription_schedules
    """

    event_types = [
        "subscription_schedule.aborted",
        "subscription_schedule.canceled",
        "subscription_schedule.completed",
        "subscription_schedule.created",
        "subscription_schedule.expiring",
        "subscription_schedule.released",
        "subscription_schedule.updated",
    ]

    def path(self, **kwargs):
        return "subscription_schedules"


class Transfers(SlicedEventIncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/transfers/list
    """

    use_cache = True
    event_types = ["transfer.created", "transfer.reversed", "transfer.updated"]

    def path(self, **kwargs):
        return "transfers"


class Refunds(SlicedEventIncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/refunds/list
    """

    use_cache = True
    event_types = ["refund.created", "refund.updated"]

    def path(self, **kwargs):
        return "refunds"


class PaymentIntents(SlicedEventIncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/payment_intents/list
    """

    event_types = [
        "payment_intent.amount_capturable_updated",
        "payment_intent.canceled",
        "payment_intent.created",
        "payment_intent.partially_funded",
        "payment_intent.payment_failed",
        "payment_intent.processing",
        "payment_intent.requires_action",
        "payment_intent.succeeded",
    ]

    def path(self, **kwargs):
        return "payment_intents"


class PaymentMethods(EventIncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/payment_methods/list
    """

    event_types = ["payment_method.attached", "payment_method.automatically_updated", "payment_method.detached", "payment_method.updated"]

    def path(self, **kwargs):
        return "payment_methods"


class BankAccounts(EventIncrementalStripeLazySubStream):
    """
    API docs: https://stripe.com/docs/api/customer_bank_accounts/list
    """

    event_types = ["customer.source.created", "customer.source.expiring", "customer.source.updated"]

    parent_cls = Customers
    parent_id = "customer_id"
    sub_items_attr = "sources"
    filter = {"attr": "object", "value": "bank_account"}
    extra_request_params = {"object": "bank_account"}

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs):
        return f"customers/{stream_slice[self.parent_id]}/sources"

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        # need to filter out data here because it's not done in EventProxy
        for record in super().read_records(sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state):
            if record["object"] == "bank_account":
                yield record


class CheckoutSessions(SlicedEventIncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/checkout/sessions/list
    """

    use_cache = True
    legacy_cursor_field = "expires_at"

    event_types = [
        "checkout.session.async_payment_failed",
        "checkout.session.async_payment_succeeded",
        "checkout.session.completed",
        "checkout.session.expired",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # https://stripe.com/docs/api/checkout/sessions/create#create_checkout_session-expires_at
        # 'expires_at' - can be anywhere from 1 to 24 hours after Checkout Session creation.
        # thus we should always add 1 day to lookback window to avoid possible checkout_sessions losses
        self.lookback_window_days = self.lookback_window_days + 1

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        # override to not refer to slice values
        params = {"limit": 100}
        if next_page_token:
            params.update(next_page_token)
        return params

    def path(self, **kwargs):
        return "checkout/sessions"

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping]:
        since_date = self.get_start_timestamp(stream_state)
        records = self.set_updated_timestamp(super().parse_response(response, **kwargs))
        for item in records:
            # Filter out too old items as this is a semi-incremental sync
            expires_at = item.get(self.cursor_field)
            if expires_at and expires_at > since_date:
                yield item


class CheckoutSessionsLineItems(NormalIncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/checkout/sessions/line_items
    """

    extra_request_params = {"expand[]": ["data.discounts", "data.taxes"]}
    cursor_field = "checkout_session_expires_at"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # https://stripe.com/docs/api/checkout/sessions/create#create_checkout_session-expires_at
        # 'expires_at' - can be anywhere from 1 to 24 hours after Checkout Session creation.
        # thus we should always add 1 day to lookback window to avoid possible checkout_sessions losses
        self.lookback_window_days = self.lookback_window_days + 1

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs):
        return f"checkout/sessions/{stream_slice['checkout_session_id']}/line_items"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        # override to not refer to slice values
        params = {"limit": 100, **self.extra_request_params}
        if next_page_token:
            params.update(next_page_token)
        return params

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
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


class PromotionCodes(SlicedEventIncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/promotion_codes/list
    """

    event_types = ["promotion_code.created", "promotion_code.updated"]

    def path(self, **kwargs):
        return "promotion_codes"


class ExternalAccount(EventIncrementalStripeStream, ABC):
    """
    Bank Accounts and Cards are separate streams because they have different schemas
    """

    event_types = ["account.external_account.created", "account.external_account.updated"]

    @property
    @abstractmethod
    def object(self):
        pass

    @property
    def extra_request_params(self):
        return {"object": self.object}

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        # need to filter out data here because it's not done in EventProxy
        for record in super().read_records(sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state):
            if record["object"] == self.object:
                yield record

    def path(self, **kwargs):
        return f"accounts/{self.account_id}/external_accounts"


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


class SetupIntents(SlicedEventIncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/setup_intents/list
    """

    event_types = [
        "setup_intent.canceled",
        "setup_intent.created",
        "setup_intent.requires_action",
        "setup_intent.setup_failed",
        "setup_intent.succeeded",
    ]

    def path(self, **kwargs):
        return "setup_intents"


class Accounts(StripeStream):
    """
    Docs: https://stripe.com/docs/api/accounts/list
    Even the endpoint allow to filter based on created the data usually don't have this field.
    """

    use_cache = True

    # For some reason Stripe API does not return the `created` field in the response
    # for some records, therefore this stream does not support incremental syncs.

    def path(self, **kwargs):
        return "accounts"


class Persons(EventIncrementalStripeSubStream):
    """
    API docs: https://stripe.com/docs/api/persons/list
    """

    event_types = ["person.created", "person.updated"]

    def __init__(self, *args, lookback_window_days: int = 0, **kwargs):
        super().__init__(*args, parent=Accounts(*args, **kwargs), lookback_window_days=lookback_window_days, **kwargs)

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs):
        return f"accounts/{stream_slice['parent']['id']}/persons"


class CreditNotes(EventIncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/credit_notes/list
    """

    event_types = ["credit_note.created", "credit_note.updated", "credit_note.voided"]

    def path(self, **kwargs) -> str:
        return "credit_notes"


class Cards(SlicedEventIncrementalStripeStream):
    """
    Docs: https://stripe.com/docs/api/issuing/cards/list
    """

    event_types = ["issuing_card.created", "issuing_card.updated"]

    def path(self, **kwargs):
        return "issuing/cards"


class TopUps(SlicedEventIncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/topups/list
    """

    event_types = ["topup.canceled", "topup.created", "topup.failed", "topup.reversed", "topup.succeeded"]

    def path(self, **kwargs) -> str:
        return "topups"


class Files(NormalIncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/files/list
    """

    def path(self, **kwargs) -> str:
        return "files"


class FileLinks(NormalIncrementalStripeStream):
    """
    API docs: https://stripe.com/docs/api/file_links/list
    """

    def path(self, **kwargs) -> str:
        return "file_links"


class SetupAttempts(NormalIncrementalStripeStream, HttpSubStream):
    """
    Docs: https://stripe.com/docs/api/setup_attempts/list
    """

    def __init__(self, **kwargs):
        parent = SetupIntents(**kwargs)
        super().__init__(parent=parent, **kwargs)

    def path(self, **kwargs) -> str:
        return "setup_attempts"

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        # this is a unique combination of NormalIncrementalStripeStream and HttpSubStream,
        # so we need to have all the parent IDs multiplied by all the date slices
        incremental_slices = list(
            NormalIncrementalStripeStream.stream_slices(self, sync_mode=sync_mode, cursor_field=cursor_field, stream_state=stream_state)
        )
        if incremental_slices:
            parent_records = HttpSubStream.stream_slices(self, sync_mode=sync_mode, cursor_field=cursor_field, stream_state=stream_state)
            yield from (slice | rec for rec in parent_records for slice in incremental_slices)
        else:
            yield from []

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
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        transfer_id = stream_slice.get("parent", {}).get("id")
        return f"transfers/{transfer_id}/reversals"


class Transactions(SlicedEventIncrementalStripeStream):
    """
    Docs: https://stripe.com/docs/api/issuing/transactions/list
    """

    event_types = ["issuing_transaction.created", "issuing_transaction.updated"]

    def path(self, **kwargs) -> str:
        return "issuing/transactions"
