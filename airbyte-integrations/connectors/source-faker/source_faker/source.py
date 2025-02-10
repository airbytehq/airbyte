#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, List, Mapping, Tuple

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .streams import Products, Purchases, Users


DEFAULT_COUNT = 1_000


class SourceFaker(AbstractSource):
    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        if type(config["count"]) == int or type(config["count"]) == float:
            return True, None
        else:
            return False, "Count option is missing"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        count: int = config["count"] if "count" in config else DEFAULT_COUNT
        seed: int = config.get("seed")  # Allow None as default
        records_per_slice: int = config.get("records_per_slice", 100)
        always_updated: bool = config.get("always_updated", True)
        parallelism: int = config.get("parallelism", 4)

        # Create streams in order of dependency
        users = Users(count, seed, parallelism, records_per_slice, always_updated)
        products = Products(count, seed, parallelism, records_per_slice, always_updated)
        purchases = Purchases(count, seed, parallelism, records_per_slice, always_updated)

        return [users, products, purchases]
