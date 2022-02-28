from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

from datetime import date, timedelta
import requests
import re

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

        data = response.json()["data"]

        if data == None:
            yield from []
        else:
            rows = response.json()["data"]["reportingDataResponse"]["row"]

            for row in rows:
                row[self.primary_key] = row["metadata"][self.primary_key]

            yield from rows

class ReportCampaigns(WithCampaignReportAppleSearchAdsStream):
    primary_key = "campaignId"

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
    primary_key = "adGroupId"

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

class ReportKeywords(WithCampaignReportAppleSearchAdsStream):
    primary_key = "keywordId"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"reports/campaigns/{stream_slice.get('campaign_id')}/keywords"

    # For keywords, if the keywords does not exist it gives out a 400
    @classmethod
    def check_for_non_existant_keyword(cls, response: requests.Response) -> bool:
        if response.status_code in [400]:
            # example response:
            # {'data': None, 'pagination': None, 'error': {'errors': [{'messageCode': 'INVALID_INPUT', 'message': 'APPSTORE_SEARCH_TAB CAMPAIGN DOES NOT CONTAIN KEYWORD', 'field': ''}]}}
            err_body = response.json()["error"]["errors"][0]
            if re.match(r"DOES NOT CONTAIN KEYWORD", err_body["message"]):
                return True

        return False

    def should_retry(self, response: requests.Response) -> bool:
        if self.check_for_non_existant_keyword(response):
            return False

        return super().should_retry(response)

    @property
    def raise_on_http_errors(self) -> bool:
        return False

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
                        "field": "keywordId",
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
