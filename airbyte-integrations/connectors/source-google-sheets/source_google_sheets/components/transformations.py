# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional, Type, Union

import dpath
from airbyte_cdk.sources.declarative.transformations.add_fields import AddFields
from airbyte_cdk.sources.types import Config, StreamSlice, StreamState


@dataclass
class AddIndexedPropertiesFromList(AddFields):
    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)
        self._key_to_extract = parameters["key_to_extract"]

    def transform(
        self,
        record: Dict[str, Any],
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> None:
        if config is None:
            config = {}
        kwargs = {"record": record, "stream_state": stream_state, "stream_slice": stream_slice}
        for parsed_field in self._parsed_fields:
            valid_types = (parsed_field.value_type,) if parsed_field.value_type else None
            items_for_extraction = parsed_field.value.eval(config, valid_types=valid_types, **kwargs)
            if not isinstance(items_for_extraction, list):
                raise Exception("Transformation is expected to  occur on a list.")
            indexed_properties = {
                index: item_for_extraction[self._key_to_extract] for index, item_for_extraction in enumerate(items_for_extraction)
            }
            dpath.new(record, parsed_field.path, indexed_properties)
