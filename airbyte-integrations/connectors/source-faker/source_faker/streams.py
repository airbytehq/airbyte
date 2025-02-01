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
    primary_key = "id"
    cursor_field = "updated_at"

    def __init__(self, count: int, seed: int, parallelism: int, records_per_slice: int, always_updated: bool, **kwargs):
        super().__init__(**kwargs)
        self.count = count
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

        products = self.load_products()
        updated_at = ""

        median_record_byte_size = 180
        rows_to_emit = len(products)
        yield generate_estimate(self.name, rows_to_emit, median_record_byte_size)

        for product in products:
            if product["id"] <= self.count:
                now = datetime.datetime.now()
                updated_at = format_airbyte_time(now)
                product["updated_at"] = updated_at
                yield product

        self.state = {"seed": self.seed, "updated_at": updated_at}


class Users(Stream, IncrementalMixin):
    primary_key = "id"
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

        updated_at = ""

        median_record_byte_size = 450
        yield generate_estimate(self.name, self.count, median_record_byte_size)

        loop_offset = 0
        with Pool(initializer=self.generator.prepare, processes=self.parallelism) as pool:
            while loop_offset < self.count:
                records_remaining_this_loop = min(self.records_per_slice, (self.count - loop_offset))
                users = pool.map(self.generator.generate, range(loop_offset, loop_offset + records_remaining_this_loop))
                for user in users:
                    updated_at = user["updated_at"]
                    loop_offset += 1
                    yield user

                if records_remaining_this_loop == 0:
                    break

                self.state = {"seed": self.seed, "updated_at": updated_at, "loop_offset": loop_offset}

            self.state = {"seed": self.seed, "updated_at": updated_at, "loop_offset": loop_offset}


class Purchases(Stream, IncrementalMixin):
    primary_key = "id"
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

        updated_at = ""

        # a fuzzy guess, some users have purchases, some don't
        median_record_byte_size = 230
        yield generate_estimate(self.name, int(self.count * 1.3), median_record_byte_size)

        loop_offset = 0
        with Pool(initializer=self.generator.prepare, processes=self.parallelism) as pool:
            while loop_offset < self.count:
                records_remaining_this_loop = min(self.records_per_slice, (self.count - loop_offset))
                carts = pool.map(self.generator.generate, range(loop_offset, loop_offset + records_remaining_this_loop))
                for purchases in carts:
                    loop_offset += 1
                    for purchase in purchases:
                        updated_at = purchase["updated_at"]
                        yield purchase
                if records_remaining_this_loop == 0:
                    break

                self.state = {"seed": self.seed, "updated_at": updated_at, "loop_offset": loop_offset}

            self.state = {"seed": self.seed, "updated_at": updated_at, "loop_offset": loop_offset}
