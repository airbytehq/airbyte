from abc import ABC
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.sources.streams.http import HttpStream


class GainsightCsStream(HttpStream, ABC):
    url_base = "https://demo-magnify.gainsightcloud.com/v1/"

    def get_dates(self, stream_name):
        match stream_name:
            case "Activity_Timeline":
                return ("CreatedDate", "LastModifiedDate")
            case "Report":
                return ("CreatedAt", "ModifiedAt")
            case _:
                return ("CreatedDate", "ModifiedDate")


class GainsightCsObjectStream(GainsightCsStream):
    primary_key = "gsid"
    limit = 100
    json_schema = None

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
        created_date, modified_date = self.get_dates("")
        select_columns = self.get_select_columns()
        request_body = {
          "select": select_columns,
          "limit": self.limit,
          "offset": 0
        }
        return request_body

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        records = response.json().get("data", {}).get("records", [])
        yield from records

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def get_json_schema(self) -> Mapping[str, Any]:
        if self.json_schema is not None:
            return self.json_schema

        base_schema = super().get_json_schema()
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


class Person(GainsightCsObjectStream):
    name = "person"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return "data/objects/query/Person"


class Company(GainsightCsObjectStream):
    name = "company"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return "data/objects/query/Company"


class User(GainsightCsObjectStream):
    name = "user"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return "data/objects/query/GsUser"
