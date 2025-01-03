#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Any, Mapping, Union

import dpath.util
import requests

from airbyte_cdk.sources.declarative.extractors.dpath_extractor import DpathExtractor
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.types import Record


@dataclass
class ObjectDpathExtractor(DpathExtractor):
    """
    Record extractor that searches a decoded response over a path defined as an array of fields.

    Extends the DpathExtractor to allow for a list of records to be generated from a dpath that points
    to an object, where the object's values are individual records.

    Example data:
    ```
    {
        "data": {
            "2022-01-01": {
                "id": "id1",
                "name": "name1",
                ...
            },
            "2022-01-02": {
                "id": "id2",
                "name": "name2",
                ...
            },
            ...
    }
    ```

    There is an optional `inject_key_as_field` parameter that can be used to inject the key of the object
    as a field in the record. For example, if `inject_key_as_field` is set to `date`, the above data would
    be transformed to:
    ```
    [
        {
            "date": "2022-01-01",
            "id": "id1",
            "name": "name1",
            ...
        },
        {
            "date": "2022-01-02",
            "id": "id2",
            "name": "name2",
            ...
        },
        ...
    ]
    """

    inject_key_as_field: Union[str, InterpolatedString] = None

    def __post_init__(self, parameters: Mapping[str, Any]):
        self.inject_key_as_field = InterpolatedString.create(self.inject_key_as_field, parameters=parameters)
        for path_index in range(len(self.field_path)):
            if isinstance(self.field_path[path_index], str):
                self.field_path[path_index] = InterpolatedString.create(self.field_path[path_index], parameters=parameters)

    def extract_records(self, response: requests.Response) -> list[Record]:
        response_body = self.decoder.decode(response)
        if len(self.field_path) == 0:
            extracted = response_body
        else:
            path = [path.eval(self.config) for path in self.field_path]
            extracted = dpath.util.get(response_body, path, default=[])
        if isinstance(extracted, list):
            return extracted
        elif isinstance(extracted, dict) and all(isinstance(v, dict) for v in extracted.values()):  # Ensure object is dict[Hashable, dict]
            if not self.inject_key_as_field:
                return [value for _, value in extracted.items()]
            else:
                key_field = self.inject_key_as_field.eval(self.config)
                return [{key_field: key, **value} for key, value in extracted.items()]
        elif extracted:
            return [extracted]
        else:
            return []
