from abc import ABC
from datetime import date
from typing import Any, Iterable, List, Mapping, Optional
import requests
from source_close_com.authenticator import Base64HttpAuthenticator
from airbyte_cdk.sources.streams.http import HttpStream
import logging
from source_close_com.utils import generate_custom_object_search_query, get_data_type
from source_close_com.constants import COMMON_FIELDS, CUSTOM_FIELD_PREFIX

logger = logging.getLogger("airbyte")

BASE_URL = "https://api.close.com/api/v1/"
SEARCH_PATH = "data/search/"
CUSTOM_OBJECT_TYPE_URL = f"{BASE_URL}/custom_object_type"


class CustomObjectStream(HttpStream, ABC):

    primary_key = "id"
    cursor_field = "date_updated"
    url_base: str = BASE_URL
    http_method: str = "POST"

    def __init__(
        self,
        authenticator: Base64HttpAuthenticator,
        start_date: str,
        object_id: str,
        fields: List[Mapping[str, Any]],
    ):
        super().__init__(authenticator=authenticator)
        self.start_date = start_date
        self.object_id = object_id
        self.fields = fields

    def path(self, **kwargs) -> str:
        return SEARCH_PATH

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return {"cursor": cursor} if (cursor := response.json().get("cursor")) else None

    def request_body_json(
        self,
        stream_state: Optional[Mapping[str, Any]],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Optional[Mapping[str, Any]]:
        return generate_custom_object_search_query(
            object_id=self.object_id,
            created_date=self.start_date,
            fields=self.fields,
            updated_date=stream_state.get(self.cursor_field) if stream_state else None,
            updated_date_field=self.cursor_field,
            cursor=next_page_token.get("cursor") if next_page_token else None,
        )

    def _map_field_id_to_field_name(self, field_id: str) -> str:
        return next(
            (
                field["name"]
                for field in self.fields
                # Remove prefix from both field_id and field["id"] to be extra cautious, only the field_id should have the prefix but convert both to be safe
                if field["id"].removeprefix(CUSTOM_FIELD_PREFIX) == field_id.removeprefix(CUSTOM_FIELD_PREFIX)
            ),
            field_id,
        )

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping[str, Any]]:
        data = response.json()["data"]
        for item in data:
            yield {self._map_field_id_to_field_name(field): val for field, val in item.items()}

    def get_updated_state(
        self,
        current_stream_state: Mapping[str, Any],
        latest_record: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        """This method is called after read_records() completes and is called once for every record returned."""
        return {self.cursor_field: date.today().strftime("%Y-%m-%d")}

    def get_json_schema(self) -> Mapping[str, Any]:
        json_schema = {
            "type": "object",
            "properties": {
                **{f["id"]: f["type"] for f in COMMON_FIELDS},
                **{f["name"]: get_data_type(f) for f in self.fields},
            },
        }
        return json_schema


def generate_custom_objects(authenticator: Base64HttpAuthenticator, args: Mapping[str, Any]) -> List[Mapping[str, Any]]:
    try:
        response = requests.get(url=CUSTOM_OBJECT_TYPE_URL, headers=authenticator.get_auth_header())
        response.raise_for_status()
        custom_object_types = response.json().get("data", [])
        return [
            type(custom_object_type["name"], (CustomObjectStream,), {})(
                authenticator=authenticator,
                start_date=args.get("start_date"),
                object_id=custom_object_type["id"],
                fields=custom_object_type["fields"],
            )
            for custom_object_type in custom_object_types
        ]
    except Exception as e:
        logger.error(f"Error generating custom objects: {e}")
        return []
