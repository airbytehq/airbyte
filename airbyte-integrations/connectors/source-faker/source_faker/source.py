#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .streams import Products, Purchases, Users


class SourceFaker(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        if type(config["count"]) == int or type(config["count"]) == float:
            return True, None
        else:
            return False, "Count option is missing"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:

        count: int = config["count"] if "count" in config else 0
        seed: int = config["seed"] if "seed" in config else None
        records_per_sync: int = config["records_per_sync"] if "records_per_sync" in config else 500
        records_per_slice: int = config["records_per_slice"] if "records_per_slice" in config else 100

        return [
            Products(count, seed, records_per_sync, records_per_slice),
            Users(count, seed, records_per_sync, records_per_slice),
            Purchases(seed, records_per_sync, records_per_slice),
        ]
