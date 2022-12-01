#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime
import os
from typing import Any, Dict, Iterable, Mapping, Optional

from airbyte_cdk.models import AirbyteEstimateTraceMessage, AirbyteTraceMessage, EstimateType, TraceType
from airbyte_cdk.sources.streams import IncrementalMixin, Stream
from mimesis import Datetime, Numeric, Person
from mimesis.locales import Locale

from .utils import format_airbyte_time, read_json


class Products(Stream, IncrementalMixin):
    primary_key = None
    cursor_field = "id"

    def __init__(self, count: int, seed: int, records_per_sync: int, records_per_slice: int, **kwargs):
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


class Users(Stream, IncrementalMixin):
    primary_key = None
    cursor_field = "id"

    def __init__(self, count: int, seed: int, records_per_sync: int, records_per_slice: int, **kwargs):
        super().__init__(**kwargs)
        self.count = count
        self.seed = seed
        self.records_per_sync = records_per_sync
        self.records_per_slice = records_per_slice
        self.person = Person(locale=Locale.EN, seed=self.seed)
        self.dt = Datetime(seed=self.seed)

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
        time_a = self.dt.datetime()
        time_b = self.dt.datetime()

        profile = {
            "id": user_id + 1,
            "created_at": format_airbyte_time(time_a if time_a <= time_b else time_b),
            "updated_at": format_airbyte_time(time_a if time_a > time_b else time_b),
            "name": self.person.name(),
            "title": self.person.title(),
            "age": self.person.age(),
            "email": self.person.email(),
            "telephone": self.person.telephone(),
            "gender": self.person.gender(),
            "language": self.person.language(),
            "academic_degree": self.person.academic_degree(),
            "nationality": self.person.nationality(),
            "occupation": self.person.occupation(),
            "height": self.person.height(),
            "blood_type": self.person.blood_type(),
            "weight": self.person.weight(),
        }

        while not profile["created_at"]:
            profile["created_at"] = format_airbyte_time(self.dt.datetime())

        if not profile["updated_at"]:
            profile["updated_at"] = profile["created_at"] + 1

        return profile

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        total_records = self.state[self.cursor_field] if self.cursor_field in self.state else 0
        records_in_sync = 0
        records_in_slice = 0

        median_record_byte_size = 450
        yield generate_estimate(self.name, self.count - total_records, median_record_byte_size)

        for i in range(total_records, self.count):
            user = self.generate_user(i)
            yield user
            total_records += 1
            records_in_sync += 1
            records_in_slice += 1

            if records_in_slice >= self.records_per_slice:
                self.state = {self.cursor_field: total_records, "seed": self.seed}
                records_in_slice = 0

            if records_in_sync == self.records_per_sync:
                break

        self.state = {self.cursor_field: total_records, "seed": self.seed}
        set_total_user_records(total_records)


class Purchases(Stream, IncrementalMixin):
    primary_key = None
    cursor_field = "user_id"

    def __init__(self, seed: int, records_per_sync: int, records_per_slice: int, **kwargs):
        super().__init__(**kwargs)
        self.seed = seed
        self.records_per_sync = records_per_sync
        self.records_per_slice = records_per_slice
        self.dt = Datetime(seed=self.seed)
        self.numeric = Numeric(seed=self.seed)

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

    def generate_purchases(self, user_id: int, purchases_count: int) -> list[Dict]:
        purchases: list[Dict] = []
        purchase_percent_remaining = 70  # ~30% of people will have no purchases
        total_products = 100
        purchase_percent_remaining = purchase_percent_remaining - self.numeric.integer_number(1, 100)
        i = 0

        time_a = self.dt.datetime()
        time_b = self.dt.datetime()
        created_at = time_a if time_a <= time_b else time_b

        while purchase_percent_remaining > 0:
            id = purchases_count + i + 1
            product_id = self.numeric.integer_number(1, total_products)
            added_to_cart_at = self.random_date_in_range(created_at)
            purchased_at = (
                self.random_date_in_range(added_to_cart_at)
                if added_to_cart_at is not None and self.numeric.integer_number(1, 100) <= 70
                else None
            )  # 70% likely to purchase the item in the cart
            returned_at = (
                self.random_date_in_range(purchased_at) if purchased_at is not None and self.numeric.integer_number(1, 100) <= 15 else None
            )  # 15% likely to return the item

            purchase = {
                "id": id,
                "product_id": product_id,
                "user_id": user_id,
                "added_to_cart_at": format_airbyte_time(added_to_cart_at) if added_to_cart_at is not None else None,
                "purchased_at": format_airbyte_time(purchased_at) if purchased_at is not None else None,
                "returned_at": format_airbyte_time(returned_at) if returned_at is not None else None,
            }
            purchases.append(purchase)

            purchase_percent_remaining = purchase_percent_remaining - self.numeric.integer_number(1, 100)
            i += 1
        return purchases

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        purchases_count = self.state[self.cursor_field] if self.cursor_field in self.state else 0

        if total_user_records <= 0:
            return  # if there are no new users, there should be no new purchases

        median_record_byte_size = 230
        yield generate_estimate(
            self.name, total_user_records - purchases_count * 1.3, median_record_byte_size
        )  # a fuzzy guess, some users have purchases, some don't

        for i in range(purchases_count, total_user_records):
            purchases = self.generate_purchases(i + 1, purchases_count)
            for purchase in purchases:
                yield purchase
                purchases_count += 1

        self.state = {self.cursor_field: total_user_records, "seed": self.seed}


def generate_estimate(stream_name: str, total: int, bytes_per_row: int):
    emitted_at = int(datetime.datetime.now().timestamp() * 1000)
    estimate_message = AirbyteEstimateTraceMessage(
        type=EstimateType.STREAM, name=stream_name, row_estimate=round(total), byte_estimate=round(total * bytes_per_row)
    )
    return AirbyteTraceMessage(type=TraceType.ESTIMATE, emitted_at=emitted_at, estimate=estimate_message)


# a globals hack to share data between streams:
total_user_records = 0


def set_total_user_records(total: int):
    globals()["total_user_records"] = total
