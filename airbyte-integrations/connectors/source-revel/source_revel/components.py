#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
from dataclasses import dataclass

from typing import Any, Mapping, Optional
from airbyte_cdk.sources.declarative.incremental import DatetimeBasedCursor
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOptionType
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState


@dataclass
class InitialFullRefreshDatetimeIncrementalSync(DatetimeBasedCursor):
    """
    In order to run an initial full data sync without using incremental stream options
    don't return request parameters if the cursor field is not in the stream state.
    """

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        if self._cursor_field.eval(self.config, stream_state=stream_state) not in stream_state:
            return {}
        else:
            return self._get_request_options(RequestOptionType.request_parameter, stream_slice)
