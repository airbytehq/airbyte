# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from dataclasses import dataclass
from typing import Any, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.declarative.requesters.request_options.interpolated_request_options_provider import (
    RequestInput,
)
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState

@dataclass
class CustomAsanaRequester(HttpRequester):
    """
    This class is created to add call throttling using the optional requests_per_minute parameter
    """

    request_parameters: Optional[RequestInput] = None

    # def _validate_response(
    #     self,
    #     response: requests.Response,
    # ) -> Optional[requests.Response]:
    #     # if fail -> raise exception
    #     # if ignore -> ignore response and return None
    #     # else -> delegate to caller

    #     return response

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        params = {"limit": self.page_size}
        params.update(self.request_parameters)
        params.update(self.get_opt_fields())
        if next_page_token:
            params.update(next_page_token)

        return params

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
        schema = self.get_json_schema()

        for prop, value in schema["properties"].items():
            if "object" in value["type"]:
                opt_fields.append(self._handle_object_type(prop, value))
            elif "array" in value["type"]:
                opt_fields.append(self._handle_array_type(prop, value.get("items", [])))
            else:
                opt_fields.append(prop)

        return {"opt_fields": ",".join(opt_fields)} if opt_fields else dict()