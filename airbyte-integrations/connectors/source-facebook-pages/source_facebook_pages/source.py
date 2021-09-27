#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Tuple

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .streams import Page, PageInsights, Post, PostInsights


class SourceFacebookPages(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        ok = False
        error_msg = None

        try:
            _ = list(Page(access_token=config["access_token"], page_id=config["page_id"]).read_records(sync_mode=SyncMode.full_refresh))
            ok = True
        except Exception as e:
            error_msg = repr(e)

        return ok, error_msg

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        stream_kwargs = {
            "access_token": config["access_token"],
            "page_id": config["page_id"],
        }

        streams = [
            Post(**stream_kwargs),
            Page(**stream_kwargs),
            PostInsights(**stream_kwargs),
            PageInsights(**stream_kwargs),
        ]
        return streams
