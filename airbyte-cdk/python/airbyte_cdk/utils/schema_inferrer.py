#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Dict

from airbyte_cdk.models import AirbyteRecordMessage, Status, Type

from genson import SchemaBuilder
from genson.schema.strategies.object import Object


class NoRequiredObj(Object):
    """
    This class has Object behaviour, but it does not generate "required[]" fields
    every time it parses object. So we dont add unnecessary extra field.
    """

    def to_schema(self):
        schema = super(Object, self).to_schema()
        schema["type"] = "object"
        if self._properties:
            schema["properties"] = self._properties_to_schema(self._properties)
        if self._pattern_properties:
            schema["patternProperties"] = self._properties_to_schema(self._pattern_properties)
        return schema


class NoRequiredSchemaBuilder(SchemaBuilder):
    EXTRA_STRATEGIES = (NoRequiredObj,)


class SchemaInferrer:
   """
   This class is used to infer a JSON schema which fits all the records passed into it
   throughout its lifecycle via the accumulate method.
 
   Instances of this class are stateful, meaning they build their inferred schemas
   from every record passed into the accumulate method until the reset() method is called.
  
   """
   def __init__(self):
        self.builders = {}

   def accumulate(self, record: AirbyteRecordMessage):
       """Uses the input record to add to the inferred schema maintained by this object"""
       stream_name = record.stream
       builder = None
       if stream_name not in self.builders:
            builder = NoRequiredSchemaBuilder()
            self.builders[stream_name] = builder
       else:
            builder = self.builders[stream_name]
       builder.add_object(record.data)
 
   def get_inferred_schemas(self) -> Dict[str, Any]:
       """
       Returns the JSON schema inferred by this object by inspecting all records
       passed via the accumulate method
       """
       schemas = {}
       for stream_name, builder in self.builders.items():
          schemas[stream_name] = builder.to_schema()
       return schemas

 
   def reset(self) -> None:
       """Resets the inferred schemas, as if no records have been passed to the accumulate method"""
       self.builders = {}