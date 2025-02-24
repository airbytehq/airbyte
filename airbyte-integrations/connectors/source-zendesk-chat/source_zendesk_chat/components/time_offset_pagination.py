#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Any, List, Mapping, Optional, Union

import requests

from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
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

    time_field_name: Union[InterpolatedString, str] = None

    def __post_init__(self, parameters: Mapping[str, Any], **kwargs) -> None:
        if not self.time_field_name:
            raise ValueError("The `time_field_name` property is missing, with no-default value.")
        else:
            self._time_field_name = InterpolatedString.create(self.time_field_name, parameters=parameters).eval(self.config)
        super().__post_init__(parameters=parameters, **kwargs)

    def should_stop_pagination(self, decoded_response: Mapping[str, Any], last_records: List[Mapping[str, Any]]) -> bool:
        """
        Stop paginating when there are fewer records than the page size or the current page has no records
        """
        last_records_len = len(last_records)
        no_records = last_records_len == 0
        current_page_len = self._page_size.eval(self.config, response=decoded_response)
        return (self._page_size and last_records_len < current_page_len) or no_records

    def get_next_page_token_offset(self, decoded_response: Mapping[str, Any]) -> int:
        """
        The `records` are returned in `ASC` order.
        Described in: https://developer.zendesk.com/api-reference/live-chat/chat-api/incremental_export/#incremental-agent-timeline-export

        Arguments:
            decoded_response: Mapping[str, Any] -- The object with RECORDS decoded from the RESPONSE.

        Returns:
            The offset value as the `next_page_token`
        """
        self._offset = decoded_response[self._time_field_name]
        return self._offset

    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Any]:
        decoded_response = self.decoder.decode(response)
        if self.should_stop_pagination(decoded_response, last_records):
            return None
        else:
            return self.get_next_page_token_offset(decoded_response)
