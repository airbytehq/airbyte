#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
from unittest.mock import MagicMock, patch

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.retrievers.substream_retriever import SubstreamRetriever


@patch("airbyte_cdk.sources.streams.http.http.HttpStream.read_records", return_value=(y for y in [{"id": 1, "data": "B"}]))
def test_substream_retriever(method):
    substream_name = "substream"
    primary_key = "id"
    requester = MagicMock()
    paginator = MagicMock()
    extractor = MagicMock()
    stream_slicer = MagicMock()
    state = MagicMock()
    parent_stream = MagicMock()
    parent_extractor = MagicMock()
    retriever = SubstreamRetriever(
        substream_name, primary_key, requester, paginator, extractor, stream_slicer, state, parent_stream, parent_extractor
    )

    paginator.next_page_token.return_value = {"starting_after": 0}
    parent_records = [{"id": "1234", "data": "some_data", "sub": {"data": [{"id": 0, "data": "A"}]}}]

    parent_stream.read_records.return_value = parent_records
    parent_extractor.extract_records.return_value = [{"data": [{"id": 0, "data": "A"}]}]
    extractor.extract_records.return_value = [{"id": 0, "data": "A"}]

    records = [r for r in retriever.read_records(SyncMode.full_refresh)]
    expected_records = [{"id": 0, "data": "A"}, {"id": 1, "data": "B"}]

    assert records == expected_records
