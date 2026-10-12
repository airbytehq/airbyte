#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, List, Mapping, Tuple

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .streams import Products, Purchases, Users


POSITIVE_INTEGER_DEFAULTS = {"count": 1_000, "records_per_slice": 100, "parallelism": 4}


class SourceFaker(AbstractSource):
    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        # Reject settings the streams can't run with (e.g. `parallelism: 0`
        # can't start the worker pool) before a sync starts. Omitted settings
        # fall back to the same defaults the streams use.
        for key, default in POSITIVE_INTEGER_DEFAULTS.items():
            value = config.get(key, default)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 1:
                return False, f"`{key}` must be a number greater than or equal to 1, got {value!r}"
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        count: int = config.get("count", POSITIVE_INTEGER_DEFAULTS["count"])
        seed: int = config["seed"] if "seed" in config else None
        records_per_slice: int = config.get("records_per_slice", POSITIVE_INTEGER_DEFAULTS["records_per_slice"])
        always_updated: bool = config["always_updated"] if "always_updated" in config else True
        parallelism: int = config.get("parallelism", POSITIVE_INTEGER_DEFAULTS["parallelism"])

        return [
            Products(count, seed, parallelism, records_per_slice, always_updated),
            Users(count, seed, parallelism, records_per_slice, always_updated),
            Purchases(count, seed, parallelism, records_per_slice, always_updated),
        ]
