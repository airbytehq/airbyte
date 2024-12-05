#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Any, List, Mapping, Optional, Union

import requests
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.paginators.strategies import OffsetIncrement


@dataclass
class ZendeskChatIdOffsetIncrementPaginationStrategy(OffsetIncrement):
    """
    Id Offset Pagination docs:
        https://developer.zendesk.com/api-reference/live-chat/chat-api/agents/#pagination

    Attributes:
        page_size (InterpolatedString): the number of records to request,
        id_field (InterpolatedString): the name of the <key> to track and increment from, {<key>: 1234}
    """

    id_field: Union[InterpolatedString, str] = None

    def __post_init__(self, parameters: Mapping[str, Any], **kwargs) -> None:
        if not self.id_field:
            raise ValueError("The `id_field` property is missing, with no-default value.")
        else:
            self._id_field = InterpolatedString.create(self.id_field, parameters=parameters).eval(self.config)
        super().__post_init__(parameters=parameters, **kwargs)

    def should_stop_pagination(self, decoded_response: Mapping[str, Any], last_records: List[Mapping[str, Any]]) -> bool:
        """
        Stop paginating when there are fewer records than the page size or the current page has no records
        """
        last_records_len = len(last_records)
        no_records = last_records_len == 0
        current_page_len = self._page_size.eval(self.config, response=decoded_response)
        return (self._page_size and last_records_len < current_page_len) or no_records

    def get_next_page_token_offset(self, last_records: List[Mapping[str, Any]]) -> int:
        """
        The `IDs` are returned in `ASC` order, we add `+1` to the ID integer value to avoid the record duplicates,
        Described in: https://developer.zendesk.com/api-reference/live-chat/chat-api/agents/#pagination

        Arguments:
            last_records: List[Records] -- decoded from the RESPONSE.

        Returns:
            The offset value as the `next_page_token`
        """
        self._offset = last_records[-1][self._id_field]
        return self._offset + 1

    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Any]:
        decoded_response = self.decoder.decode(response)
        if self.should_stop_pagination(decoded_response, last_records):
            return None
        else:
            return self.get_next_page_token_offset(last_records)
