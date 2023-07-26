from jinja2 import Template

from datetime import datetime
from typing import Generator

from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    Type,
)
from source_adaptive.adaptive.base import Adaptive
from airbyte_cdk.sources import Source
from datetime import datetime


class AdaptiveExportAttributes(Adaptive):
    def construct_payload(self) -> Generator[str, None, None]:
        yield self.construct_payload_fast()

    def construct_payload_fast(self) -> str:
        """
        Generate the xml that is sent to the request using jinja templating
        """

        TEMPLATE = """<?xml version='1.0' encoding='UTF-8'?>
        <call method="{{method_obj["method"]}}" callerName="Airbyte - auto">
            <credentials login="{{username}}" password="{{password}}"/>
        </call>"""

        payload = Template(TEMPLATE).render(**self.config)
        return payload

    def generate_table_name(self):
        return "exportAttributes"

    def generate_table_schema(self):
        json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "autoCreate": {"type": "string"},
                "keepSorted": {"type": "string"},
                "type": {"type": "string"},
                "dimension_id": {"type": "string"},
                "seq_no": {"type": "string"},
                "parent_id": {"type": "string"}
                },
        }

        return json_schema

    def parse_attribute_row(self,data_obj,parent_obj):

        data = {"id": data_obj.get("@id"),
                "name": data_obj.get("@name"),
                "autoCreate": data_obj.get("@autoCreate"),
                "keepSorted": data_obj.get("@keepSorted"),
                "type": data_obj.get("@type"),
                "dimension_id": data_obj.get("@dimension-id"),
                "seq_no": data_obj.get("@seqNo"),
                "parent_id": parent_obj.get("parent_id")
                }

        yield AirbyteMessage(
            type=Type.RECORD,
            record=AirbyteRecordMessage(
                stream=self.generate_table_name(), data=data, emitted_at=int(datetime.now().timestamp()) * 1000
            ),
        )
        parent_obj={ "parent_id":data["id"] }
        if "attributeValue" in data_obj:
            children = data_obj["attributeValue"]

            if isinstance(children,list):
                for record_found in children:
                    yield from self.parse_attribute_row(data_obj=record_found,parent_obj=parent_obj)


    def generate_table_row(self) -> Generator[AirbyteMessage, None, None]:

        for response in self.perform_request():
            response_data = self.get_data_from_response(response)
            for row in response_data["attributes"]["attribute"]:
                print(row)
                yield from self.parse_attribute_row(data_obj=row,parent_obj={})

