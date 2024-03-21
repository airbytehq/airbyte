#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union, Iterator

import elasticsearch.exceptions
import pendulum
from airbyte_cdk.sources.streams.http.auth import NoAuth, HttpAuthenticator
from elasticsearch import Elasticsearch
import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream

from airbyte_cdk.models import (
    SyncMode,
    ConfiguredAirbyteStream,
    AirbyteMessage,
    Type as MessageType
)

from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig, split_config

from .common import deep_merge

from airbyte_cdk.sources.utils.slice_logger import SliceLogger

from airbyte_cdk.sources.streams.core import IncrementalMixin

StreamData = Union[Mapping[str, Any], AirbyteMessage]

# Streams that only support full refresh don't have a suitable cursor so this sentinel
# value is used to indicate that stream should not load the incoming state value
FULL_REFRESH_SENTINEL_STATE_KEY = "__ab_full_refresh_state_message"

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
class ElasticSearchV2Stream(HttpStream, ABC):
    url_base = "http://aes-statistic01.prod.dld:9200"
    client: Elasticsearch = Elasticsearch(url_base)
    date_start = ""
    pit = None

    def __init__(self, date_start):
        super().__init__()
        self.date_start = date_start

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "/_search"

    @property
    def http_method(self) -> str:
        """
        Override if needed. See get_request_data/get_request_json if using POST/PUT/PATCH.
        """
        return "POST"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        docs = response.json()["hits"]["hits"]
        pit_id = response.json()["pit_id"]
        if response.status_code == 200 and docs != []:
            search_after = docs[len(docs) - 1].get("sort")
            return {"search_after": search_after, "pit_id": pit_id}
        else:
            # Case when no more pages
            try:
                self.client.close_point_in_time(id=self.pit.body["id"])
            except elasticsearch.exceptions.NotFoundError as e:
                logging.info("Not PIT found")
            return None

    def request_headers(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        """
        Override to return any non-auth headers. Authentication headers will overwrite any overlapping headers returned from this method.
        """
        return {"content-type": "application/json"}

    def request_body_data(
            self,
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, Any] = None,
            next_page_token: int = 0,
    ) -> Optional[Union[Mapping, str]]:
        """
        Override when creating POST/PUT/PATCH requests to populate the body of the request with a non-JSON payload.

        If returns a ready text that it will be sent as is.
        If returns a dict that it will be converted to a urlencoded form.
        E.g. {"key1": "value1", "key2": "value2"} => "key1=value1&key2=value2"

        At the same time only one of the 'request_body_data' and 'request_body_json' functions can be overridden.
        """

        if stream_state == {}:
            date_filter_start = self.date_start
        else:
            date_filter_start = stream_state.get("updated_at")

        # If this is a new sync
        if next_page_token is None:
            self.pit = self.client.open_point_in_time(index=self.index, keep_alive="1m")
            # Every document do not have an updated_at field. In this case, default to date field
            payload = {
                "query": {
                    "bool": {
                        "minimum_should_match": 1,
                        "should": [
                            {
                                "range": {
                                    "updated_at": {
                                        "gte": date_filter_start
                                    }
                                }
                            },
                            {
                                "bool": {
                                    "must_not": {
                                        "exists": {
                                            "field": self.cursor_field
                                        }
                                    },
                                    "filter": {
                                        "range": {
                                            "date": {
                                                "gte": date_filter_start
                                            }
                                        }
                                    }
                                }
                            }
                        ]
                    }
                },
                "pit": {
                    "id": self.pit.body["id"],
                    "keep_alive": "1m"
                },
                "size": 10000,
                "sort": [
                    "updated_at",
                    "ad_creative",
                    "image"
                ]
            }

        # If this is the next page of a sync
        else:
            pit_id = next_page_token["pit_id"]
            search_after = next_page_token["search_after"]

            payload = {
                "query": {
                    "query_string": {
                        "query": "*"
                    }
                },
                "pit": {
                    "id": pit_id,
                    "keep_alive": "5m"
                },
                "size": 10000,
                "search_after": search_after
            }

        return payload

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """

        hits = response.json()["hits"]["hits"]

        for hit in hits:
            data = hit["_source"]
            data["_id"] = hit["_id"]
            yield data


# Basic incremental stream
class IncrementalElasticSearchV2Stream(ElasticSearchV2Stream, IncrementalMixin, ABC):
    # point in time
    pit = ""
    date_start = ""
    _cursor_value = ""

    def __init__(self, date_start):
        super().__init__(date_start)

    @property
    def cursor_field(self) -> str:
        """
        Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
        usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.

        :return str: The name of the cursor field.
        """
        return "updated_at"

    @property
    def state(self) -> MutableMapping[str, Any]:
        """State getter, should return state in form that can serialized to a string and send to the output
        as a STATE AirbyteMessage.

        A good example of a state is a _cursor_value:
            {
                self.cursor_field: "_cursor_value"
            }

         State should try to be as small as possible but at the same time descriptive enough to restore
         syncing process from the point where it stopped.
        """

        return {"date": "2024-03-20"}

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        """State setter, accept state serialized by state getter."""
        self._cursor_value = {"date": "2024-03-20"}

    def get_updated_state(self, a, b):
        return {"date": "2024-03-20"}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """

        hits = response.json()["hits"]["hits"]

        try:
            last_document_timestamp = hits[len(hits) - 1].get("_source")["updated_at"]
            self._cursor_value = {"date": "2024-03-20"}
        except KeyError as k:
            last_document_timestamp = hits[len(hits) - 1].get("_source")["date"]
            self._cursor_value = {"date": "2024-03-20"}
        except IndexError as e:
            print("No more documents")

        for hit in hits:
            data = hit["_source"]
            data["_id"] = hit["_id"]
            yield data


