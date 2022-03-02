from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional
from urllib import request

import requests

from .with_campaign_streams import WithCampaignAppleSearchAdsStream

class WithCampaignAdgroupAppleSearchAdsStream(WithCampaignAppleSearchAdsStream):
    cursor_field = "date"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        return {}

    def _chunk_adgroup_range(self, campaigns: List[any]) -> List[Mapping[str, any]]:
        offset = 0

        campaign_adgroups = []

        self.logger.info("Starting all Adgroup access")

        for campaign in campaigns:
          self.logger.info(f"Starting all Adwords access for Campaign {campaign['campaign_id']}")

          while True:
              params = {
                  "limit": self.limit,
                  "offset": offset
              }

              response = requests.request(
                  "GET",
                  url=f"{self.url_base}campaigns/{campaign['campaign_id']}/adgroups",
                  headers={
                      "X-AP-Context": f"orgId={self.org_id}",
                      **self.my_auth.get_auth_header()
                  },
                  params=params
              )

              for adgroup in response.json()["data"]:
                  campaign_adgroups.append({
                    "campaign_id": campaign["campaign_id"],
                    "adgroup_id": adgroup["id"]
                  })

              pagination = response.json()["pagination"]

              if pagination["totalResults"] > (pagination["startIndex"] + pagination["itemsPerPage"]):
                  offset = pagination["startIndex"] + pagination["itemsPerPage"]
              else:
                  break

        self.logger.info(f"Got {len(campaign_adgroups)} Campaign Adgroups")

        return campaign_adgroups

    def stream_slices(self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None) -> Iterable[
        Optional[Mapping[str, any]]]:

        campaigns = self._chunk_campaigns_range()

        return self._chunk_adgroup_range(campaigns)

class AdgroupNegativeKeywords(WithCampaignAdgroupAppleSearchAdsStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"campaigns/{stream_slice.get('campaign_id')}/adgroups/{stream_slice.get('adgroup_id')}/negativekeywords"

class AdgroupTargetingKeywords(WithCampaignAdgroupAppleSearchAdsStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"campaigns/{stream_slice.get('campaign_id')}/adgroups/{stream_slice.get('adgroup_id')}/targetingkeywords"
