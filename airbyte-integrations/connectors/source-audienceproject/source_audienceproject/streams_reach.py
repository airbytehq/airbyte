#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpSubStream

from .streams import IncrementalAudienceprojectStream
from .streams_campaigns import Campaigns


class Reach(IncrementalAudienceprojectStream, HttpSubStream):

    primary_key = ""
    parent: object = Campaigns

    def __init__(self, authenticator, config, **kwargs):
        self.config = config
        self._authenticator = authenticator
        self._session = requests.sessions.Session()

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def stream_slices(
        self, sync_mode: SyncMode.incremental, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None, **kwargs
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        parent = Campaigns(self._authenticator, self.config, **kwargs)
        parent_stream_slices = parent.stream_slices(sync_mode=sync_mode, cursor_field=cursor_field, stream_state=stream_state)
        for stream_slice in parent_stream_slices:
            parent_records = parent.read_records(
                sync_mode=sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
            )
            for record in parent_records:
                yield {"campaign_id": record.get("id")}

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"reports/{stream_slice['campaign_id']}/reach"
