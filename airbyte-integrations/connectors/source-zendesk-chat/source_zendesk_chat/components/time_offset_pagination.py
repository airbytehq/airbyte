#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Any, List, Mapping, Optional

import requests
from airbyte_cdk.sources.declarative.requesters.paginators.strategies import OffsetIncrement


@dataclass
class ZendeskChatTimeOffsetIncrementPaginationStrategy(OffsetIncrement):
    """
    Time Offset Pagination docs:
        https://developer.zendesk.com/api-reference/live-chat/chat-api/agents/#pagination
    
    Attributes:
        page_size (InterpolatedString): the number of records to request,
        time_field_name (InterpolatedString): the name of the <key> to track and increment from, {<key>: 1234}
    """
    
    time_field_name: str = None
    
    def __post_init__(self, parameters: Mapping[str, Any], **kwargs):
        if not self.time_field_name:
            raise Exception("The `time_field_name` property is missing, with no-default value.")
        else:
            self._time_field_name = self.time_field_name
        super().__post_init__(parameters=parameters, **kwargs)

    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Any]:
        decoded_response = self.decoder.decode(response)
        # Stop paginating when there are fewer records than the page size or the current page has no records
        if (self._page_size and len(last_records) < self._page_size.eval(self.config, response=decoded_response)) or len(last_records) == 0:
            return None
        else:
            # the `records` are returned in `ASC` order,
            # as described in: https://developer.zendesk.com/api-reference/live-chat/chat-api/incremental_export/#incremental-agent-timeline-export
            self._offset = decoded_response[self._time_field_name]
            return self._offset
