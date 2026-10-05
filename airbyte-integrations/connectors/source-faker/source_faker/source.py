#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from multiprocessing import Pool
from typing import Any, List, Mapping, Tuple

from airbyte_cdk.config_observation import emit_configuration_as_airbyte_control_message
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .streams import Products, Purchases, Users


DEFAULT_COUNT = 1_000


class SourceFaker(AbstractSource):
    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        parallelism: int = config["parallelism"] if "parallelism" in config else 4
        try:
            pool = Pool(processes=parallelism)
            pool.close()
            pool.join()
            config["parallelism"] = parallelism
            emit_configuration_as_airbyte_control_message(config)
            logger.info(f"Worker pool preflight passed (parallelism={parallelism})")
        except OSError as error:
            return False, f"Cannot allocate worker pool (parallelism={parallelism}): {error}. Reduce the parallelism setting."

        if type(config["count"]) == int or type(config["count"]) == float:
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
