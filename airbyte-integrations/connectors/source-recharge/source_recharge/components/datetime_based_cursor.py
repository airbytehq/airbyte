#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from dataclasses import dataclass
from datetime import datetime
from typing import Any, List, Mapping, Optional, Union

from airbyte_cdk.sources.declarative.incremental import DatetimeBasedCursor
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.types import Record, StreamSlice, StreamState


@dataclass
class RechargeDateTimeBasedCursor(DatetimeBasedCursor):
    """
    Override for the default `DatetimeBasedCursor`.

    `get_request_params()` - to guarantee the records are returned in `ASC` order.

    Currently the `HttpRequester` couldn't handle the case when,
    we need to omit all other `request_params` but `next_page_token` param,
    typically when the `CursorPagination` straregy is applied.

    We should have the `request_parameters` structure like this, or similar to either keep or omit the parameter,
    based on the paginated result:
    ```
    HttpRequester:
       ...
       request_parameters:
        # The `sort_by` param, will be omitted intentionaly on the paginated result
        - sort_by: "updated_at-asc"
          ignore_on_pagination: true
        # the `some_other_param` param, will be kept on the paginated result
        - some_other_param: "string_value"
          ignore_on_pagination: false
    ```

    Because there is a `ignore_stream_slicer_parameters_on_paginated_requests` set to True for the `SimpleRetriever`,
    we are able to omit everthing what we pass from the `DatetimeBasedCursor.get_request_params()` having the initial request as expected,
    all subsequent requests are made based on Paginated Results.
    """

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters=parameters)

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        """
        The override to add additional param to the api request to guarantee the `ASC` records order.

        Background:
            There is no possability to pass multiple request params from the YAML for the incremental streams,
            in addition to the `start_time_option` or similar, having them ignored those additional params,
            when we have `next_page_token`, which must be the single param to be passed to satisfy the API requirements.
        """

        params = super().get_request_params(
            stream_state=stream_state,
            stream_slice=stream_slice,
            next_page_token=next_page_token,
        )
        params["sort_by"] = "updated_at-asc"
        return params
