#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import IncrementalMixin, Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


def convex_url_base(instance_name) -> str:
    return f"https://{instance_name}.convex.cloud"


# Source
class SourceConvex(AbstractSource):
    def _json_schemas(self, config) -> requests.Response:
        instance_name = config["instance_name"]
        access_key = config["access_key"]
        url = f"{convex_url_base(instance_name)}/api/0.2.0/json_schemas"
        headers = {"Authorization": f"Convex {access_key}"}
        return requests.get(url, headers=headers)

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        Connection check to validate that the user-provided config can be used to connect to the underlying API

        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        resp = self._json_schemas(config)
        if resp.status_code == 200:
            return True, None
        else:
            return False, resp.text

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        resp = self._json_schemas(config)
        assert resp.status_code == 200
        json_schemas = resp.json()
        table_names = list(json_schemas.keys())
        return [
            ConvexStream(
                config["instance_name"],
                config["access_key"],
                table_name,
                json_schemas[table_name],
            )
            for table_name in table_names
        ]


class ConvexStream(HttpStream, IncrementalMixin):
    def __init__(self, instance_name: str, access_key: str, table_name: str, json_schema: Any):
        self.instance_name = instance_name
        self.table_name = table_name
        if json_schema:
            json_schema["properties"]["_ts"] = {"type": "number"}
        else:
            json_schema = {}
        self.json_schema = json_schema
        self._cursor_value = None
        self._has_more = True
        super().__init__(TokenAuthenticator(access_key, "Convex"))

    @property
    def name(self) -> str:
        return self.table_name

    @property
    def url_base(self) -> str:
        return convex_url_base(self.instance_name)

    def get_json_schema(self) -> Mapping[str, Any]:
        return self.json_schema

    primary_key = "_id"
    cursor_field = "_ts"

    # Checkpoint stream reads after this many records. This prevents re-reading of data if the stream fails for any reason.
    state_checkpoint_interval = 128

    @property
    def state(self) -> Mapping[str, Any]:
        if self._cursor_value:
            return {self.cursor_field: self._cursor_value}
        else:
            return {}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = value[self.cursor_field]

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        # Inner level of pagination shares the same state as outer,
        # and returns None to indicate that we're done.
        return self.state if self._has_more else None

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "/api/0.2.0/document_deltas"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        resp_json = response.json()
        self._cursor_value = resp_json["cursor"]
        self._has_more = resp_json["hasMore"]
        return resp_json["values"]

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {"tableName": self.table_name}
        if stream_state and self.cursor_field in stream_state:
            params["cursor"] = stream_state[self.cursor_field]
        if next_page_token and self.cursor_field in next_page_token:
            params["cursor"] = next_page_token[self.cursor_field]
        return params

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]):
        """
        This is supposedly deprecated, but it's still used by AbstractSource to update state between calls to `read_records`.
        """
        return self.state
