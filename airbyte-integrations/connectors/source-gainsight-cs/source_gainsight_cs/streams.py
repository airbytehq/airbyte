from abc import ABC
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.sources.streams.http import HttpStream


class GainsightCsStream(HttpStream, ABC):
    def __init__(self, domain_url: str, **kwargs):
        super().__init__(**kwargs)
        self.domain_url = f"{domain_url}/v1/"

    @property
    def url_base(self):
        return self.domain_url


class GainsightCsObjectStream(GainsightCsStream):
    primary_key = "gsid"
    limit = 100
    json_schema = None
    offset = 0

    gainsight_airbyte_type_map = {
        "STRING": ["null", "string"],
        "BOOLEAN": ["null", "boolean"],
        "NUMBER": ["null", "integer"],
        "GSID": ["null", "string"],
        "DATETIME": ["null", "string"],
        "EMAIL": ["null", "string"],
        "URL": ["null", "string"],
        "RICHTEXTAREA": ["null", "string"],
        "LOOKUP": ["null", "string"],
    }

    def __init__(self, name: str, domain_url: str, **kwargs):
        super().__init__(domain_url, **kwargs)
        self.object_name = name

    @property
    def name(self):
        return self.object_name

    def lowercase(self, field_name):
        return field_name[0].lower() + field_name[1:]

    def dynamic_schema(self, full_schema, metadata):
        for field in metadata:
            field_name = self.lowercase(field['fieldName'])
            field_type = self.gainsight_airbyte_type_map.get(field['dataType'], ["null", "string"])
            full_schema['properties'][field_name] = {
                "type": field_type
            }
        return full_schema

    @property
    def http_method(self) -> str:
        return "POST"

    def request_body_json(self, stream_state: Mapping[str, Any] | None, stream_slice: Mapping[str, Any] | None = None, next_page_token: Mapping[str, Any] | None = None) -> Mapping[str, Any] | None:
        select_columns = self.get_select_columns()
        offset = self.offset if next_page_token is None else next_page_token
        request_body = {
          "select": select_columns,
          "limit": self.limit,
          "offset": offset
        }
        return request_body

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        records = response.json().get("data", {}).get("records", [])
        yield from records

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        data = response.json().get("data", {}).get("records", [])
        if len(data) < self.limit:
            return None
        self.offset = self.offset + self.limit
        return self.offset

    def get_json_schema(self) -> Mapping[str, Any]:
        if self.json_schema is not None:
            return self.json_schema

        base_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {}
        }
        url = f"{self.url_base}meta/services/objects/{self.name}/describe?idd=true"
        auth_headers = self.authenticator.get_auth_header()

        try:
            session = requests.get(url, headers=auth_headers)
            body = session.json()
            full_schema = base_schema
            fields = body['data'][0]['fields']
            full_schema = self.dynamic_schema(full_schema, fields)
            self.json_schema = full_schema
        except requests.exceptions.RequestException:
            self.json_schema = base_schema

        return self.json_schema

    def get_select_columns(self):
        json_schema = self.get_json_schema()
        return [key for key in json_schema['properties']]

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"data/objects/query/{self.name}"
