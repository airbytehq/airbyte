#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import csv
import io
import re
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union
from datetime import datetime

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

import json

YD_REPORTS_CODE_MAPPING = {
    201: "Queue to genereate",
    202: "Generating",
}

# Basic full refresh stream
class YandexDirectStream(HttpStream, ABC):
    raise_on_http_errors = True

    url_base = "https://api.direct.yandex.com/json/v5/"

    @property
    def max_retries(self) -> Union[int, None]:
        return 240

    @property
    def http_method(self) -> str:
        return "POST"

    def should_retry(self, response: requests.Response) -> bool:
        if response.status_code not in YD_REPORTS_CODE_MAPPING.keys():
            self.logger.error(
                f"Skipping stream {self.name}. {YD_REPORTS_CODE_MAPPING.get(response.status_code)}. Full error message: {response.text}"
            )
            setattr(self, "raise_on_http_errors", False)
            return False

        return True

    def backoff_time(self, response: requests.Response) -> Optional[int]:
        return int(response.headers.get("retryIn"))

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield {}

# Source
class SourceYandexDirect(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            # Check connectivity
            stream_args = {
                "authenticator": TokenAuthenticator(token=config["auth_token"]),
                "start_date": config["start_date"],
            }

            campaigns_stream = Campaigns(**stream_args)

            next(campaigns_stream.read_records(sync_mode=SyncMode.full_refresh))

            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[YandexDirectStream]:
        auth = TokenAuthenticator(token=config["auth_token"])
        stream_args = {
            "authenticator": auth,
            "start_date": config["start_date"],
        }

        return [
            Ads(**stream_args),
            AdGroups(**stream_args),
            Campaigns(**stream_args),
            Costs(**stream_args)
        ]

class Ads(HttpSubStream, YandexDirectStream):
    primary_key = "Id"

    def __init__(self, start_date: str, authenticator: TokenAuthenticator, **kwargs):
        super().__init__(
            authenticator=authenticator,
            parent=Campaigns(authenticator=authenticator, start_date=start_date, **kwargs),
        )

        self.start_date = start_date

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "ads"

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        args = {
            "authenticator": self.authenticator,
            "start_date": self.start_date,
        }

        campaigns_stream = Campaigns(**args)

        campaigns = []

        for campaign in campaigns_stream.read_records(sync_mode=SyncMode.full_refresh):
            campaigns.append(f'{campaign["Id"]}')

        start = 0
        end = len(campaigns)
        step = 10
        for i in range(start, end, step):
            x = i
            yield {"campaigns": campaigns[x:x+step]}

    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Union[Mapping, str]]:
        campaigns = stream_slice['campaigns']

        body = {
            "method": "get",
            "params": {
                "SelectionCriteria": { "CampaignIds": campaigns },
                "FieldNames": [
                    "Id",
                    "CampaignId",
                    "AdGroupId",
                    "State",
                    "Status",
                    "Type",
                    "Subtype"
                ],
                "TextAdFieldNames": ["Href", "Text"]
            }
        }

        return body

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        """
        Example output:
            {
                "result": {
                    "Ads": [
                        {
                            "Id": 11823565840,
                            "CampaignId": 71850270,
                            "AdGroupId": 4842517623,
                            "Status": "ACCEPTED",
                            "State": "ARCHIVED",
                            "Type": "TEXT_AD",
                            "Subtype": "NONE",
                            "TextAd": {
                                "Text": "#Введение в программирование#. Для любого уровня. Попробуйте!",
                                "Href": "https://ru.hexlet.io/courses/free?utm_source=yandex&utm_medium=cpc&utm_campaign=freemium&utm_content=keys&utm_term=search.cpc&roistat=direct5_{source_type}_{banner_id}_{keyword}&roistat_referrer={source}&roistat_pos={position_type}_{position}"
                            },
                            "CpcVideoAdBuilderAd": {
                                "Href": "https://ru.hexlet.io/programs/frontend?utm_source=yandex&utm_medium=cpc&utm_campaign=prof-frontend&utm_content=rsy_msc.segment_keys&utm_term=campaignid_{campaign_id}.ad_{ad_id}.key_{keyword}.device_{device_type}.pst_{position_type}.rgnid_{region_id}.region_{region_name}.placement_{source}.creative_{creative_name}_{creative_id}.type_{source_type}.adg_{gbid}.phrase_{phrase_id}&roistat=direct5_{source_type}_{banner_id}_{keyword}&roistat_referrer={source}&roistat_pos={position_type}_{position}"
                            },
                            "TextImageAd": {
                                "Href": "https://ru.hexlet.io/programs/frontend?utm_source=yandex&utm_medium=cpc&utm_campaign=prof-frontend&utm_content=rsy_by.segment_keys&utm_term=campaignid_{campaign_id}.ad_{ad_id}.key_{keyword}.device_{device_type}.pst_{position_type}.rgnid_{region_id}.region_{region_name}.placement_{source}.creative_{creative_name}_{creative_id}.type_{source_type}.adg_{gbid}.phrase_{phrase_id}&roistat=direct5_{source_type}_{banner_id}_{keyword}&roistat_referrer={source}&roistat_pos={position_type}_{position}"
                            }
                        }
                    ]
                }
            }
        """

        ads = response.json().get("result").get("Ads")

        yield from ads

