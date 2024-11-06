#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
import copy
from typing import Any, Dict, List, Mapping, Optional, Union

from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.types import Config, StreamSlice, StreamState

NEW_TO_LEGACY_FIELDS_MAPPING = {
    "hs_lifecyclestage_": "hs_v2_date_entered_",
    "hs_date_entered_": "hs_v2_date_entered_",
    "hs_date_exited_": "hs_v2_date_exited_",
    "hs_time_in_": "h2_v2_latest_time_in_",
}


class NewToLegacyFieldTransformation(RecordTransformation):
    def transform(
        self,
        record: Dict[str, Any],
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> Mapping[str, Any]:
        updated_record = copy.deepcopy(record)
        for field_name, field_value in record.get("properties", {}).items():
            for legacy_field_prefix, new_field_prefix in NEW_TO_LEGACY_FIELDS_MAPPING.items():
                if new_field_prefix in field_name:
                    updated_field_name = field_name.replace(new_field_prefix, legacy_field_prefix)
                    if legacy_field_prefix == "hs_lifecyclestage_":
                        updated_field_name += "_date"
                    updated_record["properties"][updated_field_name] = field_value

        return updated_record
