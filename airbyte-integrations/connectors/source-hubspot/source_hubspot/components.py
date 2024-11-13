#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from copy import deepcopy
from typing import Any, Dict, Optional

from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.types import Config, StreamSlice, StreamState

NEW_TO_LEGACY_FIELDS_MAPPING = {
    "hs_lifecyclestage_": "hs_v2_date_entered_",
    "hs_date_entered_": "hs_v2_date_entered_",
    "hs_date_exited_": "hs_v2_date_exited_",
    "hs_time_in": "hs_v2_latest_time_in_",
}


class NewtoLegacyFieldTransformation(RecordTransformation):
    """
    Implements a custom transformation which maps a "new" field to the legacy equivalent of the field for streams which contain Deals and Contacts entities.
    """

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
        updated_record = deepcopy(record)

        for field, value in record.get("properties", record).items():
            for legacy_field, new_field in NEW_TO_LEGACY_FIELDS_MAPPING.items():
                if new_field in field:
                    transformed_field = field.replace(new_field, legacy_field)
                    if legacy_field == "hs_lifecyclestage_":
                        transformed_field += "_date"
                    if updated_record.get("properties", updated_record).get(transformed_field) is None:
                        if updated_record.get("properties"):
                            updated_record["properties"][transformed_field] = value
                        else:
                            updated_record[transformed_field] = value
        return updated_record
