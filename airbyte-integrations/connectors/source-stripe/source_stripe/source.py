#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


from typing import Any, List, Mapping, Tuple

import stripe
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from source_stripe.streams import (
    BalanceTransactions,
    BankAccounts,
    Charges,
    Coupons,
    CustomerBalanceTransactions,
    Customers,
    Disputes,
    Events,
    InvoiceItems,
    InvoiceLineItems,
    Invoices,
    PaymentIntents,
    Payouts,
    Plans,
    Products,
    Refunds,
    SubscriptionItems,
    Subscriptions,
    Transfers,
)


class SourceStripe(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            stripe.api_key = config["client_secret"]
            stripe.Account.retrieve(config["account_id"])
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = TokenAuthenticator(config["client_secret"])
        args = {"authenticator": authenticator, "account_id": config["account_id"]}
        return [
            BalanceTransactions(**args),
            BankAccounts(**args),
            Charges(**args),
            Coupons(**args),
            CustomerBalanceTransactions(**args),
            Customers(**args),
            Disputes(**args),
            Events(**args),
            InvoiceItems(**args),
            InvoiceLineItems(**args),
            Invoices(**args),
            PaymentIntents(**args),
            Payouts(**args),
            Plans(**args),
            Products(**args),
            Refunds(**args),
            SubscriptionItems(**args),
            Subscriptions(**args),
            Transfers(**args),
        ]
