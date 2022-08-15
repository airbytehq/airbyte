#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from datetime import datetime
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.utils import casing
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.core import IncrementalMixin
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
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

# Basic full refresh stream
class FirestoreStream(HttpStream, ABC):
    url_base = Helpers.url_base
    primary_key = "name"
    page_size = 100
    http_method = "POST"
    collection_name: str

    @property
    def name(self):
        return casing.camel_to_snake(self.collection_name)

    def __init__(self, authenticator: TokenAuthenticator, collection_name: str):
        super().__init__(authenticator=authenticator)
        self._cursor_value = ""
        self.collection_name = collection_name

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        documents = list(self.parse_response(response))
        if len(documents) == 0:
            return None
        if self.cursor_key is None:
            return {"stringValue": documents[len(documents) - 1]["name"]}
        return documents[len(documents) - 1]["fields"][self.cursor_key]

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        timestamp_state: Optional[datetime] = stream_state.get(self.cursor_key)
        timestamp_value = timestamp_state.timestamp() if timestamp_state else None
        return {
            "structuredQuery": {
                "from": [{"collectionId": self.collection_name, "allDescendants": True}],
                "where": {
                    "fieldFilter": {
                        "field": {"fieldPath": "authorization.updated_at"},
                        "op": "GREATER_THAN_OR_EQUAL",
                        "value": {
                            "timestampValue": timestamp_value,
                        },
                    }
                }
                if timestamp_value
                else None,
                "limit": self.page_size,
                "orderBy": [{"field": {"fieldPath": self.cursor_key}, "direction": "ASCENDING"}] if self.cursor_key else None,
                "startAt": {"values": [next_page_token], "before": False} if next_page_token else None,
            }
        }

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        json = response.json()
        results = []
        for entry in json:
            if "document" in entry:
                result = entry["document"]
                if self.cursor_field:
                    result[self.cursor_field] = entry["document"]["fields"][self.cursor_field]["timestampValue"]
                results.append(result)
        return iter(results)

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "type": "object",
            "$schema": "http://json-schema.org/draft-07/schema#",
            "additionalProperties": True,
            "required": ["name"],
            "properties": {
                "name": { "type": ["string"] },
                self.cursor_field: { "type": ["null", "string"]}
            },
        }


class IncrementalFirestoreStream(FirestoreStream, IncrementalMixin):

    _cursor_value: Optional[datetime]
    cursor_key = 'updated_at'
    start_date: Optional[datetime]

    def __init__(self, authenticator: TokenAuthenticator, collection_name: str):
        super().__init__(authenticator=authenticator, collection_name=collection_name)

    @property
    def cursor_field(self):
        return self.cursor_key

    @property
    def state(self) -> MutableMapping[str, Any]:
        return {self.cursor_key: self._cursor_value} if self._cursor_value else {}

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        self._cursor_value = value.get(self.cursor_key, self.start_date)

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        return params

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        for record in super().read_records(
            sync_mode=sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
        ):
            yield record
            self._cursor_value = max(record["fields"][self.cursor_key]["timestampValue"], self._cursor_value)


class Collection(IncrementalFirestoreStream):
    project_id: str
    collection_name: str

    def __init__(self, authenticator: TokenAuthenticator, collection_name: str, config: Mapping[str, Any]):
        super().__init__(authenticator, collection_name=collection_name)
        self.collection_name = collection_name
        self.project_id = config["project_id"]
        self.start_date = datetime.fromisoformat(config["start_date"].replace("Z", "+00:00")) if "start_date" in config else None

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return Helpers.get_collection_path(self.project_id, self.collection_name)


# Source
class SourceFirestore(AbstractSource):
    def get_auth(self, config: Mapping[str, Any]) -> TokenAuthenticator:
        scopes = ['https://www.googleapis.com/auth/datastore']
        credentials = service_account.Credentials.from_service_account_info(json.loads(config["google_application_credentials"]), scopes=scopes)        
        credentials.refresh(google.auth.transport.requests.Request())
        return TokenAuthenticator(token=credentials.token)

    def check_connection(self, logger, config: Mapping[str, Any]) -> Tuple[bool, any]:
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

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = self.get_auth(config=config)
        project_id = config["project_id"]
        collections = self.discover_collections(project_id, auth)
        return map(lambda collection_name : Collection(auth, collection_name, config), collections)
