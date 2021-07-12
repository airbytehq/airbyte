#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


import logging
from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from source_bing_ads.client import Client
from suds import sudsobject

logging.basicConfig(level=logging.INFO)
logging.getLogger("suds.client").setLevel(logging.DEBUG)
logging.getLogger("suds.transport.http").setLevel(logging.DEBUG)


class BingAdsStream(Stream, ABC):
    limit: int = 1000
    primary_key = "Id"

    def __init__(self, client: Client, config: Mapping[str, Any]) -> None:
        self.client = client
        self.config = config

    def next_page_token(self, response: sudsobject.Object, **kwargs: Mapping[str, Any]) -> Optional[Mapping[str, Any]]:
        return None

    def parse_response(self, response: sudsobject.Object, **kwargs) -> Iterable[Mapping]:
        if response is not None and hasattr(response, self.data_field):
            yield from self.client.asdict(response)[self.data_field]

        yield from []

    @abstractmethod
    def send_request(self, **kwargs) -> Mapping[str, Any]:
        """
        This method should be overridden by subclasses to send proper SOAP request
        """
        pass

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        stream_state = stream_state or {}
        pagination_complete = False
        next_page_token = None

        while not pagination_complete:
            params = self.request_params(
                stream_state=stream_state,
                stream_slice=stream_slice,
                next_page_token=next_page_token,
            )
            response = self.send_request(**params)

            next_page_token = self.next_page_token(response, current_page_token=next_page_token)
            if not next_page_token:
                pagination_complete = True

            for record in self.parse_response(response):
                yield record

        yield from []


class Accounts(BingAdsStream):
    data_field: str = "AdvertiserAccount"
    service_name: str = "CustomerManagementService"
    operation_name: str = "SearchAccounts"

    def send_request(self, **kwargs) -> Mapping[str, Any]:
        return self.client.request(service_name=self.service_name, account_id=None, operation_name=self.operation_name, params=kwargs)

    def next_page_token(self, response: sudsobject.Object, current_page_token: Optional[int]) -> Optional[Mapping[str, Any]]:
        current_page_token = current_page_token or 0
        if response is not None and hasattr(response, self.data_field):
            return None if self.limit > len(response[self.data_field]) else current_page_token + 1
        else:
            return None

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        predicates = {
            "Predicate": [
                {
                    "Field": "UserId",
                    "Operator": "Equals",
                    "Value": self.config["user_id"],
                },
            ]
        }

        paging = self.client.get_service().factory.create("ns5:Paging")
        paging.Index = next_page_token or 0
        paging.Size = self.limit
        return {
            "PageInfo": paging,
            "Predicates": predicates,
            "ReturnAdditionalFields": "TaxCertificate AccountMode",
        }


class Campaigns(BingAdsStream):
    data_field: str = "Campaign"
    service_name: str = "CampaignManagement"
    operation_name: str = "GetCampaignsByAccountId"

    additional_fields = " ".join(
        [
            "AdScheduleUseSearcherTimeZone",
            "BidStrategyId",
            "CpvCpmBiddingScheme",
            "DynamicDescriptionSetting",
            "DynamicFeedSetting",
            "MaxConversionValueBiddingScheme",
            "MultimediaAdsBidAdjustment",
            "TargetImpressionShareBiddingScheme",
            "TargetSetting",
            "VerifiedTrackingSetting",
        ]
    )

    def send_request(self, **kwargs) -> Mapping[str, Any]:
        return self.client.request(
            service_name=self.service_name, account_id=kwargs["AccountId"], operation_name=self.operation_name, params=kwargs
        )

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        return {
            "AccountId": stream_slice["account_id"],
            "ReturnAdditionalFields": self.additional_fields,
        }

    def stream_slices(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        for account_id in self.config["account_ids"]:
            yield {"account_id": account_id}


class SourceBingAds(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            client = Client(**config)
            client.get_service().GetAccount(AccountId=config["account_ids"][0])
        except Exception as error:
            return False, error

        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        client = Client(**config)
        return [Accounts(client, config), Campaigns(client, config)]
