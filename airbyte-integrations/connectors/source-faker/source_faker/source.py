#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os

import logging
from typing import Any, List, Mapping, Tuple

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .streams import Products, Purchases, Users


DEFAULT_COUNT = 1_000

REQUIRED_PRODUCT_FIELDS = {"id", "make", "model", "year", "price", "created_at", "updated_at"}


class SourceFaker(AbstractSource):
    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        if type(config["count"]) == int or type(config["count"]) == float:
            dirname = os.path.dirname(os.path.realpath(__file__))
            from .utils import read_json

            products = read_json(os.path.join(dirname, "record_data", "products.json"))
            if products:
                sample = products[0]
                missing = REQUIRED_PRODUCT_FIELDS - set(sample.keys())
                if missing:
                    return False, f"Product data schema validation failed: missing fields {missing}."

            return True, None
        else:
            return False, "Count option is missing"

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
