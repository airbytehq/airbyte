#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from dataclasses import dataclass
from typing import Any, Mapping


from airbyte_cdk.sources.declarative.schema.schema_loader import SchemaLoader


from airbyte_cdk.models import AirbyteMessage, AirbyteStreamStatus, FailureType, StreamDescriptor
from airbyte_cdk.models import Type as MessageType

from airbyte_cdk.sources.declarative.requesters.requester import Requester


@dataclass
class DynamicSchemaLoader(SchemaLoader):
    schema_requester: Requester

    def get_json_schema(self) -> Mapping[str, Any]:
        response = self.schema_requester.send_request()
        response_json = response.json()
        fields = response_json['values'][0]

        json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            # For simplicity, the type of every cell is a string
            "properties": {field: {"type": "string"} for field in fields},
        }

        return json_schema
