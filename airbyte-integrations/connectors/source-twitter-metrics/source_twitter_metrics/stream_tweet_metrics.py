import datetime
import time
from abc import ABC
import json
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
import requests
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union


class TwitterTweetMetrics(HttpStream, ABC):
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

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        result = response.json()
        meta = result['meta']

        # api 限制 15 calls/min,所以要sleep 一下
        # if 'next_token' in meta.keys():
        #     print("next_page_token find next page,sleep 60 seconds!")
        #     time.sleep(60)
        #     return {"pagination_token": meta["next_token"]}
        # else:
        #     return None
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

        print("request_params \n", type(next_page_token), next_page_token)
        if not next_page_token:
            return {'tweet.fields': 'public_metrics,created_at', 'max_results': 10}
        else:
            return {'tweet.fields': 'public_metrics,created_at', "pagination_token": next_page_token["pagination_token"], 'max_results': 10}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        result = response.json()

        if not 'data' in result.keys():
            return []

        tweet_list = result['data']

        count_result = []
        for tweet_detail in tweet_list:
            public_metrics = tweet_detail['public_metrics']
            count_result.append({
                'tweet_id': tweet_detail['id'],
                'handler': self.screen_name,
                'timestamp': self.job_time,
                'tweet_time': tweet_detail['created_at'],
                'text': tweet_detail['text'],
                'retweet_count': public_metrics['retweet_count'],
                'reply_count': public_metrics['reply_count'],
                'like_count': public_metrics['like_count'],
                'quote_count': public_metrics['quote_count'],
                'impression_count': public_metrics['impression_count']
            })
        print(count_result)
        return count_result

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        user_result = requests.get(f'{self.url_base}/2/users/by?usernames={self.screen_name}', headers=self.auth.get_auth_header())
        user_result = json.loads(user_result.text)
        user_id = user_result['data'][0]['id']
        return f'/2/users/{user_id}/tweets'

