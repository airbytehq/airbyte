#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Union

from pendulum import timezone
from pendulum.tz.timezone import Timezone


@dataclass
class Customer:
    id: str
    time_zone: Union[timezone, str] = "local"
    is_manager_account: bool = False

    @classmethod
    def from_accounts(cls, accounts: Iterable[Iterable[Mapping[str, Any]]]):
        data_objects = []
        for account_list in accounts:
            for account in account_list:
                time_zone_name = account.get("customer.time_zone")
                tz = Timezone(time_zone_name) if time_zone_name else "local"

                data_objects.append(
                    cls(id=str(account["customer.id"]), time_zone=tz, is_manager_account=bool(account.get("customer.manager")))
                )
        return data_objects
