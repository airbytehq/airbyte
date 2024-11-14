#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import Any, Dict, Optional

from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.types import Config, StreamSlice, StreamState


class NewtoLegacyFieldTransformation(RecordTransformation):
    """
    Implements a custom transformation which adds the legacy field equivalent of v2 fields for streams which contain Deals and Contacts entities.
    """

    def __init__(self, field_mapping: Dict[str, str]) -> None:
        self._field_mapping = field_mapping

    def transform(
        self,
        record: Dict[str, Any],
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> None:
        """
        Transform a record in place by adding fields directly to the record by manipulating the injected fields into a legacy field to avoid breaking syncs.

        :param record: The input record to be transformed
        """
        for field, value in list(record.get("properties", record).items()):
            for legacy_field, new_field in self._field_mapping.items():
                if new_field in field:
                    transformed_field = field.replace(new_field, legacy_field)

                    if legacy_field == "hs_lifecyclestage_" and not transformed_field.endswith("_date"):
                        transformed_field += "_date"

                    if record.get("properties") is not None:
                        if record["properties"].get(transformed_field) is None:
                            record["properties"][transformed_field] = value
                    elif record.get(transformed_field) is None:
                        record[transformed_field] = value
