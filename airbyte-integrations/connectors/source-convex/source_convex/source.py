#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from datetime import datetime
from json import JSONDecodeError
from typing import Any, Dict, Iterable, Iterator, List, Mapping, MutableMapping, Optional, Tuple, TypedDict, cast

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import IncrementalMixin, Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth.token import TokenAuthenticator

ConvexConfig = TypedDict(
    "ConvexConfig",
    {
        "deployment_url": str,
        "access_key": str,
    },
)

ConvexState = TypedDict(
    "ConvexState",
    {
        "snapshot_cursor": Optional[str],
        "snapshot_has_more": bool,
        "delta_cursor": Optional[int],
    },
)

CONVEX_CLIENT_VERSION = "0.4.0"


# Source
class SourceConvex(AbstractSource):
    def _json_schemas(self, config: ConvexConfig) -> requests.Response:
        deployment_url = config["deployment_url"]
        access_key = config["access_key"]
        url = f"{deployment_url}/api/json_schemas?deltaSchema=true&format=json"
        headers = {
            "Authorization": f"Convex {access_key}",
            "Convex-Client": f"airbyte-export-{CONVEX_CLIENT_VERSION}",
        }
        return requests.get(url, headers=headers)

    def check_connection(self, logger: Any, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        """
        Connection check to validate that the user-provided config can be used to connect to the underlying API

        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        config = cast(ConvexConfig, config)
        resp = self._json_schemas(config)
        if resp.status_code == 200:
            return True, None
        else:
            return False, format_http_error("Connection to Convex via json_schemas endpoint failed", resp)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        config = cast(ConvexConfig, config)
        resp = self._json_schemas(config)
        if resp.status_code != 200:
            raise Exception(format_http_error("Failed request to json_schemas", resp))
        json_schemas = resp.json()
        table_names = list(json_schemas.keys())
        return [
            ConvexStream(
                config["deployment_url"],
                config["access_key"],
                "json",  # Use `json` export format
                table_name,
                json_schemas[table_name],
            )
            for table_name in table_names
        ]


class ConvexStream(HttpStream, IncrementalMixin):
    def __init__(
        self,
        deployment_url: str,
        access_key: str,
        fmt: str,
        table_name: str,
        json_schema: Dict[str, Any],
    ):
        self.deployment_url = deployment_url
        self.fmt = fmt
        self.table_name = table_name
        if json_schema:
            json_schema["additionalProperties"] = True
            json_schema["properties"]["_ab_cdc_lsn"] = {"type": "number"}
            json_schema["properties"]["_ab_cdc_updated_at"] = {"type": "string"}
            json_schema["properties"]["_ab_cdc_deleted_at"] = {"anyOf": [{"type": "string"}, {"type": "null"}]}
        else:
            json_schema = {}
        self.json_schema = json_schema
        self._snapshot_cursor_value: Optional[str] = None
        self._snapshot_has_more = True
        self._delta_cursor_value: Optional[int] = None
        self._delta_has_more = True
        super().__init__(TokenAuthenticator(access_key, "Convex"))

    @property
    def name(self) -> str:
        return self.table_name

    @property
    def url_base(self) -> str:
        return self.deployment_url

    def get_json_schema(self) -> Mapping[str, Any]:  # type: ignore[override]
        return self.json_schema

    primary_key = "_id"
    cursor_field = "_ts"

    # Checkpoint stream reads after this many records. This prevents re-reading of data if the stream fails for any reason.
    state_checkpoint_interval = 128

    @property
    def state(self) -> MutableMapping[str, Any]:
        value: ConvexState = {
            "snapshot_cursor": self._snapshot_cursor_value,
            "snapshot_has_more": self._snapshot_has_more,
            "delta_cursor": self._delta_cursor_value,
        }
        return cast(MutableMapping[str, Any], value)

    @state.setter
    def state(self, value: MutableMapping[str, Any]) -> None:
        state = cast(ConvexState, value)
        self._snapshot_cursor_value = state["snapshot_cursor"]
        self._snapshot_has_more = state["snapshot_has_more"]
        self._delta_cursor_value = state["delta_cursor"]

    def next_page_token(self, response: requests.Response) -> Optional[ConvexState]:
        if response.status_code != 200:
            raise Exception(format_http_error("Failed request", response))
        resp_json = response.json()
        if self._snapshot_has_more:
            self._snapshot_cursor_value = resp_json["cursor"]
            self._snapshot_has_more = resp_json["hasMore"]
            self._delta_cursor_value = resp_json["snapshot"]
        else:
            self._delta_cursor_value = resp_json["cursor"]
            self._delta_has_more = resp_json["hasMore"]
        has_more = self._snapshot_has_more or self._delta_has_more
        return cast(ConvexState, self.state) if has_more else None

    def path(
        self,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        # https://docs.convex.dev/http-api/#sync
        if self._snapshot_has_more:
            return "/api/list_snapshot"
        else:
            return "/api/document_deltas"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        if response.status_code != 200:
            raise Exception(format_http_error("Failed request", response))
        resp_json = response.json()
        return list(resp_json["values"])

    def request_params(
        self,
        stream_state: Optional[Mapping[str, Any]],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        params: Dict[str, Any] = {"tableName": self.table_name, "format": self.fmt}
        if self._snapshot_has_more:
            if self._snapshot_cursor_value:
                params["cursor"] = self._snapshot_cursor_value
            if self._delta_cursor_value:
                params["snapshot"] = self._delta_cursor_value
        else:
            if self._delta_cursor_value:
                params["cursor"] = self._delta_cursor_value
        return params

    def request_headers(
        self,
        stream_state: Optional[Mapping[str, Any]],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, str]:
        """
        Custom headers for each HTTP request, not including Authorization.
        """
        return {
            "Convex-Client": f"airbyte-export-{CONVEX_CLIENT_VERSION}",
        }

    def get_updated_state(self, current_stream_state: ConvexState, latest_record: Mapping[str, Any]) -> ConvexState:
        """
        This (deprecated) method is still used by AbstractSource to update state between calls to `read_records`.
        """
        return cast(ConvexState, self.state)

    def read_records(self, sync_mode: SyncMode, *args: Any, **kwargs: Any) -> Iterator[Any]:
        self._delta_has_more = sync_mode == SyncMode.incremental
        for read_record in super().read_records(sync_mode, *args, **kwargs):
            record = dict(read_record)
            ts_ns = record["_ts"]
            ts_seconds = ts_ns / 1e9  # convert from nanoseconds.
            # equivalent of java's `new Timestamp(transactionMillis).toInstant().toString()`
            ts_datetime = datetime.utcfromtimestamp(ts_seconds)
            ts = ts_datetime.isoformat()
            # DebeziumEventUtils.CDC_LSN
            record["_ab_cdc_lsn"] = ts_ns
            # DebeziumEventUtils.CDC_DELETED_AT
            record["_ab_cdc_updated_at"] = ts
            record["_deleted"] = "_deleted" in record and record["_deleted"]
            # DebeziumEventUtils.CDC_DELETED_AT
            record["_ab_cdc_deleted_at"] = ts if record["_deleted"] else None
            yield record


def format_http_error(context: str, resp: requests.Response) -> str:
    try:
        err = resp.json()
        return f"{context}: {resp.status_code}: {err['code']}: {err['message']}"
    except (JSONDecodeError, KeyError):
        return f"{context}: {resp.text}"
