#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import os
from multiprocessing import Pool
from typing import Any, Dict, Iterable, Mapping, Optional

from airbyte_cdk.sources.streams import IncrementalMixin, Stream

from .purchase_generator import PurchaseGenerator
from .user_generator import UserGenerator
from .utils import generate_estimate, read_json


class Products(Stream, IncrementalMixin):
    primary_key = None
    cursor_field = "id"

    def __init__(self, count: int, seed: int, parallelism: int, records_per_sync: int, records_per_slice: int, **kwargs):
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

    def __init__(self, count: int, seed: int, parallelism: int, records_per_sync: int, records_per_slice: int, **kwargs):
        super().__init__(**kwargs)
        self.count = count
        self.seed = seed
        self.records_per_sync = records_per_sync
        self.records_per_slice = records_per_slice
        self.parallelism = parallelism
        self.generator = UserGenerator(self.name, self.seed)

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

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        """
        This is a multi-process implementation of read_records.
        We make N workers (where N is the number of available CPUs) and spread out the CPU-bound work of generating records and serializing them to JSON
        """

        total_records = self.state[self.cursor_field] if self.cursor_field in self.state else 0
        records_in_sync = 0

        median_record_byte_size = 450
        yield generate_estimate(self.name, self.count - total_records, median_record_byte_size)

        with Pool(initializer=self.generator.prepare, processes=self.parallelism) as pool:
            while records_in_sync < self.count and records_in_sync < self.records_per_sync:
                records_remaining_this_loop = min(self.records_per_slice, (self.count - total_records))
                if records_remaining_this_loop <= 0:
                    break
                users = pool.map(self.generator.generate, range(total_records, total_records + records_remaining_this_loop))
                for user in users:
                    total_records += 1
                    records_in_sync += 1
                    yield user

                    if records_in_sync >= self.records_per_sync:
                        break

                self.state = {self.cursor_field: total_records, "seed": self.seed}

        self.state = {self.cursor_field: total_records, "seed": self.seed}


class Purchases(Stream, IncrementalMixin):
    primary_key = None
    cursor_field = "id"

    def __init__(self, count: int, seed: int, parallelism: int, records_per_sync: int, records_per_slice: int, **kwargs):
        super().__init__(**kwargs)
        self.count = count
        self.seed = seed
        self.records_per_sync = records_per_sync
        self.records_per_slice = records_per_slice
        self.parallelism = parallelism
        self.generator = PurchaseGenerator(self.name, self.seed)

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

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        """
        This is a multi-process implementation of read_records.
        We make N workers (where N is the number of available CPUs) and spread out the CPU-bound work of generating records and serializing them to JSON
        """

        total_purchase_records = self.state[self.cursor_field] if self.cursor_field in self.state else 0
        total_user_records = self.state["user_id"] if "user_id" in self.state else 0
        user_records_in_sync = 0

        # a fuzzy guess, some users have purchases, some don't
        median_record_byte_size = 230
        yield generate_estimate(self.name, (self.count - total_user_records) * 1.3, median_record_byte_size)

        with Pool(initializer=self.generator.prepare, processes=self.parallelism) as pool:
            while total_user_records < self.count and user_records_in_sync < self.records_per_sync:
                records_remaining_this_loop = min(self.records_per_slice, (self.count - user_records_in_sync))
                if records_remaining_this_loop <= 0:
                    break
                carts = pool.map(self.generator.generate, range(total_user_records, total_user_records + records_remaining_this_loop))
                for purchases in carts:
                    for purchase in purchases:
                        total_purchase_records += 1
                        yield purchase

                    total_user_records += 1
                    user_records_in_sync += 1

                    if user_records_in_sync >= self.records_per_sync:
                        break

                self.state = {self.cursor_field: total_purchase_records, "user_id": total_user_records, "seed": self.seed}

        self.state = {self.cursor_field: total_purchase_records, "user_id": total_user_records, "seed": self.seed}
