#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from pdb import post_mortem
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib import request

import jwt
import requests
import pendulum
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

class AppleSearchAdsException(Exception):
    pass

class AppleSearchAdsAuthenticator(TokenAuthenticator):
    audience = 'https://appleid.apple.com'
    alg = 'ES256'

    expiration_seconds = 60*10

    def __init__(self, client_id: str, team_id: str, key_id: str, private_key: str):
        self.client_id = client_id
        self.team_id = team_id
        self.key_id = key_id
        self.private_key = private_key

        super().__init__(None)

        self._access_token = None
        self._token_expiry_date = pendulum.now()

    def update_access_token(self) -> Optional[str]:
        post_headers = {
            "Host": "appleid.apple.com",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        post_url = f"https://appleid.apple.com/auth/oauth2/token"

        # Create Client secret
        headers = dict()
        headers['alg'] = self.alg
        headers['kid'] = self.key_id

        payload = dict()
        payload['sub'] = self.client_id
        payload['aud'] = self.audience
        payload['iat'] = self._token_expiry_date
        payload['exp'] = pendulum.now().add(seconds=self.expiration_seconds)
        payload['iss'] = self.team_id

        client_secret = jwt.encode(
            payload=payload,
            headers=headers,
            algorithm=self.alg,
            key=self.private_key
        )

        post_data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": client_secret,
            "scope": "searchadsorg"
        }

        resp = requests.post(post_url,
                    data=post_data,
                    headers=post_headers)
        resp.raise_for_status()

        data = resp.json()
        self._access_token = data["access_token"]
        self._token_expiry_date = payload['exp']
        return None

    def get_auth_header(self) -> Mapping[str, Any]:
        if self._token_expiry_date < pendulum.now():
            err = self.update_access_token()
            if err:
                raise AppleSearchAdsException(f"auth error: {err}")
        return {"Authorization": f"Bearer {self._access_token}"}


# Basic full refresh stream
class AppleSearchAdsStream(HttpStream, ABC):

    url_base = "https://api.searchads.apple.com/api/v4/"

    limit = 1000

    org_id: str

    def __init__(
        self,
        org_id: str,
        authenticator: AppleSearchAdsAuthenticator,
        **kwargs,
    ):
        self.org_id = org_id

        super().__init__(authenticator=authenticator)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        pagination = response.json()["pagination"]

        if pagination["totalResults"] > (pagination["startIndex"] + 1) * self.limit:
            return {"limit": self.limit, "offset": ((pagination["startIndex"] + 1) * self.limit) + 1 }
        else:
            return None

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {
            "X-AP-Context": f"orgId={self.org_id}"
        }

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data = response.json()["data"]

        yield from data


class Campaigns(AppleSearchAdsStream):
    primary_key = "id"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {
            "limit": self.limit,
            "offset": 0
        }

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "campaigns"

class IncrementalAppleSearchAdsStream(AppleSearchAdsStream, ABC):
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

        campaign_ids = []

        for campaign in response.json()["data"]:
            campaign_ids.append({
                "campaign_id": campaign["id"],
                "adam_id": campaign["adamId"]
            })

        return campaign_ids

    def stream_slices(self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None) -> Iterable[
        Optional[Mapping[str, any]]]:

        return self._chunk_campaigns_range()

class Adgroups(IncrementalAppleSearchAdsStream):
    primary_key = ["id"]

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"campaigns/{stream_slice.get('campaign_id')}/adgroups"

class CampaignNegativeKeywords(IncrementalAppleSearchAdsStream):
    primary_key = ["id"]

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"campaigns/{stream_slice.get('campaign_id')}/adgroups"

class CreativeSets(IncrementalAppleSearchAdsStream):
    primary_key = ["id"]

    @property
    def http_method(self) -> str:
        return "POST"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"creativesets/find"

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

class SourceAppleSearchAds(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        auth = AppleSearchAdsAuthenticator(
            client_id=config["client_id"],
            team_id=config["team_id"],
            key_id=config["key_id"],
            private_key=config["private_key"]
        )

        try:
            logger.info("Apple Search Ads me access")
            response = requests.request(
                "GET",
                url="https://api.searchads.apple.com/api/v4/me",
                headers=auth.get_auth_header()
            )

            if response.status_code != 200:
                message = response.json()
                error_message = message.get("error")
                if error_message:
                    return False, error_message
                response.raise_for_status()
        except Exception as e:
            logger.info(f"Apple Search Ads failed {e}")
            return False, e

        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = AppleSearchAdsAuthenticator(
            client_id=config["client_id"],
            team_id=config["team_id"],
            key_id=config["key_id"],
            private_key=config["private_key"]
        )

        return [
            Campaigns(org_id=config["org_id"], authenticator=auth),
            Adgroups(org_id=config["org_id"], authenticator=auth),
            CampaignNegativeKeywords(org_id=config["org_id"], authenticator=auth),
            CreativeSets(org_id=config["org_id"], authenticator=auth)
        ]
