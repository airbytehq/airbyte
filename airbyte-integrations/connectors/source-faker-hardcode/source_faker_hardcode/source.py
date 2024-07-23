#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, List, Mapping, Tuple

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .streams import Countries, Orders

DEFAULT_COUNT = 1_000


class SourceFakerHardcode(AbstractSource):
    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        if type(config["count"]) == int or type(config["count"]) == float:
            return True, None
        else:
            return False, "Count option is missing"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        count: int = config["count"] if "count" in config else DEFAULT_COUNT

        return [Countries(count), Orders(count)]
