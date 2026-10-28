#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, List, Mapping, Tuple

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .streams import Products, Purchases, Users


DEFAULT_CONFIG = {"count": 1_000, "seed": -1, "records_per_slice": 1_000, "always_updated": True, "parallelism": 4}
POSITIVE_INTEGER_SETTINGS = ("count", "records_per_slice", "parallelism")


class SourceFaker(AbstractSource):
    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        # Reject settings the streams can't run with (e.g. `parallelism: 0`
        # can't start the worker pool) before a sync starts.
        for key in POSITIVE_INTEGER_SETTINGS:
            value = config.get(key, DEFAULT_CONFIG[key])
            if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 1:
                return False, f"`{key}` must be a number greater than or equal to 1, got {value!r}"
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config = {**DEFAULT_CONFIG, **config}
        count: int = config["count"]
        seed: int = config["seed"]
        records_per_slice: int = config["records_per_slice"]
        always_updated: bool = config["always_updated"]
        parallelism: int = config["parallelism"]

        return [
            Products(count, seed, parallelism, records_per_slice, always_updated),
            Users(count, seed, parallelism, records_per_slice, always_updated),
            Purchases(count, seed, parallelism, records_per_slice, always_updated),
        ]
