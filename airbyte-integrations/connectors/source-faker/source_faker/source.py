#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, List, Mapping, Tuple

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .streams import Products, Purchases, Users


DEFAULT_COUNT = 1_000
POSITIVE_INTEGER_SETTINGS = ("count", "records_per_slice", "parallelism")


class SourceFaker(AbstractSource):
    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        # Reject settings the streams can't run with (e.g. `parallelism: 0`
        # can't start the worker pool) before a sync starts.
        for key in POSITIVE_INTEGER_SETTINGS:
            value = config.get(key, 0)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 1:
                return False, f"`{key}` must be a number greater than or equal to 1, got {value!r}"
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        count: int = config["count"] if "count" in config else DEFAULT_COUNT
        seed: int = config["seed"] if "seed" in config else None
        records_per_slice: int = config["records_per_slice"] if "records_per_slice" in config else 100
        always_updated: bool = config["always_updated"] if "always_updated" in config else True
        parallelism: int = config["parallelism"] if "parallelism" in config else 4

        return [
            Products(count, seed, parallelism, records_per_slice, always_updated),
            Users(count, seed, parallelism, records_per_slice, always_updated),
            Purchases(count, seed, parallelism, records_per_slice, always_updated),
        ]
