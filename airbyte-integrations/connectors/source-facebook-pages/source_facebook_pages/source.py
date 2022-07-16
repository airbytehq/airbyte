#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from json import JSONDecodeError
from typing import Any, List, Mapping, Tuple

import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .streams import Page, PageInsights, Post, PostInsights


class SourceFacebookPages(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        if "access_token" not in config or "page_id" not in config:
            return False, "You must provide both Access token and Page ID"

        ok = False
        error_msg = None

        try:
            access_token, page_id = config["access_token"], config["page_id"]
            access_token = self.generate_page_access_token(page_id, access_token)
            _ = list(Page(access_token=access_token, page_id=page_id).read_records(sync_mode=SyncMode.full_refresh))
            ok = True
        except Exception as e:
            logger.info(f'Error:{e}')
            error_msg = str(e)

        return ok, error_msg

    @staticmethod
    def generate_page_access_token(page_id: str, access_token: str) -> str:
        # We are expecting to receive User access token from config. To access
        # Pages API we need to generate Page access token. Page access tokens
        # can be generated from another Page access token (with the same page ID)
        # so if user manually set Page access token instead of User access
        # token it would be no problem unless it has wrong page ID.
        # https://developers.facebook.com/docs/pages/access-tokens#get-a-page-access-token
        r = requests.get(f"https://graph.facebook.com/{page_id}", params={"fields": "access_token", "access_token": access_token})
        if r.ok:
            return r.json().get("access_token")

        try:
            error_msg = r.json().get("error", {}).get("message")
        except JSONDecodeError:
            error_msg = r.text
        raise Exception(error_msg)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        access_token, page_id = config["access_token"], config["page_id"]
        access_token = self.generate_page_access_token(page_id, access_token)
        stream_kwargs = {
            "access_token": access_token,
            "page_id": page_id,
        }

        streams = [
            Post(**stream_kwargs),
            Page(**stream_kwargs),
            PostInsights(**stream_kwargs),
            PageInsights(**stream_kwargs),
        ]
        return streams
