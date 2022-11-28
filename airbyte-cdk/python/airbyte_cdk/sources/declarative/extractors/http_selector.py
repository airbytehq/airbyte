#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, List, Mapping, Optional

import requests
from airbyte_cdk.sources.declarative.types import Record, StreamSlice, StreamState
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class HttpSelector(JsonSchemaMixin):
    """
    Responsible for translating an HTTP response into a list of records by extracting records from the response and optionally filtering
    records based on a heuristic.
    """

    @abstractmethod
    def select_records(
        self,
        response: requests.Response,
        stream_state: StreamState,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> List[Record]:
        """
        Selects records from the response
        :param response: The response to select the records from
        :param stream_state: The stream state
        :param stream_slice: The stream slice
        :param next_page_token: The paginator token
        :return: List of Records selected from the response
        """
        pass
