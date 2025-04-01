# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
from dataclasses import dataclass
from typing import Any, MutableMapping, Optional

from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.declarative.types import Config


@dataclass
class MondayTransformation(RecordTransformation):
    def transform(self, record: MutableMapping[str, Any], config: Optional[Config] = None, **kwargs) -> MutableMapping[str, Any]:
        # Oncall issue: https://github.com/airbytehq/oncall/issues/4337
        column_values = record.get("column_values", [])
        for values in column_values:
            display_value, text = values.get("display_value"), values.get("text")
            if display_value and not text:
                values["text"] = display_value

        return record
