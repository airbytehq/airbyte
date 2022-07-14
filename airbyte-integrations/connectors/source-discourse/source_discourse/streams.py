#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.sources.streams.http import HttpStream


class DiscourseStream(HttpStream, ABC):

    url_base = "https://discuss.airbyte.io/"

    primary_key = None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield {}


class TagGroups(DiscourseStream):
    """
    API docs: https://docs.discourse.org/#tag/Tags/operation/listTagGroups
    """

    #  primary_key is not used as we don't do incremental syncs - https://docs.airbyte.com/understanding-airbyte/connections/
    primary_key = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
        **kwargs,
    ) -> str:
        path = "tag_groups.json"
        return path

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        for item in response_json["tag_groups"]:
            yield item


class LatestTopics(DiscourseStream):
    """
    API docs: https://docs.discourse.org/#tag/Topics/operation/listLatestTopics
    """

    #  primary_key is not used as we don't do incremental syncs - https://docs.airbyte.com/understanding-airbyte/connections/
    primary_key = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
        **kwargs,
    ) -> str:
        path = "latest.json"
        return path

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        yield response_json


class Posts(DiscourseStream):
    """
    API docs: https://docs.discourse.org/#tag/Posts/operation/listPosts
    """

    primary_key = None

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        TODO: Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        path = "posts.json"
        return path

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        yield response_json
