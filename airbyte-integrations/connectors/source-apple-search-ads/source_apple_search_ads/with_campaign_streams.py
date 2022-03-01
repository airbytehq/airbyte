from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional
from urllib import request

import requests

from .basic_streams import AppleSearchAdsStream

class WithCampaignAppleSearchAdsStream(AppleSearchAdsStream, ABC):
    cursor_field = "date"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        return {}

    def _chunk_campaigns_range(self) -> List[Mapping[str, any]]:
        offset = 0

        campaign_ids = []

        self.logger.info("Starting all Campaigns access")

        while True:
            params = {
                "limit": self.limit,
                "offset": offset
            }

            response = requests.request(
                "GET",
                url=f"{self.url_base}campaigns",
                headers={
                    "X-AP-Context": f"orgId={self.org_id}",
                    **self.authenticator.get_auth_header()
                },
                params=params
            )

            for campaign in response.json()["data"]:
                campaign_ids.append({
                    "campaign_id": campaign["id"],
                    "adam_id": campaign["adamId"]
                })

            pagination = response.json()["pagination"]

            if pagination["totalResults"] > (pagination["startIndex"] + pagination["itemsPerPage"]):
                offset = pagination["startIndex"] + pagination["itemsPerPage"]
            else:
                break

        self.logger.info(f"Got {len(campaign_ids)} Campaigns")

        return campaign_ids

    def stream_slices(self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None) -> Iterable[
        Optional[Mapping[str, any]]]:

        return self._chunk_campaigns_range()

class Adgroups(WithCampaignAppleSearchAdsStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"campaigns/{stream_slice.get('campaign_id')}/adgroups"

class CampaignNegativeKeywords(WithCampaignAppleSearchAdsStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"campaigns/{stream_slice.get('campaign_id')}/adgroups"

class CreativeSets(WithCampaignAppleSearchAdsStream):
    primary_key = "id"

    @property
    def http_method(self) -> str:
        return "POST"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"creativesets/find"

    def stream_slices(self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None) -> Iterable[
        Optional[Mapping[str, any]]]:

        data_slices = super().stream_slices(sync_mode, cursor_field, stream_state)

        new_slices = []
        adam_id_slices = set()

        for slice in data_slices:
            if slice["adam_id"] in adam_id_slices:
                next
            else:
                new_slices.append(slice)
                adam_id_slices.add(slice["adam_id"])

        return new_slices

    def request_body_json(
        self, stream_slice: Mapping[str, Any] = None, **kwargs: Any
    ) -> Optional[Mapping]:
        post_json = {
            "selector": {
                "conditions": [
                    {
                        "field": "adamId",
                        "operator": "EQUALS",
                        "values": [
                            stream_slice.get('adam_id')
                        ]
                    }
                ]
            }
        }

        return post_json

class AdgroupCreativeSets(WithCampaignAppleSearchAdsStream):
    primary_key = "id"

    @property
    def http_method(self) -> str:
        return "POST"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"campaigns/{stream_slice.get('campaign_id')}/adgroupcreativesets/find"

    def request_body_json(
        self, stream_slice: Mapping[str, Any] = None, **kwargs: Any
    ) -> Optional[Mapping]:
        post_json = {
            "selector": {
                "conditions": [
                    {
                        "field": "campaignId",
                        "operator": "EQUALS",
                        "values": [
                            stream_slice.get('campaign_id')
                        ]
                    }
                ]
            }
        }

        return post_json
