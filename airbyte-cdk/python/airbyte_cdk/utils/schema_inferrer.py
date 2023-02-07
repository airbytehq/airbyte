#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from collections import defaultdict
from typing import Any, Dict, List, Optional, Union

from airbyte_cdk.models import AirbyteRecordMessage
from genson import SchemaBuilder
from genson.schema.strategies.object import Object


class NoRequiredObj(Object):
    """
    This class has Object behaviour, but it does not generate "required[]" fields
    every time it parses object. So we dont add unnecessary extra field.
    """

    def to_schema(self):
        schema = super(NoRequiredObj, self).to_schema()
        schema.pop("required", None)
        return schema


class NoRequiredSchemaBuilder(SchemaBuilder):
    EXTRA_STRATEGIES = (NoRequiredObj,)


# This type is inferred from the genson lib, but there is no alias provided for it - creating it here for type safety
InferredSchema = Dict[str, Union[str, Any, List, List[Dict[str, Union[Any, List]]]]]


class SchemaInferrer:
    """
    This class is used to infer a JSON schema which fits all the records passed into it
    throughout its lifecycle via the accumulate method.

    Instances of this class are stateful, meaning they build their inferred schemas
    from every record passed into the accumulate method.

    """

    stream_to_builder: Dict[str, SchemaBuilder]

    def __init__(self):
        self.stream_to_builder = defaultdict(NoRequiredSchemaBuilder)

    def accumulate(self, record: AirbyteRecordMessage):
        """Uses the input record to add to the inferred schemas maintained by this object"""
        self.stream_to_builder[record.stream].add_object(record.data)

    def get_inferred_schemas(self) -> Dict[str, InferredSchema]:
        """
        Returns the JSON schemas for all encountered streams inferred by inspecting all records
        passed via the accumulate method
        """
        schemas = {}
        for stream_name, builder in self.stream_to_builder.items():
            schemas[stream_name] = builder.to_schema()
        return schemas

    def get_stream_schema(self, stream_name: str) -> Optional[InferredSchema]:
        """
        Returns the inferred JSON schema for the specified stream. Might be `None` if there were no records for the given stream name.
        """
        return self.stream_to_builder[stream_name].to_schema() if stream_name in self.stream_to_builder else None
