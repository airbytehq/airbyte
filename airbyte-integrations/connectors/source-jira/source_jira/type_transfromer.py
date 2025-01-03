#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from datetime import datetime
from typing import Any, Dict

from airbyte_cdk.sources.utils.transform import TypeTransformer


logger = logging.getLogger("airbyte")


class DateTimeTransformer(TypeTransformer):
    api_date_time_format = "%Y-%m-%dT%H:%M:%S.%f%z"

    @staticmethod
    def default_convert(original_item: Any, subschema: Dict[str, Any]) -> Any:
        target_format = subschema.get("format", "")
        if target_format == "date-time":
            if isinstance(original_item, str):
                try:
                    date = datetime.strptime(original_item, DateTimeTransformer.api_date_time_format)
                    return date.isoformat()
                except ValueError:
                    logger.warning(f"{original_item}: doesn't match expected format.")
                    # returning original item in case we received another date format
                    return original_item
        # we don't need to convert other types
        return original_item
