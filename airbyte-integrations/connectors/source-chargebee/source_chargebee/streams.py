#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

import pendulum
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from chargebee import APIError
from chargebee.list_result import ListResult
from chargebee.model import Model
from chargebee.models import Addon as AddonModel
from chargebee.models import AttachedItem as AttachedItemModel
from chargebee.models import Coupon as CouponModel
from chargebee.models import CreditNote as CreditNoteModel
from chargebee.models import Customer as CustomerModel
from chargebee.models import Event as EventModel
from chargebee.models import Invoice as InvoiceModel
from chargebee.models import Item as ItemModel
from chargebee.models import ItemPrice as ItemPriceModel
from chargebee.models import Order as OrderModel
from chargebee.models import Plan as PlanModel
from chargebee.models import Subscription as SubscriptionModel
from chargebee.models import Transaction as TransactionModel

from .rate_limiting import default_backoff_handler
from .utils import transform_custom_fields

# Backoff params below according to Chargebee's guidance on rate limit.
# https://apidocs.chargebee.com/docs/api?prod_cat_ver=2#api_rate_limits
MAX_TRIES = 10  # arbitrary max_tries
MAX_TIME = 90  # because Chargebee API enforce a per-minute limit


class ChargebeeStream(Stream):
    primary_key = "id"
    page_size = 100
    api: Model = None

    def next_page_token(self, list_result: ListResult) -> Optional[Mapping[str, Any]]:
        # Reference for Chargebee's pagination strategy below:
        # https://apidocs.chargebee.com/docs/api/#pagination_and_filtering
        if list_result:
            next_offset = list_result.next_offset
            if next_offset:
                return {"offset": next_offset}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {
            "limit": self.page_size,
        }

        if next_page_token:
            params.update(next_page_token)

        return params

    def parse_response(self, list_result: ListResult, **kwargs) -> Iterable[Mapping]:
        for message in list_result:
            yield from transform_custom_fields(message._response[self.name])

    @default_backoff_handler(max_tries=MAX_TRIES, factor=MAX_TIME)
    def _send_request(self, **kwargs) -> ListResult:
        """
        Just a wrapper to allow @backoff decorator
        Reference: https://apidocs.chargebee.com/docs/api/#error_codes_list
        """
        params = self.request_params(**kwargs)
        return self.api.list(params=params)

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """
        Override airbyte_cdk Stream's `read_records` method.
        """
        stream_state = stream_state or {}
        pagination_completed = False

        next_page_token = None
        while not pagination_completed:
            try:
                # Request the ListResult object from Chargebee with back-off implemented through self._send_request().
                list_result = self._send_request(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
            except APIError as e:
                self.logger.warn(str(e))
                break

            yield from self.parse_response(list_result=list_result, stream_state=stream_state, stream_slice=stream_slice)

            next_page_token = self.next_page_token(list_result)
            if not next_page_token:
                pagination_completed = True

        # Always return an empty generator just in case no records were ever yielded
        yield from []


class SemiIncrementalChargebeeStream(ChargebeeStream):
    """
    Semi incremental streams are also incremental but with one difference, they:
      - read all records;
      - output only new records.
    This means that semi incremental streams read all records (like full_refresh streams) but do filtering directly
    in the code and output only latest records (like incremental streams).
    """

    cursor_field = "updated_at"

    def __init__(self, start_date: str):
        # Convert `start_date` to timestamp(UTC).
        self._start_date = pendulum.parse(start_date).int_timestamp if start_date else None

    def get_starting_point(self, stream_state: Mapping[str, Any], item_id: str) -> int:
        start_point = self._start_date

        if stream_state and stream_state.get(item_id, {}).get(self.cursor_field):
            start_point = max(start_point, stream_state[item_id][self.cursor_field])

        return start_point

    def parse_response(
        self, list_result: ListResult, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Mapping]:
        starting_point = self.get_starting_point(stream_state=stream_state, item_id=stream_slice["item_id"])

        for message in list_result:
            record = message._response[self.name]
            if record[self.cursor_field] > starting_point:
                yield from transform_custom_fields(record)

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]):
        """
        Override airbyte_cdk Stream's `get_updated_state` method to get the latest Chargebee stream state.
        """
        item_id = latest_record.get("parent_item_id")
        latest_cursor_value = latest_record.get(self.cursor_field)
        current_stream_state = current_stream_state.copy()
        current_state = current_stream_state.get(item_id)
        if current_state:
            current_state = current_state.get(self.cursor_field)

        current_state_value = current_state or latest_cursor_value
        if current_state_value:
            max_value = max(current_state_value, latest_cursor_value)
            current_stream_state[item_id] = {self.cursor_field: max_value}
        return current_stream_state or {}


