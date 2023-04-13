import datetime
from abc import ABC
import json
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
import requests
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union


class UserDetail(HttpStream, ABC):
    url_base = "https://api.twitter.com"
    primary_key = "metrics"

    def __init__(self, authenticator: TokenAuthenticator, config: Mapping[str, Any], **kwargs):
        super().__init__()
        self.screen_name = config["screen_name"]
        self.api_key = config["api_key"]
        self.page_size = config["page_size"]

        self.job_time = datetime.datetime.now()
        self.auth = authenticator

    @property
    def use_cache(self):
        """
        Override if needed. If True, all records will be cached.
        """
        return True

    @property
    def max_retries(self) -> Union[int, None]:
        """
        Override if needed. Specifies maximum amount of retries for backoff policy. Return None for no limit.
        """
        return 10

    @property
    def retry_factor(self) -> float:
        """
        Override if needed. Specifies factor for backoff policy.
        """
        return 10

    # use auth now
    def request_headers(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        # The api requires that we include apikey as a header so we do that in this method
        print("request_headers.auth\n", self.auth.get_auth_header())
        return self.auth.get_auth_header()

    def request_params(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {'expansions': 'pinned_tweet_id', 'user.fields': 'created_at,description,entities,id,location,name,profile_image_url,public_metrics'}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        result = response.json()

        if not 'data' in result.keys():
            return []

        user_lookup = result['data']

        return [
            {
                'handler': self.screen_name,
                'id': user_lookup['id'],
                'timestamp': self.job_time,
                'description': user_lookup['description'],
                'profile_image_url': user_lookup['profile_image_url'],
                'followers_count': user_lookup['public_metrics']['followers_count'],
                'following_count': user_lookup['public_metrics']['following_count'],
                'tweet_count': user_lookup['public_metrics']['tweet_count'],
                'listed_count': user_lookup['public_metrics']['listed_count'],
                'name': user_lookup['name']
            }
        ]

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        user_result = requests.get(f'{self.url_base}/2/users/by?usernames={self.screen_name}', headers=self.auth.get_auth_header())
        user_result = json.loads(user_result.text)
        user_id = user_result['data'][0]['id']
        return f'/2/users/{user_id}'

