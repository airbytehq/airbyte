#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime
import os
from multiprocessing import Pool, current_process
from typing import Any, Dict, Iterable, Mapping, Optional

from airbyte_cdk.models import AirbyteRecordMessage, Type
from airbyte_cdk.sources.streams import IncrementalMixin, Stream
from mimesis import Datetime, Numeric, Person
from mimesis.locales import Locale

from .airbyte_message_with_cached_json import AirbyteMessageWithCachedJSON
from .utils import format_airbyte_time, generate_estimate, now_millis, read_json


class FakerMultithreaded:
    def worker_init(self):
        """For the workers, we want a unique instance of the faker packages with their own seeds to differentiate the generated responses"""
        global person
        global dt
        global numeric
        seed_with_offset = self.seed
        if self.seed is not None:
            seed_with_offset = self.seed + current_process()._identity[0]
        person = Person(locale=Locale.EN, seed=seed_with_offset)
        dt = Datetime(seed=seed_with_offset)
        numeric = Numeric(seed=seed_with_offset)


class Products(Stream, IncrementalMixin):
    primary_key = None
    cursor_field = "id"

    def __init__(self, count: int, seed: int, threads: int, records_per_sync: int, records_per_slice: int, **kwargs):
        super().__init__(**kwargs)
        self.seed = seed
        self.records_per_sync = records_per_sync
        self.records_per_slice = records_per_slice

    @property
    def state_checkpoint_interval(self) -> Optional[int]:
        return self.records_per_slice

    @property
    def state(self) -> Mapping[str, Any]:
        if hasattr(self, "_state"):
            return self._state
        else:
            return {self.cursor_field: 0}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._state = value

    def load_products(self) -> list[Dict]:
        dirname = os.path.dirname(os.path.realpath(__file__))
        return read_json(os.path.join(dirname, "record_data", "products.json"))

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        total_records = self.state[self.cursor_field] if self.cursor_field in self.state else 0
        products = self.load_products()

        median_record_byte_size = 180
        rows_to_emit = len(products) - total_records
        if rows_to_emit > 0:
            yield generate_estimate(self.name, rows_to_emit, median_record_byte_size)

        for product in products:
            if product["id"] > total_records:
                yield product
                total_records = product["id"]

        self.state = {self.cursor_field: total_records, "seed": self.seed}


class Users(Stream, IncrementalMixin, FakerMultithreaded):
    primary_key = None
    cursor_field = "id"

    def __init__(self, count: int, seed: int, threads: int, records_per_sync: int, records_per_slice: int, **kwargs):
        super().__init__(**kwargs)
        self.count = count
        self.seed = seed
        self.records_per_sync = records_per_sync
        self.records_per_slice = records_per_slice
        self.threads = threads

    @property
    def state_checkpoint_interval(self) -> Optional[int]:
        return self.records_per_slice

    @property
    def state(self) -> Mapping[str, Any]:
        if hasattr(self, "_state"):
            return self._state
        else:
            return {self.cursor_field: 0}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._state = value

    def generate_user(self, user_id: int):
        time_a = dt.datetime()
        time_b = dt.datetime()

        # faker doesn't always produce unique email addresses, so to enforce uniqueness, we will append the user_id to the prefix
        email_parts = person.email().split("@")
        email = f"{email_parts[0]}+{user_id + 1}@{email_parts[1]}"

        profile = {
            "id": user_id + 1,
            "created_at": format_airbyte_time(time_a if time_a <= time_b else time_b),
            "updated_at": format_airbyte_time(time_a if time_a > time_b else time_b),
            "name": person.name(),
            "title": person.title(),
            "age": person.age(),
            "email": email,
            "telephone": person.telephone(),
            "gender": person.gender(),
            "language": person.language(),
            "academic_degree": person.academic_degree(),
            "nationality": person.nationality(),
            "occupation": person.occupation(),
            "height": person.height(),
            "blood_type": person.blood_type(),
            "weight": person.weight(),
        }

        while not profile["created_at"]:
            profile["created_at"] = format_airbyte_time(dt.datetime())

        if not profile["updated_at"]:
            profile["updated_at"] = profile["created_at"] + 1

        record = AirbyteRecordMessage(stream=self.name, data=profile, emitted_at=now_millis())
        return AirbyteMessageWithCachedJSON(type=Type.RECORD, record=record)

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        total_records = self.state[self.cursor_field] if self.cursor_field in self.state else 0
        records_in_sync = 0

        median_record_byte_size = 450
        yield generate_estimate(self.name, self.count - total_records, median_record_byte_size)

        running = True
        with Pool(initializer=self.worker_init, processes=self.threads) as pool:
            while running and records_in_sync < self.count:
                records_remaining_this_loop = min(self.records_per_slice, (self.count - total_records))
                if records_remaining_this_loop <= 0:
                    running = False
                    break
                users = pool.map(self.generate_user, range(total_records, total_records + records_remaining_this_loop))
                for user in users:
                    total_records += 1
                    records_in_sync += 1
                    yield user

                    if records_in_sync == self.records_per_sync:
                        running = False
                        break

                self.state = {self.cursor_field: total_records, "seed": self.seed}

        self.state = {self.cursor_field: total_records, "seed": self.seed}


