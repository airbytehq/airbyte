import datetime
import time
import json
from abc import ABC
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
import requests
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union


class FollowerDetails(HttpStream, ABC):
    url_base = "https://api.twitter.com"
    primary_key = "id"

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

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        # api 限制 15 calls/min,所以要sleep 一下
        result = response.json()['meta']

        if 'next_token' in result.keys():
            time.sleep(60)
            return {'next_token': result['next_token']}

        return None

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
        if not next_page_token:
            return {
                "expansions": "pinned_tweet_id",
                "max_results": 1000,
                "user.fields": "created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,verified_type,withheld"
            }
        else:
            return {
                "pagination_token": next_page_token['next_token'],
                "expansions": "pinned_tweet_id",
                "max_results": 1000,
                "user.fields": "created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,verified_type,withheld"
            }

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        result = response.json()
        follower_infos = result['data']
        follower_list = []
        for follower_info in follower_infos:
            follower = {
                'handler': self.screen_name,
                'id': follower_info['id'],
                'timestamp': self.job_time,
                'profile_image_url': follower_info['profile_image_url'],
                'username': follower_info['username'],
                'created_at': follower_info['created_at'],
                'verified': follower_info['verified'],
                'followers_count': follower_info['public_metrics']['followers_count'],
                'following_count': follower_info['public_metrics']['following_count'],
                'tweet_count': follower_info['public_metrics']['tweet_count'],
                'listed_count': follower_info['public_metrics']['listed_count'],
                'protected': follower_info['protected'],
                'name': follower_info['name'],
                'description': follower_info['description'],
                'verified_type': follower_info['verified_type']
            }
            follower_list.append(follower)
        return follower_list

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        user_result = requests.get(f'{self.url_base}/2/users/by?usernames={self.screen_name}', headers=self.auth.get_auth_header())
        user_result = json.loads(user_result.text)
        user_id = user_result['data'][0]['id']
        return f'/2/users/{user_id}/followers'
