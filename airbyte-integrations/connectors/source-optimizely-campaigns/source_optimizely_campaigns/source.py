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

import urllib.parse as urlparse
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import parse_qs

import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


# Basic full refresh stream
class OptimizelyStream(HttpStream, ABC):
    url_base = "https://api.campaign.episerver.net/rest/"
    primary_key = "id"

    logger = AirbyteLogger()

    def __init__(self, client_id: str, **kwargs):
        super().__init__(**kwargs)
        self.client_id = client_id
        self.url_base += self.client_id

        """
        A maximum of 500.000 recipients can be queried per call with the Optimizely Campaigns API. 
        All other endpoints have a limit of 10.000 per call.
        """
        self.API_RECIPIENT_LIMIT = 500000
        self.API_LIMIT = 10000

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        If there are more records after the current query, this is indicated by the property 'rel' 
        with the value 'next'. We can now use this link to retrieve the next records according to 
        the limit and offset.

        e.g.
        "links": [
            {
            "rel": "next",
            "href": "https://api.campaign.episerver.net/rest/<client_id>/recipients/<recipient_list_id>?offset=100&limit=100"
            }
        ]
        """
        decoded_response = response.json()
        for link in decoded_response.get("links", []):
            if link.get("rel", None) == "next":
                decoded_response.update({"has_more": True, "next": link.get("href")})
                break

        if decoded_response.get("has_more", False) and decoded_response.get("elements", []):
            parsed = urlparse.urlparse(decoded_response.get("next"))
            return parse_qs(parsed.query)
        
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:

        # Optimizely default pagination is 100, max is 100000
        params = {"limit": self.API_LIMIT}

        # Handle pagination by inserting the next page's token in the request parameters
        if next_page_token:
            params.update(next_page_token)

        return params

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        if self.client_id:
            return {"Optimizely-Account": self.client_id}

        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()

        yield from response_json.get("elements", [])


class IncrementalOptimizelyStream(OptimizelyStream, ABC):
    cursor_field = "modified"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """

        return {self.cursor_field: max(latest_record.get(self.cursor_field, ""), current_stream_state.get(self.cursor_field, ""))}


class RecipientLists(IncrementalOptimizelyStream):
    primary_key = ["id"]
    cursor_field = "modified"

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "/recipientlists"


class Recipients(IncrementalOptimizelyStream):
    primary_key = ["id", "recipient_list"]
    cursor_field = "modified"

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        recipient_list = stream_slice["list_id"]
        return f"/recipients/{recipient_list}"

    def stream_slices(
        self,
        **kwargs: Mapping[str, Any],
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        attribute_names_stream = AttributeNames(authenticator=self.authenticator, client_id=self.client_id)
        for attribute_name_record in attribute_names_stream.read_records(sync_mode=SyncMode.full_refresh):
            attribute_name_string = ",".join(attribute_name_record["attributeNames"])
            yield {"list_id": attribute_name_record["recipient_list"], "attributes": attribute_name_string}

    def request_params(self, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs):
        params = {"limit": self.API_RECIPIENT_LIMIT, "attributeNames": stream_slice["attributes"]}

        if next_page_token:
            params.update(next_page_token)

        return params

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        response_json = response.json()

        recipients = response_json.get("elements", [])
        for recipient in recipients:
            recipient.update({"recipient_list": stream_slice["list_id"]})

        yield from recipients


class AttributeNames(OptimizelyStream):
    primary_key = None

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        recipient_list = stream_slice["list_id"]
        return f"/recipientlists/{recipient_list}/attributeNames"


    def stream_slices(
        self,
        **kwargs: Mapping[str, Any],
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        recipient_lists_stream = RecipientLists(authenticator=self.authenticator, client_id=self.client_id)
        for recipient_list_record in recipient_lists_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield {"list_id": recipient_list_record["id"]}

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        data = {"recipient_list": stream_slice["list_id"], "attributeNames": response.json().get("attributeNames", [])}

        yield from [data]


class BlackListEntries(OptimizelyStream):
    primary_key = ["mailingGroupId", "pattern"]

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "/blacklistentries"


class Unsubscribes(IncrementalOptimizelyStream):
    primary_key = ["recipientListId", "recipientId"]
    cursor_field = "created"

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "/unsubscribes"

class SmartCampaigns(IncrementalOptimizelyStream):
    primary_key = ["id", "mailingGroupId"]
    cursor_field = "modified"

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "/smartcampaigns"

    def request_params(self, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs):
        params = {"resultView": "DETAILED"}

        if next_page_token:
            params.update(next_page_token)

        return params


class SmartCampaignReports(OptimizelyStream):
    primary_key = "campaignId"

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        campaign_id = stream_slice["campaign_id"]
        return f"/smartcampaigns/{campaign_id}/report"

    def stream_slices(
        self,
        **kwargs: Mapping[str, Any],
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        smart_campaigns_stream = SmartCampaigns(authenticator=self.authenticator, client_id=self.client_id)
        for smart_campaign_record in smart_campaigns_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield {"campaign_id": smart_campaign_record["id"]}

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        response_json = response.json()
        yield from [response_json]


class TransactionalMails(IncrementalOptimizelyStream):
    primary_key = ["id", "mailingGroupId"]
    cursor_field = "modified"

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "/transactionalmail"

    def request_params(self, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs):
        params = {"resultView": "DETAILED"}

        if next_page_token:
            params.update(next_page_token)

        return params


class TransactionalMailReports(OptimizelyStream):
    primary_key = "campaignId"

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        campaign_id = stream_slice["campaign_id"]
        return f"/transactionalmail/{campaign_id}/report"

    def stream_slices(
        self,
        **kwargs: Mapping[str, Any],
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        transactional_mails_stream = TransactionalMails(authenticator=self.authenticator, client_id=self.client_id)
        for transactional_mail_record in transactional_mails_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield {"campaign_id": transactional_mail_record["id"]}

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        response_json = response.json()
        yield from [response_json]


# Source
class SourceOptimizelyCampaigns(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """The connection validation asks the API endpoint `/confirmations` with the given credentials if the given credentails are correct.

        [**[API-Docs]** GET confirmations](https://api.campaign.optimizely.net/apidoc/index.html#/Confirmations)

        Raises:
            Exception: Raises if the client_secret or the client_id is invalid so the API can not be called successfully.
        """

        url = "https://api.campaign.episerver.net/rest/"
        endpoint = "/confirmations"

        try:
            api_key = config["client_secret"]
            client_id = config["client_id"]

            payload = {"limit": 1}
            headers = {"Authorization": "Basic " + api_key}

            r = requests.get(url + client_id + endpoint, params=payload, headers=headers)

            if r.status_code == 200:
                return True, None
            else:
                r.raise_for_status()

        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = TokenAuthenticator(token=config["client_secret"], auth_method="Basic")
        args = {"authenticator": auth, "client_id": config["client_id"]}
        return [
            RecipientLists(**args),
            Recipients(**args),
            AttributeNames(**args),
            BlackListEntries(**args),
            Unsubscribes(**args),
            SmartCampaigns(**args),
            SmartCampaignReports(**args),
            TransactionalMails(**args),
            TransactionalMailReports(**args),
        ]
