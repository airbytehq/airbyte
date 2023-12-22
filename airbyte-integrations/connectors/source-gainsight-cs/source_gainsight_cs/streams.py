from abc import ABC
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.sources.streams.http import HttpStream


class GainsightCsStream(HttpStream, ABC):
    url_base = "https://demo-magnify.gainsightcloud.com/v1/"
    primary_key = "gsid"
    limit = 100

    @property
    def http_method(self) -> str:
        return "POST"

    def get_json_schema(self) -> Mapping[str, Any]:
        base_schema = super().get_json_schema()
        print("base_schema: ", base_schema)
        return base_schema

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def get_dates(self, stream_name):
        match stream_name:
            case "Activity_Timeline":
                return ("CreatedDate", "LastModifiedDate")
            case "Report":
                return ("CreatedAt", "ModifiedAt")
            case _:
                return ("CreatedDate", "ModifiedDate")

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def request_body_json(self, stream_state: Mapping[str, Any] | None, stream_slice: Mapping[str, Any] | None = None, next_page_token: Mapping[str, Any] | None = None) -> Mapping[str, Any] | None:
        created_date, modified_date = self.get_dates("")
        print("created_date: ", created_date)
        print("modified_date: ", modified_date)
        select_fields = ["gsid", "name", "createdDate"]
        request_body = {
          "select": select_fields,
          "limit": self.limit,
          "offset": 0
        }
        return request_body

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        records = response.json().get("data", {}).get("records", [])
        print("records: ", records)
        yield from records


class Person(GainsightCsStream):
    name = "person"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return "data/objects/query/Person"

# class Company(GainsightCsStream):
#     name = "company"

#     def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
#         return "Company"


# class User(GainsightCsStream):
#     name = "user"

#     def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
#         return "GsUser"
