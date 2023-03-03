#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from datetime import datetime
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.utils import casing
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.core import IncrementalMixin
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.models.airbyte_protocol import DestinationSyncMode, SyncMode
from google.oauth2 import service_account
import google.auth.transport.requests
import requests
import json

class Helpers(object):
    url_base = "https://firestore.googleapis.com/v1/"
    page_size = 100

    @staticmethod
    def get_collection_path(project_id: str, collection_name: str) -> str:
        return f"projects/{project_id}/databases/(default)/documents:runQuery"

    @staticmethod
    def get_project_url(project_id: str) -> str:
        return f"{Helpers.url_base}projects/{project_id}"

    @staticmethod
    def get_collections_list_url(project_id: str) -> str:
        return f"{Helpers.get_project_url(project_id)}/databases/(default)/documents:listCollectionIds"

    @staticmethod
    def parse_date(date: str) -> datetime:
        return datetime.fromisoformat(date.replace("Z", "+00:00"))

# Basic full refresh stream
class FirestoreStream(HttpStream, ABC):
    _cursor_value: Optional[datetime]
    cursor_field: Union[str, List[str], None] = None
    @property
    def cursor_key(self):
        if isinstance(self.cursor_field, list):
            if (len(self.cursor_field) > 0):
                return self.cursor_field[0]
            return None
        return self.cursor_field


    url_base: str = Helpers.url_base
    _primary_key: str = "name"
    page_size: int = 100
    http_method: str = "POST"
    collection_name: str

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return self._primary_key

    @primary_key.setter
    def primary_key(self, value: str) -> None:
        if not isinstance(value, property):
            self._primary_key = value

    @property
    def name(self):
        return casing.camel_to_snake(self.collection_name)

    def __init__(self, authenticator: TokenAuthenticator, collection_name: str):
        super().__init__(
            authenticator=authenticator,
        )
        self._cursor_value = None
        self.collection_name = collection_name

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        documents = list(self.parse_response(response))
        if len(documents) == 0:
            return None
        if self.cursor_key is None:
            return None
        return { "timestampValue": documents[len(documents) - 1][self.cursor_key] }

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = {}, next_page_token: Mapping[str, Any] = {}
    ) -> MutableMapping[str, Any]:
        return {}

    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = {},
        next_page_token: Mapping[str, Any] = {},
    ) -> Optional[Mapping]:
        page_size = stream_state.get("page_size", self.page_size)
        timestamp_state: Optional[datetime] = stream_state.get(self.cursor_key) if self.cursor_key else None
        timestamp_value = Helpers.parse_date(timestamp_state).isoformat() if timestamp_state else None

        self.logger.info(f"Requesting body JSON with cursor {self.cursor_key} value {next_page_token} and page_size {page_size}")

        return {
            "structuredQuery": {
                "from": [{"collectionId": self.collection_name, "allDescendants": True}],
                "where": {
                    "fieldFilter": {
                        "field": {"fieldPath": self.cursor_key },
                        "op": "GREATER_THAN",
                        "value": {
                            "timestampValue": timestamp_value,
                        },
                    }
                } if timestamp_value else None,
                "limit": page_size,
                "orderBy": [{"field": {"fieldPath": self.cursor_key}, "direction": "ASCENDING"}] if self.cursor_key else None,
                "startAt": {"values": [next_page_token], "before": False} if next_page_token else None,
            }
        }

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data = response.json()
        results = []
        for entry in data:
            if "document" in entry:
                result = {
                    "name": entry["document"]["name"],
                    "json_data": entry["document"]["fields"],
                }
                if self.cursor_key:
                    result[self.cursor_key] = entry["document"]["fields"][self.cursor_key]["timestampValue"]

                results.append(result)
        return iter(results)

    def get_json_schema(self) -> Mapping[str, Any]:
        result = {
            "type": "object",
            "$schema": "http://json-schema.org/draft-07/schema#",
            "additionalProperties": True,
            "required": ["name"],
            "properties": {
                "name": { "type": "string" },
                "json_data": { "type": "object" },
            },
        }
        if self.cursor_key:
            result["properties"][self.cursor_key] = { "type": ["null", "string"] }

        return result


