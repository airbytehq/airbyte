#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Generator, Iterable, List, Mapping, Optional, Union

import backoff
import braintree
import pendulum
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.core import Stream
from braintree.attribute_getter import AttributeGetter
from source_braintree.schemas import Customer, Discount, Dispute, MerchantAccount, Plan, Subscription, Transaction
from source_braintree.spec import BraintreeConfig


class BraintreeStream(Stream, ABC):
    def __init__(self, config: BraintreeConfig):
        self._start_date = config.start_date
        self._gateway = BraintreeStream.create_gateway(config)

    @staticmethod
    def create_gateway(config: BraintreeConfig):
        return braintree.BraintreeGateway(braintree.Configuration(**config.dict()))

    @property
    @abstractmethod
    def model(self):
        """
        Pydantic model to represent catalog schema
        """

    @abstractmethod
    def get_items(self, start_date: datetime) -> Generator:
        """
        braintree SDK gateway object for items list
        """

    def get_json_schema(self):
        return self.model.schema()

    def stream_slices(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Optional[Mapping[str, Any]]]:

        current_datetime = pendulum.utcnow()
        if sync_mode == SyncMode.full_refresh:
            return [{self.cursor_field or "start_date": self._start_date or current_datetime}]
        stream_state_start_date = stream_state.get(self.cursor_field)
        if stream_state_start_date:
            stream_state_start_date = pendulum.parse(stream_state_start_date)
        start_date = stream_state_start_date or self._start_date or current_datetime
        return [{self.cursor_field: start_date}]

    def get_updated_state(
        self,
        current_stream_state: Mapping[str, Any],
        latest_record: Mapping[str, Any],
    ):
        next_state = latest_record.get(self.cursor_field)
        current_state = current_stream_state.get(self.cursor_field)
        current_state = pendulum.parse(current_state) if current_state else next_state
        return {self.cursor_field: max(current_state, next_state).strftime("%Y-%m-%d %H:%M:%S")}

    @staticmethod
    def get_json_from_resource(resource_obj: Union[AttributeGetter, List[AttributeGetter]]):
        if isinstance(resource_obj, list):
            return [obj if not isinstance(obj, AttributeGetter) else BraintreeStream.get_json_from_resource(obj) for obj in resource_obj]
        obj_dict = resource_obj.__dict__
        result = dict()
        for attr in obj_dict:
            if not attr.startswith("_"):
                result[attr] = (
                    BraintreeStream.get_json_from_resource(obj_dict[attr])
                    if isinstance(obj_dict[attr], (AttributeGetter, list))
                    else obj_dict[attr]
                )
        return result

    @backoff.on_exception(
        backoff.expo,
        (
            braintree.exceptions.GatewayTimeoutError,
            braintree.exceptions.RequestTimeoutError,
            braintree.exceptions.ServerError,
            braintree.exceptions.ServiceUnavailableError,
            braintree.exceptions.TooManyRequestsError,
        ),
        max_tries=5,
    )
    def _collect_items(self, stream_slice: Mapping[str, Any]) -> List[Mapping[str, Any]]:
        """
        Fetch list of response object normalized acccording to catalog model.
        Braintree pagination API is designed to use lazy evaluation and SDK is
        built upon this approach: First its fetch list of ids, wraps it inside
        generator object and then iterates each items and send for getting
        additional details. Cause of this implementation we cant handle retry
        in case of individual item fails.
        :stream_slice Stream slice with cursor field in case of incremental stream.
        :return List of objects
        """
        start_date = stream_slice.get(self.cursor_field or "start_date")
        items = self.get_items(start_date)
        result = []
        for item in items:
            item = self.get_json_from_resource(item)
            item = self.model(**item)
            result.append(item.dict(exclude_unset=True))
        return result

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        yield from self._collect_items(stream_slice)


class CustomerStream(BraintreeStream):
    """
    https://developer.paypal.com/braintree/docs/reference/request/customer/search
    """

    primary_key = "id"
    model = Customer
    cursor_field = "created_at"

    def get_items(self, start_date: datetime):
        return self._gateway.customer.search(braintree.CustomerSearch.created_at >= start_date)


class DiscountStream(BraintreeStream):
    """
    https://developer.paypal.com/braintree/docs/reference/response/discount
    """

    primary_key = "id"
    model = Discount

    def get_items(self, start_date: datetime):
        return self._gateway.discount.all()


class DisputeStream(BraintreeStream):
    """
    https://developer.paypal.com/braintree/docs/reference/request/dispute/search
    """

    primary_key = "id"
    model = Dispute
    cursor_field = "received_date"

    def get_items(self, start_date: datetime):
        return self._gateway.dispute.search(braintree.DisputeSearch.received_date >= start_date.date()).disputes.items


class TransactionStream(BraintreeStream):
    """
    https://developer.paypal.com/braintree/docs/reference/response/transaction
    """

    primary_key = "id"
    model = Transaction
    cursor_field = "created_at"

    def get_items(self, start_date: datetime):
        return self._gateway.transaction.search(braintree.TransactionSearch.created_at >= start_date)


class MerchantAccountStream(BraintreeStream):
    """
    https://developer.paypal.com/braintree/docs/reference/response/merchant-account
    """

    primary_key = "id"
    model = MerchantAccount

    def get_items(self, start_date: datetime):
        return self._gateway.merchant_account.all().merchant_accounts


class PlanStream(BraintreeStream):
    """
    https://developer.paypal.com/braintree/docs/reference/response/plan
    """

    primary_key = "id"
    model = Plan

    def get_items(self, start_date: datetime):
        return self._gateway.plan.all()


class SubscriptionStream(BraintreeStream):
    """
    https://developer.paypal.com/braintree/docs/reference/response/subscription
    """

    primary_key = "id"
    model = Subscription
    cursor_field = "created_at"

    def get_items(self, start_date: datetime):
        return self._gateway.subscription.search(braintree.SubscriptionSearch.created_at >= start_date).items
