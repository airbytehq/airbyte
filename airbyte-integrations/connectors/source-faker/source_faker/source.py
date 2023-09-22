#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .streams import Products, Purchases, Users, WideColumns


class SourceFaker(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        if type(config["count"]) == int or type(config["count"]) == float:
            return True, None
        else:
            return False, "Count option is missing"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        count: int = config["count"] if "count" in config else 0
        seed: int = config["seed"] if "seed" in config else None
        records_per_slice: int = config["records_per_slice"] if "records_per_slice" in config else 100
        always_updated: bool = config["always_updated"] if "always_updated" in config else True
        parallelism: int = config["parallelism"] if "parallelism" in config else 4
        wide_data_set_columns: int = config["wide_data_set_columns"] if "wide_data_set_columns" in config else 10
        wide_data_set_tables: int = config["wide_data_set_tables"] if "wide_data_set_tables" in config else 1
        generate_errors_in_wide_columns: bool = (
            config["generate_errors_in_wide_columns"] if "generate_errors_in_wide_columns" in config else False
        )

        return [
            Products(count, seed, parallelism, records_per_slice, always_updated),
            Users(count, seed, parallelism, records_per_slice, always_updated),
            Purchases(count, seed, parallelism, records_per_slice, always_updated),
            *[
                WideColumns(
                    count, seed, parallelism, records_per_slice, always_updated, wide_data_set_columns, generate_errors_in_wide_columns, i
                )
                for i in range(wide_data_set_tables)
            ],
        ]
