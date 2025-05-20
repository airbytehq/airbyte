# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


import logging
from typing import Any, List, Mapping, Tuple

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .streams import Customers, DummyFields, Products


DEFAULT_COUNT = 1_000


class SourceHardcodedRecords(AbstractSource):
    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        if "count" not in config:
            return False, "Config option `count` is missing."

        if type(config["count"]) == int or type(config["count"]) == float:
            if config["count"] < 0:
                return False, "Config option `count` cannot be negative."

            return True, None

        else:
            return False, "Config option `count` is missing"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        count: int = config["count"] if "count" in config else DEFAULT_COUNT

        return [Products(count), Customers(count), DummyFields(count)]