class Purchases(Stream, IncrementalMixin, FakerMultithreaded):
    primary_key = None
    cursor_field = "id"

    def __init__(self, count: int, seed: int, threads: int, records_per_sync: int, records_per_slice: int, **kwargs):
        super().__init__(**kwargs)
        self.count = count
        self.seed = seed
        self.records_per_sync = records_per_sync
        self.records_per_slice = records_per_slice
        self.dt = Datetime(seed=self.seed)
        self.numeric = Numeric(seed=self.seed)
        self.threads = threads

    @property
    def state_checkpoint_interval(self) -> Optional[int]:
        return self.records_per_slice

    @property
    def state(self) -> Mapping[str, Any]:
        if hasattr(self, "_state"):
            return self._state
        else:
            return {self.cursor_field: 0}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._state = value

    def random_date_in_range(
        self, start_date: datetime.datetime, end_date: datetime.datetime = datetime.datetime.now()
    ) -> datetime.datetime:
        time_between_dates = end_date - start_date
        days_between_dates = time_between_dates.days
        if days_between_dates < 2:
            days_between_dates = 2
        random_number_of_days = self.numeric.integer_number(0, days_between_dates)
        random_date = start_date + datetime.timedelta(days=random_number_of_days)
        return random_date

    def generate_purchases(self, user_id: int) -> list[Dict]:
        """Because we are doing this work in parallel processes, we need a deterministic way to know what a purchase's ID should be given on the input of a user_id"""
        """tldr; Every 10 user_ids produce 10 purchases.  User ID x5 has no purchases, User ID mod x7 has 2, and everyone else has 1"""

        purchases: list[Dict] = []
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
            time_a = dt.datetime()
            time_b = dt.datetime()
            created_at = time_a if time_a <= time_b else time_b
            product_id = numeric.integer_number(1, total_products)
            added_to_cart_at = self.random_date_in_range(created_at)
            purchased_at = (
                self.random_date_in_range(added_to_cart_at)
                if added_to_cart_at is not None and numeric.integer_number(1, 100) <= 70
                else None
            )  # 70% likely to purchase the item in the cart
            returned_at = (
                self.random_date_in_range(purchased_at) if purchased_at is not None and numeric.integer_number(1, 100) <= 15 else None
            )  # 15% likely to return the item

            purchase = {
                "id": id,
                "product_id": product_id,
                "user_id": user_id + 1,
                "added_to_cart_at": format_airbyte_time(added_to_cart_at) if added_to_cart_at is not None else None,
                "purchased_at": format_airbyte_time(purchased_at) if purchased_at is not None else None,
                "returned_at": format_airbyte_time(returned_at) if returned_at is not None else None,
            }

            record = AirbyteRecordMessage(stream=self.name, data=purchase, emitted_at=now_millis())
            message = AirbyteMessageWithCachedJSON(type=Type.RECORD, record=record)
            purchases.append(message)

            purchase_count = purchase_count - 1
            i += 1

        return purchases

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        total_purchase_records = self.state[self.cursor_field] if self.cursor_field in self.state else 0
        total_user_records = self.state["user_id"] if "user_id" in self.state else 0
        user_records_in_sync = 0

        median_record_byte_size = 230
        yield generate_estimate(
            self.name, (self.count - total_user_records) * 1.3, median_record_byte_size
        )  # a fuzzy guess, some users have purchases, some don't

        running = True
        with Pool(initializer=self.worker_init, processes=self.threads) as pool:
            while running and total_user_records < self.count:
                records_remaining_this_loop = min(self.records_per_slice, (self.count - user_records_in_sync))
                if records_remaining_this_loop <= 0:
                    running = False
                    break
                carts = pool.map(self.generate_purchases, range(total_user_records, total_user_records + records_remaining_this_loop))
                for purchases in carts:
                    for purchase in purchases:
                        total_purchase_records += 1
                        yield purchase

                    total_user_records += 1
                    user_records_in_sync += 1

                    if user_records_in_sync == self.records_per_sync:
                        running = False
                        break

                self.state = {self.cursor_field: total_purchase_records, "user_id": total_user_records, "seed": self.seed}

        self.state = {self.cursor_field: total_purchase_records, "user_id": total_user_records, "seed": self.seed}
