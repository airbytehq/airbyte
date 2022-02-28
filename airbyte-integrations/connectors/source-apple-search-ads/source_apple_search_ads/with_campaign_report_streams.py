from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

from datetime import date, timedelta
import requests

from .with_campaign_streams import WithCampaignAppleSearchAdsStream

class WithCampaignReportAppleSearchAdsStream(WithCampaignAppleSearchAdsStream, ABC):
    cursor_field = "date"

    @property
    def http_method(self) -> str:
        return "POST"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
      rows = response.json()["data"]["reportingDataResponse"]["row"]

      for row in rows:
        row["campaignId"] = row["metadata"]["campaignId"]

      yield from rows

class ReportCampaigns(WithCampaignReportAppleSearchAdsStream):
    primary_key = ["campaignId"]

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"reports/campaigns"

    def request_body_json(self,
      stream_state: Mapping[str, Any],
      stream_slice: Mapping[str, Any] = None,
      **kwargs) -> Optional[Mapping]:
        start_date = (date.today() - timedelta(days=7)).strftime("%Y-%m-%d")
        end_date = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")

        post_json = {
                "startTime": start_date,
                "endTime": end_date,
                "granularity": "DAILY",
                "selector": {
                    "conditions": [
                        {
                            "field": "campaignId",
                            "operator": "EQUALS",
                            "values": [
                                stream_slice.get('campaign_id')
                            ]
                        }
                    ],
                    "orderBy": [
                        {
                        "field": "adamId",
                        "sortOrder": "ASCENDING"
                        }
                    ],
                    "pagination": {
                        "offset": 0,
                        "limit": self.limit
                    }
                }
        }

        return post_json

class ReportAdgroups(WithCampaignReportAppleSearchAdsStream):
    primary_key = ["adGroupId"]

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"reports/campaigns/{stream_slice.get('campaign_id')}/adgroups"

    def request_body_json(self,
      stream_state: Mapping[str, Any],
      stream_slice: Mapping[str, Any] = None,
      **kwargs) -> Optional[Mapping]:
        start_date = (date.today() - timedelta(days=7)).strftime("%Y-%m-%d")
        end_date = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")

        post_json = {
                "startTime": start_date,
                "endTime": end_date,
                "granularity": "DAILY",
                "selector": {
                    "conditions": [
                        {
                            "field": "deleted",
                            "operator": "IN",
                            "values": [
                                "true",
                                "false"
                            ]
                        }
                    ],
                    "orderBy": [
                        {
                        "field": "adGroupId",
                        "sortOrder": "ASCENDING"
                        }
                    ],
                    "pagination": {
                        "offset": 0,
                        "limit": self.limit
                    }
                }
        }

        return post_json
