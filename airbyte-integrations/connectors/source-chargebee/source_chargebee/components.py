#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import List, Optional

import dpath.util
import requests
from airbyte_cdk.sources.declarative.extractors.dpath_extractor import DpathExtractor
from airbyte_cdk.sources.declarative.transformations.transformation import RecordTransformation
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState


# TODO: Remove after CDK changes are merged
@dataclass
class NestedDpathExtractor(DpathExtractor):
    """
    Record extractor that searches a decoded response over a path defined as an array of fields.

    Extends the DpathExtractor to allow for a list of records to be generated from a dpath that points
    to an array object as first point and iterates over list of records by the rest of path. See the example.

    Example data:
    ```
    {
        "list": [
            {"item": {
                "id": "id1",
                "name": "name1",
                ...
                },
            {"item": {
                "id": "id2",
                "name": "name2",
                ...
                }
                ...
            ...
        ]
    }
    ```
    """

    def extract_records(self, response: requests.Response) -> List[Record]:
        response_body = self.decoder.decode(response)
        if len(self.field_pointer) == 0:
            extracted = response_body
        else:
            pointer = [pointer.eval(self.config) for pointer in self.field_pointer]
            extracted = dpath.util.values(response_body, pointer)
        if isinstance(extracted, list):
            return extracted
        elif extracted:
            return [extracted]
        else:
            return []


@dataclass
class CustomFieldTransformation(RecordTransformation):
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
        record["custom_fields"] = [{"name": k, "value": v} for k, v in record.items() if k.startswith("cf_")]
        return record
