#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from dataclasses import dataclass
from typing import Any, Mapping


from airbyte_cdk.sources.declarative.schema.schema_loader import SchemaLoader

from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.models import AirbyteMessage, AirbyteStreamStatus, FailureType, StreamDescriptor
from airbyte_cdk.models import Type as MessageType

@dataclass
class DynamicSchemaLoader(SchemaLoader):

    stream: DeclarativeStream

    def get_json_schema(self) -> Mapping[str, Any]:
        for schema_record in self.stream.read_only_records():

            if isinstance(schema_record, AirbyteMessage) and schema_record.type == MessageType.RECORD:
                schema_record = schema_record.record.data
            else:
                continue




            # if isinstance(schema_record, AirbyteMessage):
            #     if schema_record.type == MessageType.RECORD:
            #         schema_record = schema_record.record.data
            #     else:
            #         continue
            # elif isinstance(schema_record, Record):
            #     schema_record = schema_record.data

            schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": ["null", "object"],
                "additionalProperties": True,
                "properties": {
                    **schema_record,
                },
            }

            return schema
