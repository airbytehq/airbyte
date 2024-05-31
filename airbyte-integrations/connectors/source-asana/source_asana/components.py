# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from dataclasses import dataclass
from typing import Any, Mapping, MutableMapping, Optional
from airbyte_cdk.sources.declarative.schema.json_file_schema_loader import JsonFileSchemaLoader
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState

@dataclass
class CustomAsanaRequester(HttpRequester):
    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        params = super().get_request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        # params.update(self.get_opt_fields(self))
        return params

    def _request_params(
        self,
        stream_state: Optional[StreamState],
        stream_slice: Optional[StreamSlice],
        next_page_token: Optional[Mapping[str, Any]],
        extra_params: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        extra_params = super()._request_params(stream_state, stream_slice, next_page_token, extra_params)
        return extra_params

    def get_opt_fields(self) -> MutableMapping[str, str]:
        """
        For "GET all" request for almost each stream Asana API by default returns 3 fields for each
        record: `gid`, `name`, `resource_type`. Since we want to get all fields we need to specify those fields in each
        request. For each stream set of fields will be different and we get those fields from stream's schema.
        Also each nested object, like `workspace`, or list of nested objects, like `followers`, also by default returns
        those 3 fields mentioned above, so for nested stuff we also need to specify fields we want to return and we
        decided that for all nested objects and list of objects we will be getting only `gid` field.
        Plus each stream can have its exceptions about how request required fields, like in `Tasks` stream.
        More info can be found here - https://developers.asana.com/docs/input-output-options.
        """
        opt_fields = list()
        schema_loader = JsonFileSchemaLoader(config=self.config, parameters={"name": self.name})
        schema = schema_loader.get_json_schema()

        for prop, value in schema["properties"].items():
            if "object" in value["type"]:
                opt_fields.append(self._handle_object_type(prop, value))
            elif "array" in value["type"]:
                opt_fields.append(self._handle_array_type(prop, value.get("items", [])))
            else:
                opt_fields.append(prop)

        return {"opt_fields": ",".join(opt_fields)} if opt_fields else dict()