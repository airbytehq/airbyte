#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass, field
from typing import Any, List, Mapping, Optional, Union

import dpath.util
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.declarative.types import Config, FieldPointer, Record, StreamSlice, StreamState
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass(frozen=True)
class AddedFieldDefinition:
    """Defines the field to add on a record"""

    path: FieldPointer
    value: Union[InterpolatedString, str]
    options: InitVar[Mapping[str, Any]]


@dataclass(frozen=True)
class ParsedAddFieldDefinition:
    """Defines the field to add on a record"""

    path: FieldPointer
    value: InterpolatedString
    options: InitVar[Mapping[str, Any]]


@dataclass
class AddFields(RecordTransformation, JsonSchemaMixin):
    """
    Transformation which adds field to an output record. The path of the added field can be nested. Adding nested fields will create all
    necessary parent objects (like mkdir -p). Adding fields to an array will extend the array to that index (filling intermediate
    indices with null values). So if you add a field at index 5 to the array ["value"], it will become ["value", null, null, null, null,
    "new_value"].


    This transformation has access to the following contextual values:
        record: the record about to be output by the connector
        config: the input configuration provided to a connector
        stream_state: the current state of the stream
        stream_slice: the current stream slice being read



    Examples of instantiating this transformation via YAML:
    - type: AddFields
      fields:
        # hardcoded constant
        - path: ["path"]
          value: "static_value"

        # nested path
        - path: ["path", "to", "field"]
          value: "static"

        # from config
        - path: ["shop_id"]
          value: "{{ config.shop_id }}"

        # from state
        - path: ["current_state"]
          value: "{{ stream_state.cursor_field }}" # Or {{ stream_state['cursor_field'] }}

        # from record
        - path: ["unnested_value"]
          value: {{ record.nested.field }}

        # from stream_slice
        - path: ["start_date"]
          value: {{ stream_slice.start_date }}

        # by supplying any valid Jinja template directive or expression https://jinja.palletsprojects.com/en/3.1.x/templates/#
        - path: ["two_times_two"]
          value: {{ 2 * 2 }}

    Attributes:
        fields (List[AddedFieldDefinition]): A list of transformations (path and corresponding value) that will be added to the record
    """

    fields: List[AddedFieldDefinition]
    options: InitVar[Mapping[str, Any]]
    _parsed_fields: List[ParsedAddFieldDefinition] = field(init=False, repr=False, default_factory=list)

    def __post_init__(self, options: Mapping[str, Any]):
        for add_field in self.fields:
            if len(add_field.path) < 1:
                raise f"Expected a non-zero-length path for the AddFields transformation {add_field}"

            if not isinstance(add_field.value, InterpolatedString):
                if not isinstance(add_field.value, str):
                    raise f"Expected a string value for the AddFields transformation: {add_field}"
                else:
                    self._parsed_fields.append(
                        ParsedAddFieldDefinition(
                            add_field.path, InterpolatedString.create(add_field.value, options=options), options=options
                        )
                    )
            else:
                self._parsed_fields.append(ParsedAddFieldDefinition(add_field.path, add_field.value, options={}))

    def transform(
        self,
        record: Record,
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> Record:
        kwargs = {"record": record, "stream_state": stream_state, "stream_slice": stream_slice}
        for parsed_field in self._parsed_fields:
            value = parsed_field.value.eval(config, **kwargs)
            dpath.util.new(record, parsed_field.path, value)

        return record

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
