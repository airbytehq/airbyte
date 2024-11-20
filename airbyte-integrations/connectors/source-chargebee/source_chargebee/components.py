#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, Iterable, Mapping, Optional, Union

from airbyte_cdk.sources.declarative.incremental import DeclarativeCursor
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOptionType
from airbyte_cdk.sources.declarative.transformations.transformation import RecordTransformation
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState


@dataclass
class CustomFieldTransformation(RecordTransformation):
    """
    Add custom field based on condition. Jinja interpolation does not support list comprehension.
    https://github.com/airbytehq/airbyte/issues/23134
    """

    def transform(
        self,
        record: Record,
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> Record:
        """
        Method to detect custom fields that start with 'cf_' from chargbee models.
        Args:
            record:
            {
                ...
                'cf_custom_fields': 'some_value',
                ...
            }

        Returns:
            record:
            {
                ...
                'custom_fields': [{
                    'name': 'cf_custom_fields',
                    'value': some_value'
                }],
                ...
            }
        """
        record["custom_fields"] = [{"name": k, "value": record.pop(k)} for k in record.copy() if k.startswith("cf_")]
        return record