class AdGroups(HttpSubStream, YandexDirectStream):
    primary_key = "Id"

    def __init__(self, start_date: str, authenticator: TokenAuthenticator, **kwargs):
        super().__init__(
            authenticator=authenticator,
            parent=Campaigns(authenticator=authenticator, start_date=start_date, **kwargs),
        )

        self.start_date = start_date

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "adgroups"

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        args = {
            "authenticator": self.authenticator,
            "start_date": self.start_date,
        }

        campaigns_stream = Campaigns(**args)

        campaigns = []

        for campaign in campaigns_stream.read_records(sync_mode=SyncMode.full_refresh):
            campaigns.append(f'{campaign["Id"]}')

        start = 0
        end = len(campaigns)
        step = 10
        for i in range(start, end, step):
            x = i
            yield {"campaigns": campaigns[x:x+step]}

    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Union[Mapping, str]]:
        campaigns = stream_slice['campaigns']

        body = {
            "method": "get",
            "params": {
                "SelectionCriteria": { "CampaignIds": campaigns },
                "FieldNames": ["CampaignId", "Id", "Name", "NegativeKeywords", "ServingStatus", "Status", "Subtype", "Type", "TrackingParams"]
            }
        }

        return body

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        """
        Example output:
            {
                "result": {
                    "AdGroups": [
                        {
                            "Id": 5093516849,
                            "Name": "Ретаргет",
                            "CampaignId": 81236205,
                            "Status": "ACCEPTED",
                            "Type": "SMART_AD_GROUP",
                            "Subtype": "NONE",
                            "ServingStatus": "ELIGIBLE",
                            "NegativeKeywords": null,
                            "TrackingParams": "utm_source=yandex&utm_medium=cpc&utm_campaign=prof-professions-retarget&utm_content=rsy_ru.segment_smartbanner&utm_term=campaignid_{campaign_id}.ad_{ad_id}.key_{keyword}.device_{device_type}.pst_{position_type}.rgnid_{region_id}.region_{region_name}.placement_{source}.type_{source_type}.adg_{gbid}.phrase_{phrase_id}&roistat=direct5_{source_type}_{banner_id}_{keyword}&roistat_referrer={source}&roistat_pos={position_type}_{position}"
                        }
                    ]
                }
            }
        """

        adgroups = response.json().get("result").get("AdGroups")

        yield from adgroups

class Campaigns(YandexDirectStream):
    primary_key = "Id"

    def __init__(self, start_date: str, **kwargs):
        super().__init__(**kwargs)

    @property
    def use_cache(self) -> bool:
        return True

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "campaigns"

    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Union[Mapping, str]]:
        body = {
            "method": "get",
            "params": {
                "SelectionCriteria": { },
                "FieldNames": ["Id", "Name", "Status", "Type"]
            }
        }

        return body

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        """
        Example output:
            {
                "result": {
                    "Campaigns": [
                        {
                            "Id": 81236205,
                            "Name": "Retarget Professions / РСЯ (smartbanner)",
                            "Type": "SMART_CAMPAIGN",
                            "Status": "ACCEPTED"
                        }
                    ]
                }
            }
        """

        campaigns = response.json().get("result").get("Campaigns")

        yield from campaigns

class Costs(YandexDirectStream):
    primary_key = None

    def __init__(self, start_date: str, **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "reports"

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {
            "skipReportHeader": "true",
            "skipColumnHeader": "false",
            "skipReportSummary": "true"
        }

    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Union[Mapping, str]]:
        body = {
            "method": "get",
            "params": {
                "ReportType": "CUSTOM_REPORT",
                "ReportName": f"Custom_Report: {datetime.today().strftime('%Y-%m-%d %H:%M:%S')}",
                "DateRangeType": "CUSTOM_DATE",
                "SelectionCriteria": {
                    "DateFrom": self.start_date,
                    "DateTo": f"{pendulum.today().date()}",
                    "Filter": [{
                        "Field": "Cost",
                        "Operator": "GREATER_THAN",
                        "Values": ["0"]
                    }]
                },
                "FieldNames": [
                    "AdId",
                    "AdGroupId",
                    "AdGroupName",
                    "AdNetworkType",
                    "Date",
                    "CampaignId",
                    "CampaignName",
                    "CampaignUrlPath",
                    "CampaignType",
                    "Clicks",
                    "Cost",
                    "Impressions"
                ],
                "Format": "TSV",
                "IncludeVAT": "YES"
            }
        }

        return body

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        reader = csv.DictReader(io.StringIO(response.text), delimiter="\t")
        for row in reader:
            yield row
