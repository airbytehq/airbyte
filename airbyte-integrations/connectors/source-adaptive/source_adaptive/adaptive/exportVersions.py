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


class AdaptiveExportVersions(Adaptive):
    def construct_payload(self)->Generator[str,None,None]:
        yield self.construct_payload_fast()

    def construct_payload_fast(self)->str:
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
        return "exportVersions"

    def generate_table_schema(self):
        json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {"id": {"type": "string"}, "name": {"type": "string"}},
        }

        return json_schema

    def generate_table_row(self) -> Generator[AirbyteMessage, None, None]:

        for response in self.perform_request():
            response_data = self.get_data_from_response(response)

            for row in response_data["versions"]["version"]:
                data = {"id": row["@id"], "name": row["@name"]}

                yield AirbyteMessage(
                    type=Type.RECORD,
                    record=AirbyteRecordMessage(
                        stream=self.generate_table_name(), data=data, emitted_at=int(datetime.now().timestamp()) * 1000
                    ),
                )
