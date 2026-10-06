#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from dataclasses import dataclass
from typing import Any, Iterable, List, Mapping

from pendulum import local_timezone, timezone
from pendulum.tz.timezone import Timezone


@dataclass
class CustomerModel:
    id: str
    time_zone: timezone = local_timezone()
    is_manager_account: bool = False
    login_customer_id: str = None

    @classmethod
    def _unique_from_accounts(cls, accounts: Iterable[Mapping[str, Any]]) -> Iterable["CustomerModel"]:
        seen_ids = set()

        for account in accounts:
            time_zone_name = account.get("customer_client.time_zone")
            tz = Timezone(time_zone_name) if time_zone_name else local_timezone()
            customer_id = str(account["customer_client.id"])

            # filter duplicates as one customer can be accessible from multiple connected accounts
            if customer_id in seen_ids:
                continue

            yield cls(
                id=customer_id,
                time_zone=tz,
                is_manager_account=bool(account.get("customer_client.manager")),
                login_customer_id=account.get("login_customer_id"),
            )

            seen_ids.add(customer_id)

    @classmethod
    def from_accounts(cls, accounts: Iterable[Mapping[str, Any]]) -> List["CustomerModel"]:
        return list(cls._unique_from_accounts(accounts))

    @classmethod
    def from_accounts_by_id(cls, accounts: Iterable[Mapping[str, Any]], customer_ids: List[str]) -> List["CustomerModel"]:
        return [customer for customer in cls._unique_from_accounts(accounts) if customer.id in customer_ids]
