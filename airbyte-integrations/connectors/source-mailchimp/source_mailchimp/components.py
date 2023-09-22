#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Any, Iterable, List, Mapping

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.auth.token import BasicHttpAuthenticator, BearerAuthenticator
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.declarative.types import StreamSlice


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
        if self.config.get("campaign_id"):
            # this is a workaround to speed up SATs and enable incremental tests
            campaigns = [{"id": self.config.get("campaign_id")}]
        else:
            campaigns = campaign_stream.read_records(sync_mode=SyncMode.full_refresh)

        for campaign in campaigns:
            slice_ = {"campaign_id": campaign["id"]}
            yield slice_


@dataclass
class EmailActivityRecordExtractor(RecordExtractor):
    def extract_records(self, response: requests.Response) -> List[Mapping[str, Any]]:
        try:
            response_json = response.json()
        except requests.exceptions.JSONDecodeError:
            self.logger.error(f"Response returned with {response.status_code=}, {response.content=}")
            response_json = {}
        # transform before save
        # [{'campaign_id', 'list_id', 'list_is_active', 'email_id', 'email_address', 'activity[array[object]]', '_links'}] ->
        # -> [[{'campaign_id', 'list_id', 'list_is_active', 'email_id', 'email_address', '**activity[i]', '_links'}, ...]]
        data = response_json.get("emails", [])
        records = []
        for item in data:
            for activity_item in item.pop("activity", []):
                records.append({**item, **activity_item})
        return records


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


@dataclass
class MailchimpRequester(HttpRequester):
    @staticmethod
    def get_server_prefix(access_token: str) -> str:
        try:
            response = requests.get(
                "https://login.mailchimp.com/oauth2/metadata", headers={"Authorization": "OAuth {}".format(access_token)}
            )
            return response.json()["dc"]
        except Exception as e:
            raise Exception(f"Cannot retrieve server_prefix for you account. \n {repr(e)}")

    def get_url_base(self) -> str:
        credentials = self.config.get("credentials", {})
        auth_type = credentials.get("auth_type")
        if auth_type == "apikey":
            data_center = credentials.get("apikey", "").split("-").pop()
        elif auth_type == "oauth2.0":
            data_center = self.get_server_prefix(credentials.get("access_token"))
        else:
            raise Exception(f"Invalid auth type: {auth_type}")

        return f"https://{data_center}.api.mailchimp.com/3.0/"
