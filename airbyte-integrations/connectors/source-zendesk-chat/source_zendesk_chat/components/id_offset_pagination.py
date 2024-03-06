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

    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Any]:
        decoded_response = self.decoder.decode(response)
        # Stop paginating when there are fewer records than the page size or the current page has no records
        if (self._page_size and len(last_records) < self._page_size.eval(self.config, response=decoded_response)) or len(last_records) == 0:
            return None
        else:
            # the `IDs` are returned in `ASC` order, we add `+1` to the ID integer value to avoid the record duplicates,
            # as described in: https://developer.zendesk.com/api-reference/live-chat/chat-api/agents/#pagination
            self._offset = last_records[-1][self._id_field]
            return self._offset + 1
