#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import json
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

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

    @property
    def http_method(self) -> str:
        """
        Override if needed. See get_request_data/get_request_json if using POST/PUT/PATCH.
        """
        return "POST"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        docs = response.json()["hits"]["hits"]
        if response.status_code == 200 and docs != []:
            scroll_id = response.json()["_scroll_id"]
            return scroll_id
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

        if next_page_token is None:
            next_page_token = 0

            payload = {
                "query": {
                    "query_string": {
                        "query": "*"
                    }
                },
                "size": 10000
            }

        else:
            payload = {"scroll": "10m",
                       "scroll_id": next_page_token
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
    """
    TODO fill in details of this class to implement functionality related to incremental syncs for your connector.
         if you do not need to implement incremental sync for any streams, remove this class.
    """

    # TODO: Fill in to checkpoint stream reads after N records. This prevents re-reading of data if the stream fails for any reason.
    state_checkpoint_interval = 100

    @property
    def cursor_field(self) -> str:
        """
        TODO
        Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
        usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.

        :return str: The name of the cursor field.
        """
        return "value"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """
        return latest_record

# Source
class SourceElasticSearchV2(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        TODO: Implement a connection check to validate that the user-provided config can be used to connect to the underlying API

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
        if next_page_token is None:
            return "statistics_ad_creative*" + "/_search" + "?scroll=10m"
        else:
            return "/_search" + "/scroll"


class Campaigns(IncrementalElasticSearchV2Stream):

    cursor_field = "date"

    primary_key = "_id"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        if next_page_token is None:
            return "statistics_campaign*" + "/_search" + "?scroll=10m"
        else:
            return "/_search" + "/scroll"


class Accounts(IncrementalElasticSearchV2Stream):

    cursor_field = "date"

    primary_key = "_id"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        if next_page_token is None:
            return "statistics_account*" + "/_search" + "?scroll=10m"
        else:
            return "/_search" + "/scroll"
