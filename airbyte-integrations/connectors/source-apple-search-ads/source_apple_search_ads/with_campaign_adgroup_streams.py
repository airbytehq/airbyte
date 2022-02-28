from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional
from urllib import request

import requests

from .basic_streams import AppleSearchAdsStream

class WithCampaignAdgroupAppleSearchAdsStream(AppleSearchAdsStream, ABC):
    cursor_field = "date"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        return {}

    def _chunk_campaigns_range(self) -> List[Mapping[str, any]]:
        response = requests.request(
                "GET",
                url=f"{self.url_base}campaigns",
                headers={
                    "X-AP-Context": f"orgId={self.org_id}",
                    **self.authenticator.get_auth_header()
                },
                params={
                    "limit": self.limit
                }
            )

        campaign_adgroups = []

        for campaign in response.json()["data"]:
            adgroup_response = requests.request(
                "GET",
                url=f"{self.url_base}campaigns/{campaign['id']}/adgroups",
                headers={
                    "X-AP-Context": f"orgId={self.org_id}",
                    **self.authenticator.get_auth_header()
                },
                params={
                    "limit": self.limit
                }
            )
            adgroups = adgroup_response.json()["data"]

            for adgroup in adgroups:
              campaign_adgroups.append({
                "campaign_id": campaign["id"],
                "adgroup_id": adgroup["id"]
              })

        return campaign_adgroups

    def stream_slices(self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None) -> Iterable[
        Optional[Mapping[str, any]]]:

        return self._chunk_campaigns_range()

class AdgroupNegativeKeywords(WithCampaignAdgroupAppleSearchAdsStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"campaigns/{stream_slice.get('campaign_id')}/adgroups/{stream_slice.get('adgroup_id')}/negativekeywords"
