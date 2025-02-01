#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

# Dummy change to verify CI status
import logging
from collections.abc import Mapping
from typing import Any

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .streams import Products, Purchases, Users


DEFAULT_COUNT = 1_000


class SourceFaker(AbstractSource):
    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> tuple[bool, Any]:
        try:
            if not isinstance(config.get("count"), (int, float)):
                return False, "Count option is missing"

            # First check basic config
            if not isinstance(config.get("count"), (int, float)):
                return False, "Count option is missing"

            # Check if catalog is provided (for testing purposes)
            if "catalog" in config:
                catalog = config["catalog"]
                stream_names = {stream.stream.name for stream in catalog.streams}
                if "purchases" in stream_names and "users" not in stream_names:
                    return False, "Cannot sync purchases without users"
                
            return True, None
        except Exception as e:
            return False, str(e)

    def streams(self, config: Mapping[str, Any]) -> list[Stream]:
        count: int = config["count"] if "count" in config else DEFAULT_COUNT
        seed: int | None = config["seed"] if "seed" in config else None
        records_per_slice: int = config["records_per_slice"] if "records_per_slice" in config else 100
        always_updated: bool = config["always_updated"] if "always_updated" in config else True
        parallelism: int = config["parallelism"] if "parallelism" in config else 4

        # Default to 0 if seed is None to maintain compatibility
        seed_value = seed if seed is not None else 0
        return [
            Products(count, seed_value, parallelism, records_per_slice, always_updated),
            Users(count, seed_value, parallelism, records_per_slice, always_updated),
            Purchases(count, seed_value, parallelism, records_per_slice, always_updated),
        ]
