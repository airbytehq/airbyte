#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, List, Mapping, Tuple

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .streams import Products, Purchases, Users


DEFAULT_COUNT = 1_000
# Values used when a setting is omitted from the config (e.g. sources created
# through the API, which doesn't fill in spec defaults). `check_connection` and
# `streams` must agree on these so check validates what a sync will really use.
DEFAULT_SETTINGS: Mapping[str, Any] = {
    "count": DEFAULT_COUNT,
    "seed": None,
    "records_per_slice": 100,
    "always_updated": True,
    "parallelism": 4,
}
POSITIVE_INTEGER_SETTINGS = ("count", "records_per_slice", "parallelism")


def _setting(config: Mapping[str, Any], key: str) -> Any:
    return config[key] if key in config else DEFAULT_SETTINGS[key]


class SourceFaker(AbstractSource):
    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        # Reject settings the streams can't run with (e.g. `parallelism: 0`
        # can't start the worker pool) before a sync starts.
        for key in POSITIVE_INTEGER_SETTINGS:
            value = _setting(config, key)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 1:
                return False, f"`{key}` must be a number greater than or equal to 1, got {value!r}"
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        count: int = _setting(config, "count")
        seed: int = _setting(config, "seed")
        records_per_slice: int = _setting(config, "records_per_slice")
        always_updated: bool = _setting(config, "always_updated")
        parallelism: int = _setting(config, "parallelism")

        return [
            Products(count, seed, parallelism, records_per_slice, always_updated),
            Users(count, seed, parallelism, records_per_slice, always_updated),
            Purchases(count, seed, parallelism, records_per_slice, always_updated),
        ]
