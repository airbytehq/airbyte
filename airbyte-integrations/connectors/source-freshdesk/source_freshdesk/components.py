#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import re
from dataclasses import dataclass
from typing import Any, List, Mapping, MutableMapping, Optional, Tuple
from urllib import parse

import requests
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.cursor_pagination_strategy import CursorPaginationStrategy
from airbyte_cdk.sources.declarative.types import Record, StreamSlice, StreamState


@dataclass
class FreshDeskRequester(HttpRequester):
    NEXT_PAGE_TOKEN_FIELD_NAME = "next_page_token"

    def __post_init__(self, parameters: Mapping[str, Any]):
        super(FreshDeskRequester, self).__post_init__(parameters)

        self.name = parameters.get("name", "").lower()

    def get_request_params(
        self,
        *args,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        """
        Remove page from the request parameters if page > 300 and add an updated_since parameter instead.
        """
        params = super().get_request_params(*args, stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)

        page = next_page_token and next_page_token[self.NEXT_PAGE_TOKEN_FIELD_NAME]
        if self.name == "tickets":
            page, last_updated = page if page else (None, None)
            if last_updated is not None:
                params["updated_since"] = last_updated
                params.pop("page")

        return params

    # We are using an LRU cache in should_retry() method which requires all incoming arguments (including self) to be hashable.
    # Dataclasses by default are not hashable, so we need to define __hash__(). Alternatively, we can set @dataclass(frozen=True),
    # but this has a cascading effect where all dataclass fields must also be set to frozen.
    def __hash__(self):
        return hash(tuple(self.__dict__))


class TicketsPaginationStrategy(CursorPaginationStrategy):
    """
    Cursor increment strategy for the `tickets` stream.
    """

    def __post_init__(self, parameters: Mapping[str, Any]):
        super().__post_init__(parameters=parameters)
        self.ticket_paginate_limit = 300

    def next_page_token(self, response: requests.Response, last_records: List[Record]) -> Optional[Tuple[Optional[int], Optional[int]]]:
        """
        This block extends Incremental stream to overcome '300 page' server error.
        Since the Ticket endpoint has a 300 page pagination limit, after 300 pages, update the parameters with
        query using 'updated_since' = last_record, if there is more data remaining.
        """
        next_token = super().next_page_token(response, last_records)
        last_record_updated = None

        if next_token:
            link_regex = re.compile(r'<(.*?)>;\s*rel="next"')
            link_header = response.headers.get("Link")
            if not link_header:
                return {}
            match = link_regex.search(link_header)
            next_url = match.group(1)
            params = parse.parse_qs(parse.urlparse(next_url).query)

            if int(params["page"][0]) > self.ticket_paginate_limit:
                # get last_record from latest batch, pos. -1, because of ACS order of records
                last_record_updated_at = response.json()[-1]["updated_at"]
                # updating request parameters with last_record state

                last_record_updated = last_record_updated_at

            return (next_token, last_record_updated)
