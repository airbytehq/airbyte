#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from pendulum import local_timezone, timezone
from pendulum.tz.timezone import Timezone


@dataclass
class CustomerModel:
    id: str
    time_zone: timezone = local_timezone()
    is_manager_account: bool = False
    login_customer_id: str = None

    @classmethod
    def from_accounts(cls, accounts: Iterable[Mapping[str, Any]]) -> Iterable["CustomerModel"]:
        data_objects = []
        for account in accounts:
            time_zone_name = account.get("customer_client.time_zone")
            tz = Timezone(time_zone_name) if time_zone_name else local_timezone()

            data_objects.append(
                cls(
                    id=str(account["customer_client.id"]),
                    time_zone=tz,
                    is_manager_account=bool(account.get("customer_client.manager")),
                    login_customer_id=account.get("login_customer_id"),
                )
            )
        return data_objects
