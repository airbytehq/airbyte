#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import elasticsearch.exceptions
from airbyte_cdk.sources.streams.http.auth import NoAuth, HttpAuthenticator
from elasticsearch import Elasticsearch
import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream

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
            date_filter_start = stream_state.get("date")

        # If this is a new sync
        if next_page_token is None:
            self.pit = self.client.open_point_in_time(index=self.index, keep_alive="1m")
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
                "pit": {
                    "id": self.pit.body["id"],
                    "keep_alive": "1m"
                },
                "size": 10000,
                "sort": [
                    "date",
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

        try:
            last_day = hits[len(hits) - 1].get("_source").get("date")
            # Use day before date to not miss any documents
            date_day_before = datetime.fromisoformat(last_day) - timedelta(days=1)
            self._cursor_value = datetime.strftime(date_day_before, "%Y-%m-%d")

        except IndexError as e:
            self.logger.info("No document found")

        for hit in hits:
            data = hit["_source"]
            data["_id"] = hit["_id"]
            yield data

# Basic incremental stream
class IncrementalElasticSearchV2Stream(ElasticSearchV2Stream, ABC):
    # point in time
    pit = ""
    date_start = ""

    def __init__(self, date_start):
        super().__init__(date_start)

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
    cursor_field = "date"
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
                    "ad_creative",
                    "image"
                    ]

        return json.dumps(payload)


class Campaigns(IncrementalElasticSearchV2Stream):
    cursor_field = "date"
    primary_key = "_id"
    pit = ""
    client: Elasticsearch = Elasticsearch("http://aes-statistic01.prod.dld:9200")
    index = "statistics_campaign*"

    def request_body_data(
            self,
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, Any] = None,
            next_page_token: int = 0,
    ) -> Optional[Union[Mapping, str]]:

        payload = super().request_body_data(stream_state, stream_slice, next_page_token)

        payload["sort"] = [
                    "date",
                    "campaign"
                ]

        return json.dumps(payload)


class Accounts(IncrementalElasticSearchV2Stream):
    cursor_field = "date"
    primary_key = "_id"
    pit = ""
    client: Elasticsearch = Elasticsearch("http://aes-statistic01.prod.dld:9200")
    index = "statistics_account*"

    def request_body_data(
            self,
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, Any] = None,
            next_page_token: int = 0,
    ) -> Optional[Union[Mapping, str]]:

        payload = super().request_body_data(stream_state, stream_slice, next_page_token)

        payload["sort"] = [
                    "date",
                    "account"
                ]

        return json.dumps(payload)
