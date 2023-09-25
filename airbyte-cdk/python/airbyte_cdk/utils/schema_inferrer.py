#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from collections import defaultdict
from typing import Any, Dict, Mapping, Optional

from airbyte_cdk.models import AirbyteRecordMessage
from genson import SchemaBuilder, SchemaNode
from genson.schema.strategies.object import Object
from genson.schema.strategies.scalar import Number


class NoRequiredObj(Object):
    """
    This class has Object behaviour, but it does not generate "required[]" fields
    every time it parses object. So we dont add unnecessary extra field.
    """

    def to_schema(self) -> Mapping[str, Any]:
        schema: Dict[str, Any] = super(NoRequiredObj, self).to_schema()
        schema.pop("required", None)
        return schema


class IntegerToNumber(Number):
    """
    This class has the regular Number behaviour, but it will never emit an integer type.
    """

    def __init__(self, node_class: SchemaNode):
        super().__init__(node_class)
        self._type = "number"


class NoRequiredSchemaBuilder(SchemaBuilder):
    EXTRA_STRATEGIES = (NoRequiredObj, IntegerToNumber)


# This type is inferred from the genson lib, but there is no alias provided for it - creating it here for type safety
InferredSchema = Dict[str, Any]


class SchemaInferrer:
    """
    This class is used to infer a JSON schema which fits all the records passed into it
    throughout its lifecycle via the accumulate method.

    Instances of this class are stateful, meaning they build their inferred schemas
    from every record passed into the accumulate method.

    """

    stream_to_builder: Dict[str, SchemaBuilder]

    def __init__(self) -> None:
        self.stream_to_builder = defaultdict(NoRequiredSchemaBuilder)

    def accumulate(self, record: AirbyteRecordMessage) -> None:
        """Uses the input record to add to the inferred schemas maintained by this object"""
        self.stream_to_builder[record.stream].add_object(record.data)

    def get_inferred_schemas(self) -> Dict[str, InferredSchema]:
        """
        Returns the JSON schemas for all encountered streams inferred by inspecting all records
        passed via the accumulate method
        """
        schemas = {}
        for stream_name, builder in self.stream_to_builder.items():
            schemas[stream_name] = self._clean(builder.to_schema())
        return schemas

    def _clean(self, node: InferredSchema) -> InferredSchema:
        """
        Recursively cleans up a produced schema:
        - remove anyOf if one of them is just a null value
        - remove properties of type "null"
        """
        if isinstance(node, dict):
            if "anyOf" in node:
                if len(node["anyOf"]) == 2 and {"type": "null"} in node["anyOf"]:
                    real_type = node["anyOf"][1] if node["anyOf"][0]["type"] == "null" else node["anyOf"][0]
                    node.update(real_type)
                    node["type"] = [node["type"], "null"]
                    node.pop("anyOf")
            if "properties" in node and isinstance(node["properties"], dict):
                for key, value in list(node["properties"].items()):
                    if isinstance(value, dict) and value.get("type", None) == "null":
                        node["properties"].pop(key)
                    else:
                        self._clean(value)
            if "items" in node:
                self._clean(node["items"])
        return node

    def get_stream_schema(self, stream_name: str) -> Optional[InferredSchema]:
        """
        Returns the inferred JSON schema for the specified stream. Might be `None` if there were no records for the given stream name.
        """
        return self._clean(self.stream_to_builder[stream_name].to_schema()) if stream_name in self.stream_to_builder else None
