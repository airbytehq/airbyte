#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC, abstractproperty
from datetime import datetime
import json
import logging
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator, HttpAuthenticator
from requests.auth import AuthBase


# Basic full refresh stream
class VkAdsNewStream(HttpStream, ABC):
    limit = 1000
    url_base = "https://ads.vk.com/api/"

    def __init__(
        self,
        authenticator: Union[AuthBase, HttpAuthenticator] = None,
        additional_filters: dict[str, Any] = {},
    ):
        super().__init__(authenticator=authenticator)
        self.additional_filters = additional_filters

    def request_params(self, next_page_token: Mapping[str, Any] = None, *args, **kwargs) -> MutableMapping[str, Any]:
        return {
            "limit": self.limit,
            "offset": next_page_token.get("offset", 0),
            **self.additional_filters,
        }

    def additional_filters_field_name(self) -> str:
        return self.name.lower() + "_stream_additional_filters"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        response_data: dict[str, Any] = response.json()
        # ensure pagination objects are in response
        if all(key in ("count", "offset", "items") for key in response_data.keys()):
            if response_data.get("items") and len(response_data.get("items", [])) == self.limit:
                return {"offset": response_data.get("offset") + self.limit}
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()["items"]


class ObjectStream(VkAdsNewStream, ABC):
    primary_key = "id"
    use_cache = True

    def path(self, *args, **kwargs) -> str:
        return f"v2/{self.single_object_field_name}.json"

    @abstractproperty
    def single_object_field_name(self) -> str:
        raise NotImplementedError

    @abstractproperty
    def many_objects_field_name(self) -> str:
        raise NotImplementedError


class StatisticsStream(VkAdsNewStream, HttpSubStream, ABC):
    def __init__(
        self,
        *,
        authenticator: Union[AuthBase, HttpAuthenticator] = None,
        date_from: datetime,
        date_to: datetime,
        additional_filters: dict[str, Any],
        parent: ObjectStream,
    ):
        if not isinstance(parent, self.parent_class):
            raise ValueError(f"{self.name} can't be instantiated with {parent.name} class as substream parent")
        HttpSubStream.__init__(self, parent=parent)
        VkAdsNewStream.__init__(self, authenticator=authenticator, additional_filters=additional_filters)
        self.parent: ObjectStream = self.parent
        self.date_from = date_from
        self.date_to = date_to

    @abstractproperty
    def parent_class(self) -> VkAdsNewStream:
        raise NotImplementedError

    def path(self, *args, **kwargs) -> str:
        return f"v3/statistics/{self.parent.many_objects_field_name}/day.json"

    def request_params(self, stream_slice: Mapping[str, any] = None, *args, **kwargs) -> MutableMapping[str, Any]:
        return {
            **super().request_params(stream_slice, *args, **kwargs),
            "date_from": self.date_from.strftime("%Y-%m-%d"),
            "date_from": self.date_to.strftime("%Y-%m-%d"),
            "id": stream_slice["parent"]["id"],
        }

    def parse_response(self, response: requests.Response, stream_slice: Mapping[str, any] = None, *args, **kwargs) -> Iterable[Mapping]:
        for record in super().parse_response(response=response, stream_slice=stream_slice, *args, **kwargs):
            yield {
                self.parent.single_object_field_name + "_id": stream_slice["parent"]["id"],
                **record,
            }


class Banners(ObjectStream):
    single_object_field_name = "banner"
    many_objects_field_name = "banners"


class AdPlans(ObjectStream):
    single_object_field_name = "ad_plan"
    many_objects_field_name = "ad_plans"


class AdGroups(ObjectStream):
    single_object_field_name = "ad_group"
    many_objects_field_name = "ad_groups"


class BannersStatistics(StatisticsStream):
    parent_class = Banners


class AdPlansStatistics(StatisticsStream):
    parent_class = AdPlans


class AdGroupsStatistics(StatisticsStream):
    parent_class = AdGroups


# Source
class SourceVkAdsNew(AbstractSource):
    statistics_streams_classes: List[StatisticsStream] = [
        BannersStatistics,
        AdPlansStatistics,
        AdGroupsStatistics,
    ]

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = TokenAuthenticator(token="api_key")

        shared_kwargs = {"authenticator": auth}
        streams = []

        for statistics_stream_class in self.statistics_streams_classes:
            parent = statistics_stream_class.parent_class(
                **shared_kwargs,
                additional_filters=json.loads(
                    config.get(
                        statistics_stream_class.parent_class.additional_filters_field_name,
                        "{}",
                    ),
                ),
            )
            streams.append(parent)
            streams.append(
                statistics_stream_class(
                    **shared_kwargs,
                    date_from=config.get("date_from"),
                    date_to=config.get("date_to"),
                    additional_filters=json.loads(
                        config.get(
                            statistics_stream_class.additional_filters_field_name,
                            "{}",
                        ),
                    ),
                )
            )

        return streams
