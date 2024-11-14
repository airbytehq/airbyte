#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from copy import deepcopy
from typing import Any, Dict, Optional

from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.types import Config, StreamSlice, StreamState


class NewtoLegacyFieldTransformation(RecordTransformation):
    """
    Implements a custom transformation which maps a "new" field to the legacy equivalent of the field for streams which contain Deals and Contacts entities.
    """

    def __init__(self, field_mapping: Dict[str, str]) -> None:
        self._field_mapping = field_mapping

    def transform(
        self,
        record: Dict[str, Any],
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> Dict[str, Any]:
        """
        Transform a record by adding fields directly to the record by manipulating a "new" field into a legacy field to avoid breaking syncs.

        :param record: The input record to be transformed
        :param config: The user-provided configuration as specified by the source's spec
        :param stream_state: The stream state
        :param stream_slice: The stream slice
        :return: The transformed record
        """
        record_copy = deepcopy(record)

        for field, value in record.get("properties", record).items():
            for legacy_field, new_field in self._field_mapping.items():
                if new_field in field:
                    transformed_field = field.replace(new_field, legacy_field)

                    if legacy_field == "hs_lifecyclestage_" and not transformed_field.endswith("_date"):
                        transformed_field += "_date"

                    if record_copy.get("properties") is not None:
                        if record_copy.get("properties", {}).get(transformed_field) is None:
                            record_copy["properties"][transformed_field] = value
                    elif record_copy.get(transformed_field) is None:
                        record_copy[transformed_field] = value
        return record_copy
