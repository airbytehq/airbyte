#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
from multiprocessing import current_process
from mimesis import Datetime, Numeric
from typing import cast

from airbyte_cdk.models import AirbyteRecordMessage, Type

from .airbyte_message_with_cached_json import AirbyteMessageWithCachedJSON
from .utils import format_airbyte_time, now_millis

# Global variables for mimesis generators
dt: Datetime | None = None
numeric: Numeric | None = None


class PurchaseGenerator:
    def __init__(self, stream_name: str, seed: int) -> None:
        self.stream_name = stream_name
        self.seed = seed

    def prepare(self):
        """
        Note: the instances of the mimesis generators need to be global.
        Yes, they *should* be able to be instance variables on this class, which should only instantiated once-per-worker, but that's not quite the case:
        * relying only on prepare as a pool initializer fails because we are calling the parent process's method, not the fork
        * Calling prepare() as part of generate() (perhaps checking if self.person is set) and then `print(self, current_process()._identity, current_process().pid)` reveals multiple object IDs in the same process, resetting the internal random counters
        """

        seed_with_offset = self.seed
        if self.seed is not None and len(current_process()._identity) > 0:
            seed_with_offset = self.seed + current_process()._identity[0]

        global dt
        global numeric

        dt = Datetime(seed=seed_with_offset)
        numeric = Numeric(seed=seed_with_offset)

    def random_date_in_range(
        self, start_date: datetime.datetime, end_date: datetime.datetime = datetime.datetime.now()
    ) -> datetime.datetime:
        if not all([dt, numeric]):
            self.prepare()

        # After prepare(), these should never be None
        numeric_gen = cast(Numeric, numeric)

        time_between_dates = end_date - start_date
        days_between_dates = time_between_dates.days
        if days_between_dates < 2:
            days_between_dates = 2
        random_number_of_days = numeric_gen.integer_number(0, days_between_dates)
        random_date = start_date + datetime.timedelta(days=random_number_of_days)
        return random_date

    def generate(self, user_id: int) -> list[dict]:
        """
        Because we are doing this work in parallel processes, we need a deterministic way to know what a purchase's ID should be given on the input of a user_id.
        tldr; Every 10 user_ids produce 10 purchases.  User ID x5 has no purchases, User ID mod x7 has 2, and everyone else has 1
        """
        if not all([dt, numeric]):
            self.prepare()

        # After prepare(), these should never be None
        dt_gen = cast(Datetime, dt)
        numeric_gen = cast(Numeric, numeric)

        purchases: list[dict] = []
        last_user_id_digit = int(repr(user_id)[-1])
        purchase_count = 1
        id_offset = 0
        if last_user_id_digit - 1 == 5:
            purchase_count = 0
        elif last_user_id_digit - 1 == 6:
            id_offset = 1
        elif last_user_id_digit - 1 == 7:
            id_offset = 1
            purchase_count = 2

        total_products = 100
        i = 0

        while purchase_count > 0:
            id = user_id + i + 1 - id_offset
            time_a = dt_gen.datetime()
            time_b = dt_gen.datetime()
            updated_at = format_airbyte_time(datetime.datetime.now())
            created_at = time_a if time_a <= time_b else time_b
            product_id = numeric_gen.integer_number(1, total_products)
            added_to_cart_at = self.random_date_in_range(created_at)
            purchased_at = (
                self.random_date_in_range(added_to_cart_at)
                if added_to_cart_at is not None and numeric_gen.integer_number(1, 100) <= 70
                else None
            )  # 70% likely to purchase the item in the cart
            returned_at = (
                self.random_date_in_range(purchased_at) if purchased_at is not None and numeric_gen.integer_number(1, 100) <= 15 else None
            )  # 15% likely to return the item

            purchase = {
                "id": id,
                "product_id": product_id,
                "user_id": user_id + 1,
                "created_at": created_at,
                "updated_at": updated_at,
                "added_to_cart_at": format_airbyte_time(added_to_cart_at) if added_to_cart_at is not None else None,
                "purchased_at": format_airbyte_time(purchased_at) if purchased_at is not None else None,
                "returned_at": format_airbyte_time(returned_at) if returned_at is not None else None,
            }

            record = AirbyteRecordMessage(stream=self.stream_name, data=purchase, emitted_at=now_millis())
            message = AirbyteMessageWithCachedJSON(type=Type.RECORD, record=record)
            purchases.append(message)

            purchase_count = purchase_count - 1
            i += 1

        return purchases
