#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
import os
from multiprocessing import Pool
from typing import Any, Dict, Iterable, List, Mapping, Optional

from airbyte_cdk.sources.streams import IncrementalMixin, Stream

from .purchase_generator import PurchaseGenerator
from .user_generator import UserGenerator
from .utils import format_airbyte_time, generate_estimate, read_json


class Products(Stream, IncrementalMixin):
    primary_key = None
    cursor_field = "updated_at"

    def __init__(self, count: int, seed: int, parallelism: int, records_per_slice: int, always_updated: bool, **kwargs):
        super().__init__(**kwargs)
        self.seed = seed
        self.records_per_slice = records_per_slice
        self.always_updated = always_updated

    @property
    def state_checkpoint_interval(self) -> Optional[int]:
        return self.records_per_slice

    @property
    def state(self) -> Mapping[str, Any]:
        if hasattr(self, "_state"):
            return self._state
        else:
            return {}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._state = value

    def load_products(self) -> List[Dict]:
        dirname = os.path.dirname(os.path.realpath(__file__))
        return read_json(os.path.join(dirname, "record_data", "products.json"))

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        if "updated_at" in self.state and not self.always_updated:
            return iter([])

        total_records = self.state["id"] if "id" in self.state else 0
        products = self.load_products()
        updated_at = ""

        median_record_byte_size = 180
        rows_to_emit = len(products) - total_records
        if rows_to_emit > 0:
            yield generate_estimate(self.name, rows_to_emit, median_record_byte_size)

        for product in products:
            if product["id"] > total_records:
                product["updated_at"] = format_airbyte_time(datetime.datetime.now())
                yield product
                total_records = product["id"]
            updated_at = product["updated_at"]

        self.state = {"id": total_records, "seed": self.seed, "updated_at": updated_at}


class Users(Stream, IncrementalMixin):
    primary_key = None
    cursor_field = "updated_at"

    def __init__(self, count: int, seed: int, parallelism: int, records_per_slice: int, always_updated: bool, **kwargs):
        super().__init__(**kwargs)
        self.count = count
        self.seed = seed
        self.records_per_slice = records_per_slice
        self.parallelism = parallelism
        self.always_updated = always_updated
        self.generator = UserGenerator(self.name, self.seed)

    @property
    def state_checkpoint_interval(self) -> Optional[int]:
        return self.records_per_slice

    @property
    def state(self) -> Mapping[str, Any]:
        if hasattr(self, "_state"):
            return self._state
        else:
            return {}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._state = value

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        """
        This is a multi-process implementation of read_records.
        We make N workers (where N is the number of available CPUs) and spread out the CPU-bound work of generating records and serializing them to JSON
        """

        if "updated_at" in self.state and not self.always_updated:
            return iter([])

        total_records = self.state["id"] if "id" in self.state else 0
        records_in_sync = 0
        updated_at = ""

        median_record_byte_size = 450
        yield generate_estimate(self.name, self.count - total_records, median_record_byte_size)

        with Pool(initializer=self.generator.prepare, processes=self.parallelism) as pool:
            while records_in_sync < self.count:
                records_remaining_this_loop = min(self.records_per_slice, (self.count - total_records))
                users = pool.map(self.generator.generate, range(total_records, total_records + records_remaining_this_loop))
                for user in users:
                    updated_at = user.record.data["updated_at"]
                    total_records += 1
                    records_in_sync += 1
                    yield user

                if records_remaining_this_loop == 0:
                    break

                self.state = {"id": total_records, "seed": self.seed, "updated_at": updated_at}

        self.state = {"id": total_records, "seed": self.seed, "updated_at": updated_at}


class Purchases(Stream, IncrementalMixin):
    primary_key = None
    cursor_field = "updated_at"

    def __init__(self, count: int, seed: int, parallelism: int, records_per_slice: int, always_updated: bool, **kwargs):
        super().__init__(**kwargs)
        self.count = count
        self.seed = seed
        self.records_per_slice = records_per_slice
        self.parallelism = parallelism
        self.always_updated = always_updated
        self.generator = PurchaseGenerator(self.name, self.seed)

    @property
    def state_checkpoint_interval(self) -> Optional[int]:
        return self.records_per_slice

    @property
    def state(self) -> Mapping[str, Any]:
        if hasattr(self, "_state"):
            return self._state
        else:
            return {}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._state = value

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        """
        This is a multi-process implementation of read_records.
        We make N workers (where N is the number of available CPUs) and spread out the CPU-bound work of generating records and serializing them to JSON
        """

        if "updated_at" in self.state and not self.always_updated:
            return iter([])

        total_purchase_records = self.state["id"] if "id" in self.state else 0
        total_user_records = self.state["user_id"] if "user_id" in self.state else 0
        user_records_in_sync = 0
        updated_at = ""

        # a fuzzy guess, some users have purchases, some don't
        median_record_byte_size = 230
        yield generate_estimate(self.name, (self.count - total_user_records) * 1.3, median_record_byte_size)

        with Pool(initializer=self.generator.prepare, processes=self.parallelism) as pool:
            while total_user_records < self.count:
                records_remaining_this_loop = min(self.records_per_slice, (self.count - user_records_in_sync))
                carts = pool.map(self.generator.generate, range(total_user_records, total_user_records + records_remaining_this_loop))
                for purchases in carts:
                    for purchase in purchases:
                        updated_at = purchase.record.data["updated_at"]
                        total_purchase_records += 1
                        yield purchase

                    total_user_records += 1
                    user_records_in_sync += 1

                if records_remaining_this_loop == 0:
                    break

                self.state = {"id": total_purchase_records, "user_id": total_user_records, "seed": self.seed, "updated_at": updated_at}

        self.state = {"id": total_purchase_records, "user_id": total_user_records, "seed": self.seed, "updated_at": updated_at}
