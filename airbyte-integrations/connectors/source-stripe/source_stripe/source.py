"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import math
import requests

from abc import ABC, abstractmethod
from typing import Any, Tuple, Mapping, Iterable, Optional, MutableMapping, List

import stripe

from base_python import AbstractSource, HttpStream, Stream, TokenAuthenticator


class StripeStream(HttpStream, ABC):
    url_base = "https://api.stripe.com/v1/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        decoded_response = response.json()
        if bool(decoded_response.get('has_more', "False")) and decoded_response.get('data', []):
            last_object_id = decoded_response['data'][-1]['id']
            return {'starting_after': last_object_id}

    def request_params(
            self,
            stream_state: Mapping[str, Any],
            request_configuration: Optional[Mapping] = None,
            next_page_token: Mapping[str, Any] = None,
            parent_stream_record: Mapping = None
    ) -> MutableMapping[str, Any]:

        # Stripe default pagination is 10, max is 100
        params = {'limit': 100}

        # Handle pagination by inserting the next page's token in the request parameters
        if next_page_token:
            params.update(next_page_token)

        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        yield from response_json.get('data', [])  # Stripe puts records in a container array "data"


class IncrementalStripeStream(StripeStream, ABC):
    # Stripe returns most recently created objects first, so we don't want to persist state until the entire stream has been read
    state_checkpoint_interval = math.inf

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
        return {
            self.cursor_field: max(latest_record.get(self.cursor_field), current_stream_state.get(self.cursor_field, 0))
        }

    def request_params(self, stream_state=None, **kwargs):
        stream_state = stream_state or {}
        params = super().request_params(stream_state=stream_state, **kwargs)
        params['created'] = stream_state.get(self.cursor_field)
        return params


class Customers(IncrementalStripeStream):
    cursor_field = 'created'

    def path(self, **kwargs) -> str:
        return "customers"


class BalanceTransactions(IncrementalStripeStream):
    cursor_field = 'created'
    name = "balance_transactions"

    def path(self, **kwargs) -> str:
        return "balance_transactions"


class Charges(IncrementalStripeStream):
    cursor_field = 'created'

    def path(self, **kwargs) -> str:
        return "charges"


class CustomerBalanceTransactions(StripeStream):
    name = "customer_balance_transactions"

    def path(self, parent_stream_record, **kwargs):
        customer_id = parent_stream_record['id']
        return f"customers/{customer_id}/balance_transactions"


class Coupons(IncrementalStripeStream):
    cursor_field = 'created'

    def path(self, **kwargs):
        return "coupons"


class Disputes(IncrementalStripeStream):
    cursor_field = 'created'

    def path(self, **kwargs):
        return "disputes"


class Events(IncrementalStripeStream):
    cursor_field = 'created'

    def path(self, **kwargs):
        return "events"


class Invoices(IncrementalStripeStream):
    cursor_field = 'created'

    def path(self, **kwargs):
        return "invoices"


class InvoiceLineItems(StripeStream):
    name = 'invoice_line_items'

    def path(self, parent_stream_record, **kwargs):
        return f"invoices/{parent_stream_record['id']}/lines"


class InvoiceItems(IncrementalStripeStream):
    cursor_field = 'date'
    name = 'invoice_items'

    def path(self, **kwargs):
        return "invoiceitems"


class Payouts(IncrementalStripeStream):
    cursor_field = 'created'

    def path(self, **kwargs):
        return "payouts"


class Plans(IncrementalStripeStream):
    cursor_field = 'created'

    def path(self, **kwargs):
        return "plans"


class Products(IncrementalStripeStream):
    cursor_field = 'created'

    def path(self, **kwargs):
        return "products"


class Subscriptions(IncrementalStripeStream):
    cursor_field = 'created'

    def path(self, **kwargs):
        return "subscriptions"


class SubscriptionItems(StripeStream):
    name = 'subscription_items'

    def path(self, **kwargs):
        return "subscription_items"

    def request_params(self, parent_stream_record=None, **kwargs):
        params = super().request_params(parent_stream_record=parent_stream_record, **kwargs)
        params['subscription'] = parent_stream_record['id']
        return params


class Transfers(IncrementalStripeStream):
    cursor_field = 'created'

    def path(self, **kwargs):
        return "transfers"


class SourceStripe(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            stripe.api_key = config["client_secret"]
            stripe.Account.retrieve(config["account_id"])
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = TokenAuthenticator(config['client_secret'])

        customers = Customers(authenticator=authenticator)
        subscriptions = Subscriptions(authenticator=authenticator)
        invoices = Invoices(authenticator=authenticator)
        return [
            BalanceTransactions(authenticator=authenticator),
            Charges(authenticator=authenticator),
            Coupons(authenticator=authenticator),
            customers,
            CustomerBalanceTransactions(authenticator=authenticator, parent_stream=customers),
            Disputes(authenticator=authenticator),
            Events(authenticator=authenticator),
            InvoiceItems(authenticator=authenticator),
            InvoiceLineItems(authenticator=authenticator, parent_stream=invoices),
            invoices,
            Plans(authenticator=authenticator),
            Payouts(authenticator=authenticator),
            Products(authenticator=authenticator),
            subscriptions,
            SubscriptionItems(authenticator=authenticator, parent_stream=subscriptions),
            Transfers(authenticator=authenticator)
        ]
