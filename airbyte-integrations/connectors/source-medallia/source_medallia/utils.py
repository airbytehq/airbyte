#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
import logging
from typing import Dict

from airbyte_cdk.sources.streams import Stream
from airbyte_protocol.models import SyncMode
from requests.auth import AuthBase

from .authenticator import Medalliaauth2Authenticator

logger = logging.getLogger("airbyte")


def initialize_authenticator(config: Dict) -> AuthBase:
    return Medalliaauth2Authenticator(
        token_endpoint=config.get("token-endpoint"),
        client_secret=config.get("client-secret"),
        client_id=config.get("client-id")
    )


def datetime_to_string(date: datetime.datetime) -> str:
    return date.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def read_full_refresh(stream_instance: Stream):
    slices = stream_instance.stream_slices(sync_mode=SyncMode.full_refresh)
    for _slice in slices:
        records = stream_instance.read_records(stream_slice=_slice, sync_mode=SyncMode.full_refresh)
        for record in records:
            yield record
