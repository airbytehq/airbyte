#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime
import json
import time
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.core import Stream, StreamData
import requests

"""
TODO: Most comments in this class are instructive and should be deleted after the source is implemented.

This file provides a stubbed example of how to use the Airbyte CDK to develop both a source connector which supports full refresh or and an
incremental syncs from an HTTP API.

The various TODOs are both implementation hints and steps - fulfilling all the TODOs should be sufficient to implement one basic and one incremental
stream from a source. This pattern is the same one used by Airbyte internally to implement connectors.

The approach here is not authoritative, and devs are free to use their own judgement.

There are additional required TODOs in the files within the integration_tests folder and the spec.yaml file.
"""


# Basic full refresh stream
class TwitterTweetsStream(HttpStream, ABC):
    """
    This class represents a stream output by the connector.
    This is an abstract base class meant to contain all the common functionality at the API level e.g: the API base URL, pagination strategy,
    parsing responses etc..

    Each stream should extend this class (or another abstract subclass of it) to specify behavior unique to that stream.

    Typically for REST APIs each stream corresponds to a resource in the API. For example if the API
    contains the endpoints
        - GET v1/customers
        - GET v1/employees

    then you should have three classes:
    `class TwitterFollowersStream(HttpStream, ABC)` which is the current class
    `class Customers(TwitterFollowersStream)` contains behavior to pull data for customers using v1/customers
    `class Employees(TwitterFollowersStream)` contains behavior to pull data for employees using v1/employees

    If some streams implement incremental sync, it is typical to create another class
    `class IncrementalTwitterFollowersStream((TwitterFollowersStream), ABC)` then have concrete stream implementations extend it. An example
    is provided below.

    See the reference docs for the full list of configurable options.
    """

    # Fill in the url base. Required.
    url_base = "https://api.twitter.com"

    def __init__(self, authenticator: TokenAuthenticator, config: Mapping[str, Any], **kwargs):
        super().__init__()
        self.screen_name = config["screen_name"]
        self.api_key = config["api_key"]
        self.page_size = config["page_size"]

        self.job_time = datetime.datetime.now()
        self.auth = authenticator

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        Override this method to define a pagination strategy. If you will not be using pagination, no action is required - just return None.

        This method should return a Mapping (e.g: dict) containing whatever information required to make paginated requests. This dict is passed
        to most other methods in this class to help you form headers, request bodies, query params, etc..

        For example, if the API accepts a 'page' parameter to determine which page of the result to return, and a response from the API contains a
        'page' number, then this method should probably return a dict {'page': response.json()['page'] + 1} to increment the page count by 1.
        The request_params method should then read the input next_page_token and set the 'page' param to next_page_token['page'].

        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """
        # api 限制 15 calls/min,所以要sleep 一下
        # print("next_page_token \n", response.json()["next_cursor"])
        # if response.json()["next_cursor"]:
        #     print("next_page_token find next page,sleep 10 seconds!")
        #     time.sleep(10)
        #     return {"cursor": response.json()["next_cursor"]}
        # else:
        #     return None
        return None

    # use auth now
    def request_headers(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        # The api requires that we include apikey as a header so we do that in this method
        # print("request_headers.auth\n", self.auth.get_auth_header())
        return self.auth.get_auth_header()

    def request_params(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        Override this method to define any query parameters to be set. Remove this method if you don't need to define request params.
        Usually contains common params e.g. pagination size etc.
        """
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return None


class TwitterTweetMetrics(TwitterTweetsStream):
    primary_key = "list"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        TODO: Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        user_result = requests.get(f'{self.url_base}/2/users/by?usernames={self.screen_name}', headers=self.auth.get_auth_header())
        user_result = json.loads(user_result.text)
        user_id = user_result['data'][0]['id']
        return f'/2/users/{user_id}/tweets'

    def request_params(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {'tweet.fields': 'public_metrics'}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        tweet_list = response.json()
        tweet_list = tweet_list['data']

        count_result = []
        for tweet_detail in tweet_list:
            public_metrics = tweet_detail['public_metrics']
            count_result.append({
                'id': tweet_detail['id'],
                'text': tweet_detail['text'],
                'retweet_count': public_metrics['retweet_count'],
                'reply_count': public_metrics['reply_count'],
                'like_count': public_metrics['like_count'],
                'quote_count': public_metrics['quote_count'],
                'impression_count': public_metrics['impression_count']
            })
        print(count_result)
        return count_result


# Source
class SourceTwitterTweet(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
         Implement a connection check to validate that the user-provided config can be used to connect to the underlying API

        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        api_key = config["api_key"]
        screen_name = config["screen_name"]
        if api_key and screen_name:
            return True, None
        else:
            return False, "Api key of Screen Name should not be null!"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        Replace the streams below with your own streams.

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        # remove the authenticator if not required.
        print("config \n", config)
        auth = TokenAuthenticator(token=config["api_key"])  # Oauth2Authenticator is also available if you need oauth support
        return [TwitterTweetMetrics(authenticator=auth, config=config)]
