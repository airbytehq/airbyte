#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import concurrent.futures
import datetime
import math
from abc import ABC
from dataclasses import asdict
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.sources.streams.http import HttpStream

from .api import ZohoAPI
from .exceptions import IncompleteMetaDataException, UnknownDataTypeException
from .types import FieldMeta, ModuleMeta, ZohoPickListItem


class ZohoCrmStream(HttpStream, ABC):
    json_schema: Dict[Any, Any] = {}
    _path: str = ""

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        if response.status_code != 200:
            return None
        pagination = response.json()["info"]
        if not pagination["more_records"]:
            return None
        return {"page": pagination["page"] + 1}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        if next_page_token:
            return {**next_page_token}
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data = response.json()["data"] if response.status_code == 200 else []
        yield from data

    def path(self, *args, **kwargs) -> str:
        return self._path

    def get_json_schema(self) -> Dict[Any, Any]:
        return self.json_schema


class IncrementalZohoCrmStream(ZohoCrmStream):
    cursor_field = "Modified_Time"

    def __init__(self, authenticator: "requests.auth.AuthBase" = None, config: Mapping[str, Any] = None):
        super().__init__(authenticator)
        self._config = config
        self._state = {}
        self._start_datetime = self._config.get("start_datetime") or "1970-01-01T00:00:00+00:00"

    @property
    def state(self) -> Mapping[str, Any]:
        if self._state:
            return self._state
        return {self.cursor_field: self._start_datetime}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._state = value

    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        for record in super().read_records(*args, **kwargs):
            current_cursor_value = datetime.datetime.fromisoformat(self.state[self.cursor_field])
            latest_cursor_value = datetime.datetime.fromisoformat(record[self.cursor_field])
            new_cursor_value = max(latest_cursor_value, current_cursor_value)
            self.state = {self.cursor_field: new_cursor_value.isoformat("T", "seconds")}
            yield record

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        last_modified = stream_state.get(self.cursor_field, self._start_datetime)
        # since API filters inclusively, we add 1 sec to prevent duplicate reads
        last_modified_dt = datetime.datetime.fromisoformat(last_modified)
        last_modified_dt += datetime.timedelta(seconds=1)
        last_modified = last_modified_dt.isoformat("T", "seconds")
        return {"If-Modified-Since": last_modified}


class ZohoStreamFactory:
    def __init__(self, config: Mapping[str, Any]):
        self.api = ZohoAPI(config)
        self._config = config

    def _init_modules_meta(self) -> List[ModuleMeta]:
        modules_meta_json = self.api.modules_settings()
        modules = [ModuleMeta.from_dict(module) for module in modules_meta_json]
        return list(filter(lambda module: module.api_supported, modules))

    def _populate_fields_meta(self, module: ModuleMeta):
        fields_meta_json = self.api.fields_settings(module.api_name)
        fields_meta = []
        for field in fields_meta_json:
            pick_list_values = field.get("pick_list_values", [])
            if pick_list_values:
                field["pick_list_values"] = [ZohoPickListItem.from_dict(pick_list_item) for pick_list_item in field["pick_list_values"]]
            fields_meta.append(FieldMeta.from_dict(field))
        module.fields = fields_meta

    def _populate_module_meta(self, module: ModuleMeta):
        module_meta_json = self.api.module_settings(module.api_name)
        module.update_from_dict(next(iter(module_meta_json), None))

    def produce(self) -> List[HttpStream]:
        modules = self._init_modules_meta()
        streams = []

        def populate_module(module):
            self._populate_module_meta(module)
            self._populate_fields_meta(module)

        def chunk(max_len, lst):
            for i in range(math.ceil(len(lst) / max_len)):
                yield lst[i * max_len : (i + 1) * max_len]

        max_concurrent_request = self.api.max_concurrent_requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrent_request) as executor:
            for batch in chunk(max_concurrent_request, modules):
                executor.map(lambda module: populate_module(module), batch)

        for module in modules:
            try:
                schema = asdict(module.schema)
            except (IncompleteMetaDataException, UnknownDataTypeException):
                continue

            stream_params = {
                "url_base": f"{self.api.api_url}",
                "_path": f"/crm/v2/{module.api_name}",
                "json_schema": schema,
                "primary_key": "id",
            }
            incremental_stream = type(f"Incremental{module.api_name}ZohoCRMStream", (IncrementalZohoCrmStream,), stream_params)
            streams.append(incremental_stream(self.api.authenticator, config=self._config))
        return streams