class IncrementalFirestoreStream(FirestoreStream, IncrementalMixin):
    start_date: Optional[datetime]

    def __init__(self, authenticator: TokenAuthenticator, collection_name: str, cursor_field_possibilities: List[str] = []):
        super().__init__(authenticator=authenticator, collection_name=collection_name)
        self.cursor_field = self.guess_cursor_field(cursor_field_possibilities)
        print(self.cursor_field)

    def guess_cursor_field(self, cursor_field_possibilities: List[str]) -> Union[str, None]:
        records = list(self.read_records(sync_mode=SyncMode.full_refresh, stream_state={"page_size": 1}))
        if len(records) == 0:
            return None
        # try to guess default field from first record
        first_record = records[0]["json_data"]

        for cursor_field in cursor_field_possibilities:
            if cursor_field in first_record:
                return cursor_field
        return "name"

    @property
    def state(self) -> dict[str, Any]:
        return { self.cursor_key: self._cursor_value.isoformat() } if self._cursor_value and self.cursor_key else {}

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        new_cursor_value = value.get(self.cursor_key, self.start_date) if self.cursor_key else None
        self._cursor_value = Helpers.parse_date(new_cursor_value) if isinstance(new_cursor_value, str) else new_cursor_value

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = {}, next_page_token: Mapping[str, Any] = {}
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        return params

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = [],
        stream_slice: Mapping[str, Any] = {},
        stream_state: Mapping[str, Any] = {},
    ) -> Iterable[Mapping[str, Any]]:
        self.logger.info(f"Stream {self.name}: Reading in {sync_mode} (cursor field {cursor_field}). Current cursor value: {self._cursor_value}")
        self.cursor_field = cursor_field
        for record in super().read_records(
            sync_mode=sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
        ):
            yield record
            record_date = Helpers.parse_date(record[self.cursor_key]) if self.cursor_key else None
            if record_date:
                self._cursor_value = max(record_date, self._cursor_value) if self._cursor_value else record_date

class Collection(IncrementalFirestoreStream):
    project_id: str
    collection_name: str

    def __init__(self, authenticator: TokenAuthenticator, collection_name: str, config: Mapping[str, Any]):
        self.project_id = config["project_id"]
        self.collection_name = collection_name
        super().__init__(authenticator, collection_name=collection_name, cursor_field_possibilities=config["cursor_field_possibilities"])
        self.start_date = Helpers.parse_date(config["start_date"]) if "start_date" in config else None

    def path(
        self, stream_state: Mapping[str, Any] = {}, stream_slice: Mapping[str, Any] = {}, next_page_token: Mapping[str, Any] = {}
    ) -> str:
        return Helpers.get_collection_path(self.project_id, self.collection_name)


# Source
class SourceFirestore(AbstractSource):
    def get_auth(self, config: Mapping[str, Any]) -> TokenAuthenticator:
        scopes = ['https://www.googleapis.com/auth/datastore']
        credentials = service_account.Credentials.from_service_account_info(json.loads(config["google_application_credentials"]), scopes=scopes)        
        credentials.refresh(google.auth.transport.requests.Request())
        token: Any = credentials.token
        return TokenAuthenticator(token=token)

    def check_connection(self, logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        auth = self.get_auth(config=config)
        project_id = config["project_id"]
        url = Helpers.get_collections_list_url(project_id)
        try:
            response = requests.get(url, headers=auth.get_auth_header())
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return False, str(e)
        return True, None

    def discover_collections(self, project_id: str, auth: TokenAuthenticator) -> List[str]:
        url = Helpers.get_collections_list_url(project_id)
        response = requests.post(url, headers=auth.get_auth_header())
        response.raise_for_status()
        json = response.json()
        return json["collectionIds"]

    def streams(self, config: Mapping[str, Any]):
        auth = self.get_auth(config=config)
        project_id = config["project_id"]
        collections = self.discover_collections(project_id, auth)
        return map(lambda collection_name : Collection(auth, collection_name, config), collections)