class IncrementalChargebeeStream(SemiIncrementalChargebeeStream):
    include_deleted = "true"

    @property
    def state_checkpoint_interval(self) -> int:
        return self.page_size

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)

        params["include_deleted"] = self.include_deleted
        params["sort_by[asc]"] = self.cursor_field

        start_point = self._start_date
        if stream_state:
            start_point = max(start_point, stream_state[self.cursor_field])

        if start_point:
            params[f"{self.cursor_field}[after]"] = start_point

        return params

    def parse_response(self, list_result: ListResult, **kwargs) -> Iterable[Mapping]:
        for message in list_result:
            yield from transform_custom_fields(message._response[self.name])

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]):
        """
        Override airbyte_cdk Stream's `get_updated_state` method to get the latest Chargebee stream state.
        """
        state_value = current_stream_state or {}

        latest_cursor_value = latest_record.get(self.cursor_field)

        if latest_cursor_value:
            state_value = {self.cursor_field: latest_cursor_value}

        return state_value


class Subscription(IncrementalChargebeeStream):
    """
    API docs: https://apidocs.chargebee.com/docs/api/subscriptions?prod_cat_ver=2#list_subscriptions
    """

    api = SubscriptionModel


class Customer(IncrementalChargebeeStream):
    """
    API docs: https://apidocs.chargebee.com/docs/api/customers?prod_cat_ver=2#list_customers
    """

    api = CustomerModel


class Invoice(IncrementalChargebeeStream):
    """
    API docs: https://apidocs.chargebee.com/docs/api/invoices?prod_cat_ver=2#list_invoices
    """

    api = InvoiceModel


class Order(IncrementalChargebeeStream):
    """
    API docs: https://apidocs.chargebee.com/docs/api/orders?prod_cat_ver=2#list_orders
    """

    api = OrderModel


class Plan(IncrementalChargebeeStream):
    """
    API docs: https://apidocs.chargebee.com/docs/api/plans?prod_cat_ver=1&lang=curl#list_plans
    """

    api = PlanModel


class Addon(IncrementalChargebeeStream):
    """
    API docs: https://apidocs.chargebee.com/docs/api/addons?prod_cat_ver=1&lang=curl#list_addons
    """

    api = AddonModel


class Item(IncrementalChargebeeStream):
    """
    API docs: https://apidocs.chargebee.com/docs/api/items?prod_cat_ver=2#list_items
    """

    api = ItemModel


class ItemPrice(IncrementalChargebeeStream):
    """
    API docs: https://apidocs.chargebee.com/docs/api/item_prices?prod_cat_ver=2#list_item_prices
    """

    api = ItemPriceModel


class AttachedItem(SemiIncrementalChargebeeStream):
    """
    API docs: https://apidocs.chargebee.com/docs/api/attached_items?prod_cat_ver=2#list_attached_items
    """

    api = AttachedItemModel

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        items_stream = Item(start_date="")
        for item in items_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield {"item_id": item["id"]}

    @default_backoff_handler(max_tries=MAX_TRIES, factor=MAX_TIME)
    def _send_request(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> ListResult:
        """
        Just a wrapper to allow @backoff decorator
        Reference: https://apidocs.chargebee.com/docs/api/#error_codes_list
        """
        params = self.request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        return self.api.list(id=stream_slice["item_id"], params=params)


class Event(IncrementalChargebeeStream):
    """
    API docs: https://apidocs.chargebee.com/docs/api/events?prod_cat_ver=2#list_events
    """

    cursor_field = "occurred_at"

    api = EventModel


class Transaction(IncrementalChargebeeStream):
    """
    API docs: https://apidocs.chargebee.com/docs/api/transactions?lang=curl&prod_cat_ver=2
    """

    cursor_field = "updated_at"

    api = TransactionModel
    transformer: TypeTransformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(**kwargs)
        params["sort_by[asc]"] = "date"
        return params


class Coupon(IncrementalChargebeeStream):
    """
    API docs: https://apidocs.chargebee.com/docs/api/coupons?prod_cat_ver=2#list_coupons
    """

    cursor_field = "updated_at"

    api = CouponModel

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(**kwargs)
        params["sort_by[asc]"] = "created_at"
        return params


class CreditNote(IncrementalChargebeeStream):
    """
    API docs: https://apidocs.chargebee.com/docs/api/credit_notes?prod_cat_ver=2#list_credit_notes
    """

    cursor_field = "updated_at"

    api = CreditNoteModel

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(**kwargs)
        params["sort_by[asc]"] = "date"
        return params
