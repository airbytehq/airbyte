#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Any, Iterable, List, Mapping

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.extractors.dpath_extractor import DpathExtractor
from airbyte_cdk.sources.declarative.types import StreamSlice
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.auth.token import BearerAuthenticator, BasicHttpAuthenticator

import requests



@dataclass
class CampaignIdPartitionRouter(SubstreamPartitionRouter):

    def stream_slices(self) -> Iterable[StreamSlice]:
        """
        Iterate over each parent stream's record and create a StreamSlice for each record.
        For each stream, iterate over its stream_slices.
        For each stream slice, iterate over each record.
        yield a stream slice for each such records.
        If a parent slice contains no record, emit a slice with parent_record=None.
        The template string can interpolate the following values:
        - parent_stream_slice: mapping representing the parent's stream slice
        - parent_record: mapping representing the parent record
        - parent_stream_name: string representing the parent stream name
        """

        campaign_stream = self.parent_stream_configs[0].stream
        if self.config.campaign_id:
            # this is a workaround to speed up SATs and enable incremental tests
            campaigns = [{"id": self.config.campaign_id}]
        else:
            campaigns = campaign_stream.read_records(sync_mode=SyncMode.full_refresh)
        for campaign in campaigns:
            slice_ = {"campaign_id": campaign["id"]}
            yield slice_

@dataclass
class EmailActivityRecordExtractor(DpathExtractor):
    
    def extract_records(self, response: requests.Response) -> List[Mapping[str, Any]]:
        extracted_records = super().extract_records(response)
        # transform before save
        # [{'campaign_id', 'list_id', 'list_is_active', 'email_id', 'email_address', 'activity[array[object]]', '_links'}] ->
        # -> [[{'campaign_id', 'list_id', 'list_is_active', 'email_id', 'email_address', '**activity[i]', '_links'}, ...]]
        for item in extracted_records:
            for activity_item in item.pop("activity", []):
                yield {**item, **activity_item}


@dataclass
class MailchimpAuthenticator(DeclarativeAuthenticator):
    config: Mapping[str, Any]
    basic_auth: BasicHttpAuthenticator
    oauth: BearerAuthenticator

    def __new__(cls, basic_auth, oauth, config, *args, **kwargs):
        authorization = config.get("credentials", {})
        auth_type = authorization.get("auth_type")
        if auth_type == "apikey" or not authorization:
            return basic_auth
        elif auth_type == "oauth2.0":
            return oauth
        else:
            raise Exception(f"Invalid auth type: {auth_type}")
