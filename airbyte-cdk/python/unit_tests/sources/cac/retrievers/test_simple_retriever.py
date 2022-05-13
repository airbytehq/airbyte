#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from unittest.mock import MagicMock

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.cac.retrievers.simple_retriever import SimpleRetriever

primary_key = "pk"
records = [{"id": 1}, {"id": 2}]


def test():
    requester = MagicMock()
    request_params = {"param": "value"}
    requester.request_params.return_value = request_params

    paginator = MagicMock()
    next_page_token = {"cursor": "cursor_value"}
    paginator.next_page_token.return_value = next_page_token

    extractor = MagicMock()
    extractor.extract_records.return_value = records

    iterator = MagicMock()
    stream_slices = [{"date": "2022-01-01"}, {"date": "2022-01-02"}]
    iterator.stream_slices.return_value = stream_slices

    response = requests.Response()

    state = MagicMock()
    underlying_state = {"date": "2021-01-01"}
    state.get_state.return_value = underlying_state

    url_base = "https://airbyte.io"
    path = "/v1"
    requester.get_url_base.return_value = url_base
    requester.get_path.return_value = path

    retriever = SimpleRetriever(primary_key, requester, paginator, extractor, iterator, state)

    # hack because we clone the state...
    retriever._state = state

    assert retriever.primary_key == primary_key
    assert retriever.url_base == url_base
    assert retriever.path() == path
    assert retriever.get_state() == underlying_state
    assert retriever.next_page_token(response) == next_page_token
    assert retriever.request_params(None, None, None) == request_params
    assert retriever.stream_slices(sync_mode=SyncMode.incremental) == stream_slices

    assert retriever._last_response is None
    assert retriever._last_records is None
    assert retriever.parse_response(response, stream_state=None) == records
    assert retriever._last_response == response
    assert retriever._last_records == records