# Source
class SourceElasticSearchV2(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """

        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """

        client = Elasticsearch("http://aes-statistic01.prod.dld:9200")
        response = client.ping(request_timeout=5)

        return response, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """

        date_start = config["date_start"]

        return [Campaigns(date_start), Accounts(date_start), Creatives(date_start)]


class Creatives(IncrementalElasticSearchV2Stream):
    cursor_field = "updated_at"
    primary_key = "_id"
    date_start = ""
    index = "statistics_ad_creative*"

    def request_body_data(
            self,
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, Any] = None,
            next_page_token: int = 0,
    ) -> Optional[Union[Mapping, str]]:
        payload = super().request_body_data(stream_state, stream_slice, next_page_token)

        payload["sort"] = [
            "date",
            "updated_at",
            "ad_creative",
            "image"
        ]

        return json.dumps(payload)


class Campaigns(IncrementalElasticSearchV2Stream):
    cursor_field = "updated_at"
    primary_key = "_id"
    pit = ""
    client: Elasticsearch = Elasticsearch("http://aes-statistic01.prod.dld:9200")
    index = "statistics_campaign*"

    @property
    def state(self) -> MutableMapping[str, Any]:
        """State getter, should return state in form that can serialized to a string and send to the output
        as a STATE AirbyteMessage.

        A good example of a state is a _cursor_value:
            {
                self.cursor_field: "_cursor_value"
            }

         State should try to be as small as possible but at the same time descriptive enough to restore
         syncing process from the point where it stopped.
        """

        return {"date": "2024-03-20"}

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        """State setter, accept state serialized by state getter."""
        self._cursor_value = {"date": "2024-03-20"}

    def request_body_data(
            self,
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, Any] = None,
            next_page_token: int = 0,
    ) -> Optional[Union[Mapping, str]]:
        payload = super().request_body_data(stream_state, stream_slice, next_page_token)

        payload["sort"] = [
            "date",
            "updated_at",
            "campaign"
        ]

        return json.dumps(payload)


class Accounts(IncrementalElasticSearchV2Stream):
    cursor_field = "updated_at"
    primary_key = "_id"
    pit = ""
    client: Elasticsearch = Elasticsearch("http://aes-statistic01.prod.dld:9200")
    index = "statistics_account*"
    _cursor_value = None
    stream_name = "accounts"

    @property
    def state(self) -> MutableMapping[str, Any]:
        """State getter, should return state in form that can serialized to a string and send to the output
        as a STATE AirbyteMessage.

        A good example of a state is a _cursor_value:
            {
                self.cursor_field: "_cursor_value"
            }

         State should try to be as small as possible but at the same time descriptive enough to restore
         syncing process from the point where it stopped.
        """

        return {"date": "2024-03-20"}

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        """State setter, accept state serialized by state getter."""
        self._cursor_value = {"date": "2024-03-20"}

    def request_body_data(
            self,
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, Any] = None,
            next_page_token: int = 0,
    ) -> Optional[Union[Mapping, str]]:
        payload = super().request_body_data(stream_state, stream_slice, next_page_token)

        payload["sort"] = [
            "date",
            "updated_at",
            "account"
        ]

        return json.dumps(payload)

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
            request_headers = self.request_headers(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
            request = self._create_prepared_request(
                path=self.path(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
                headers=dict(request_headers, **self.authenticator.get_auth_header()),
                params=self.request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
                json=self.request_body_json(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
                data=self.request_body_data(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
            )
            request_kwargs = self.request_kwargs(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)

            logging.getLogger("Request : " + str(request) + ", request args : " + str(request_kwargs))

            if self.use_cache:
                # use context manager to handle and store cassette metadata
                with self.cache_file as cass:
                    self.cassete = cass
                    # vcr tries to find records based on the request, if such records exist, return from cache file
                    # else make a request and save record in cache file
                    response = self._send_request(request, request_kwargs)

            else:
                response = self._send_request(request, request_kwargs)

            yield from self.parse_response(response, stream_state=stream_state, stream_slice=stream_slice)

            next_page_token = self.next_page_token(response)

            hits = response.json().get("hits").get("hits")

            try:
                last_doc = hits[len(hits) - 1].get("_source")
            except IndexError as e:
                pagination_complete = True

            if "updated_at" in last_doc:
                self._cursor_value = {"date": "2024-03-20"}
            else:
                self._cursor_value = {"date": "2024-03-20"}

        # Always return an empty generator just in case no records were ever yielded
        yield from []
