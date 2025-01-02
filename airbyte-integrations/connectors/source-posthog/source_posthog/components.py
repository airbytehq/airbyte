#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, MutableMapping, Optional
from urllib.parse import parse_qs, urlparse

from airbyte_cdk.sources.declarative.incremental import Cursor
from airbyte_cdk.sources.declarative.retrievers.simple_retriever import SimpleRetriever
from airbyte_cdk.sources.declarative.stream_slicers import CartesianProductStreamSlicer
from airbyte_cdk.sources.declarative.types import Record, StreamSlice, StreamState
from airbyte_cdk.sources.declarative.requesters import HttpRequester


@dataclass
class EventsSimpleRetriever(SimpleRetriever):
    def __post_init__(self, parameters: Mapping[str, Any]):
        super().__post_init__(parameters)
        self.cursor = self.stream_slicer if isinstance(self.stream_slicer, Cursor) else None

    def request_params(
        self,
        stream_state: StreamSlice,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        """Events API return records in descendent order (newest first).
        Default page limit is 100 items.

        Even though API mentions such pagination params as 'limit' and 'offset', they are actually ignored.
        Instead, response contains 'next' url with datetime range for next OLDER records, like:

        response:
        {
            "next": "https://app.posthog.com/api/projects/2331/events?after=2021-01-01T00%3A00%3A00.000000Z&before=2021-05-29T16%3A44%3A43.175000%2B00%3A00",
            "results": [
                {id ...},
                {id ...},
            ]
        }

        So if next_page_token is set (contains 'after'/'before' params),
        then stream_slice params ('after'/'before') should be ignored.
        """

        if next_page_token:
            stream_slice = {}

        return self._get_request_options(
            stream_slice,
            next_page_token,
            self.requester.get_request_params,
            self.paginator.get_request_params,
            self.stream_slicer.get_request_params,
            self.requester.get_authenticator().get_request_body_json,
        )


@dataclass
class EventsHttpRequester(HttpRequester):
    def _request_params(
        self,
        stream_state: Optional[StreamState],
        stream_slice: Optional[StreamSlice],
        next_page_token: Optional[Mapping[str, Any]],
        extra_params: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        """
        Specifies the query parameters that should be set on an outgoing HTTP request given the inputs.
        """
        if next_page_token is not None:
            url = next_page_token['next_page_token']
            parsed_url = urlparse(url)

            options = dict((k, v[0] if isinstance(v, list) else v)
                           for k, v in parse_qs(parsed_url.query).items())

        else:
            options = self._get_request_options(
                stream_state, stream_slice, next_page_token, self.get_request_params, self.get_authenticator(
                ).get_request_params, extra_params
            )
        if isinstance(options, str):
            raise ValueError("Request params cannot be a string")

        for k, v in options.items():
            if isinstance(v, (list, dict)):
                raise ValueError(
                    f"Invalid value for `{k}` parameter. The values of request params cannot be an array or object.")

        return options
