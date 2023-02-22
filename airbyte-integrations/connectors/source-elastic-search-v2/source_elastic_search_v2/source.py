#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

from elasticsearch import Elasticsearch
import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.core import IncrementalMixin
from airbyte_cdk.models import SyncMode

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

    @property
    def http_method(self) -> str:
        """
        Override if needed. See get_request_data/get_request_json if using POST/PUT/PATCH.
        """
        return "POST"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        docs = response.json()["hits"]["hits"]
        if response.status_code == 200 and docs != []:
            search_after = docs[len(docs) - 1].get("sort")
            return search_after
        else:
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
            date_filter_start = "2020-01-01"
        else:
            date_filter_start = stream_state.get("date")

        self.logger.info("Date filter : {}".format(date_filter_start))

        if next_page_token is None:
            payload = {
                "query": {
                    "bool": {
                        "filter": [
                            {
                                "range": {
                                    "date": {
                                        "gte": date_filter_start
                                    }
                                }
                            }
                        ]
                    }
                },
                "size": 10000,
                "sort": [
                    "date"
                ]
            }

        else:
            payload = {
                "query": {
                    "query_string": {
                        "query": "*"
                    }
                },
                "size": 10000,
                "search_after": next_page_token,
                "sort": [
                    "date"
                ]
            }

        return json.dumps(payload)

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """

        hits = response.json()["hits"]["hits"]

        for hit in hits:
            data = hit["_source"]
            yield data


# Basic incremental stream
class IncrementalElasticSearchV2Stream(ElasticSearchV2Stream, ABC):
    state_checkpoint_interval = 10
    _cursor_value = ""

    @property
    def cursor_field(self) -> str:
        """
        Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
        usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.

        :return str: The name of the cursor field.
        """
        return "date"

    @property
    def state(self) -> MutableMapping[str, Any]:
        """State getter, should return state in form that can serialized to a string and send to the output
        as a STATE AirbyteMessage.

        A good example of a state is a cursor_value:
            {
                self.cursor_field: "cursor_value"
            }

         State should try to be as small as possible but at the same time descriptive enough to restore
         syncing process from the point where it stopped.
        """

        return {self.cursor_field: self._cursor_value}

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        """State setter, accept state serialized by state getter."""
        self._cursor_value = value[self.cursor_field]

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

            if not next_page_token:
                pagination_complete = True

                try:
                    last_day = hits[len(hits) - 1].get("_source").get("date")
                    # Use day before date to not miss any documents
                    date_day_before = datetime.fromisoformat(last_day) - timedelta(days=1)
                    self._cursor_value = datetime.strftime(date_day_before, "%Y-%m-%d")

                except UnboundLocalError as e:
                    self.logger.info("No document found")

            hits = response.json().get("hits").get("hits")

        # Always return an empty generator just in case no records were ever yielded
        yield from []


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
        TODO: Replace the streams below with your own streams.

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        return [Creatives(), Campaigns(), Accounts()]


class Creatives(IncrementalElasticSearchV2Stream):
    cursor_field = "date"

    primary_key = "_id"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "statistics_ad_creative*" + "/_search"

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
            date_filter_start = "2020-01-01"
        else:
            date_filter_start = stream_state.get("date")

        self.logger.info("Date filter : {}".format(date_filter_start))

        if next_page_token is None:
            payload = {
                "query": {
                    "bool": {
                        "filter": [
                            {
                                "range": {
                                    "date": {
                                        "gte": date_filter_start
                                    }
                                }
                            }
                        ]
                    }
                },
                "size": 10000,
                "sort": [
                    "date",
                    "ad_creative",
                    "image"
                ]
            }

        else:
            payload = {
                "query": {
                    "query_string": {
                        "query": "*"
                    }
                },
                "size": 10000,
                "search_after": next_page_token,
                "sort": [
                    "date",
                    "ad_creative",
                    "image"
                ]
            }

        return json.dumps(payload)


class Campaigns(IncrementalElasticSearchV2Stream):
    cursor_field = "date"

    primary_key = "_id"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "statistics_campaign*" + "/_search"

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
            date_filter_start = "2020-01-01"
        else:
            date_filter_start = stream_state.get("date")

        self.logger.info("Date filter : {}".format(date_filter_start))

        if next_page_token is None:
            payload = {
                "query": {
                    "bool": {
                        "filter": [
                            {
                                "range": {
                                    "date": {
                                        "gte": date_filter_start
                                    }
                                }
                            }
                        ]
                    }
                },
                "size": 10000,
                "sort": [
                    "date",
                    "campaign"
                ]
            }

        else:
            payload = {
                "query": {
                    "query_string": {
                        "query": "*"
                    }
                },
                "size": 10000,
                "search_after": next_page_token,
                "sort": [
                    "date",
                    "campaign"
                ]
            }

        return json.dumps(payload)


class Accounts(IncrementalElasticSearchV2Stream):
    cursor_field = "date"

    primary_key = "_id"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "statistics_account*" + "/_search"

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
            date_filter_start = "2020-01-01"
        else:
            date_filter_start = stream_state.get("date")

        self.logger.info("Date filter : {}".format(date_filter_start))

        if next_page_token is None:
            payload = {
                "query": {
                    "bool": {
                        "filter": [
                            {
                                "range": {
                                    "date": {
                                        "gte": date_filter_start
                                    }
                                }
                            }
                        ]
                    }
                },
                "size": 10000,
                "sort": [
                    "date",
                    "account"
                ]
            }

        else:
            payload = {
                "query": {
                    "query_string": {
                        "query": "*"
                    }
                },
                "size": 10000,
                "search_after": next_page_token,
                "sort": [
                    "date",
                    "account"
                ]
            }

        return json.dumps(payload)
