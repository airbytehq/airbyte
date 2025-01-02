#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import Any, Dict, Optional

from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.types import Config, StreamSlice, StreamState


class NewtoLegacyFieldTransformation(RecordTransformation):
    """
    Implements a custom transformation which adds the legacy field equivalent of v2 fields for streams which contain Deals and Contacts entities.

    This custom implmentation was developed in lieu of the AddFields component due to the dynamic-nature of the record properties for the HubSpot source. Each

    For example:
    hs_v2_date_exited_{stage_id} -> hs_date_exited_{stage_id} where {stage_id} is a user-generated value
    """

    def __init__(self, field_mapping: Dict[str, str]) -> None:
        self._field_mapping = field_mapping

    def transform(
        self,
        record_or_schema: Dict[str, Any],
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> None:
        """
        Transform a record in place by adding fields directly to the record by manipulating the injected fields into a legacy field to avoid breaking syncs.

        :param record_or_schema: The input record or schema to be transformed.
        """
        is_record = record_or_schema.get("properties") is not None

        for field, value in list(record_or_schema.get("properties", record_or_schema).items()):
            for legacy_field, new_field in self._field_mapping.items():
                if new_field in field:
                    transformed_field = field.replace(new_field, legacy_field)

                    if legacy_field == "hs_lifecyclestage_" and not transformed_field.endswith("_date"):
                        transformed_field += "_date"

                    if is_record:
                        if record_or_schema["properties"].get(transformed_field) is None:
                            record_or_schema["properties"][transformed_field] = value
                    else:
                        if record_or_schema.get(transformed_field) is None:
                            record_or_schema[transformed_field] = value
