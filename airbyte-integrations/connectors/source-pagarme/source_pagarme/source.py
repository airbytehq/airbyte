#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from source_pagarme.streams import (
    Balance,
    BankAccounts,
    Cards,
    Chargebacks,
    Customers,
    Payables,
    PaymentLinks,
    Plans,
    Recipients,
    Refunds,
    SecurityRules,
    Transactions,
    Transfers,
)


class SourcePagarme(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            transactions = Transactions(config["api_key"], config["start_date"])
            transactions_gen = transactions.read_records(sync_mode=SyncMode.incremental)
            next(transactions_gen)
            return True, None
        except Exception as error:
            return (
                False,
                f"Unable to connect to Pagar.me API with the provided credentials - {repr(error)}",
            )

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        api_key = config["api_key"]
        start_date = config["start_date"]
        return [
            Balance(api_key=api_key, start_date=start_date),
            BankAccounts(api_key=api_key, start_date=start_date),
            Cards(api_key=api_key, start_date=start_date),
            Chargebacks(api_key=api_key, start_date=start_date),
            Customers(api_key=api_key, start_date=start_date),
            Payables(api_key=api_key, start_date=start_date),
            PaymentLinks(api_key=api_key, start_date=start_date),
            Plans(api_key=api_key, start_date=start_date),
            Recipients(api_key=api_key, start_date=start_date),
            Refunds(api_key=api_key, start_date=start_date),
            SecurityRules(api_key=api_key, start_date=start_date),
            Transactions(api_key=api_key, start_date=start_date),
            Transfers(api_key=api_key, start_date=start_date),
        ]
