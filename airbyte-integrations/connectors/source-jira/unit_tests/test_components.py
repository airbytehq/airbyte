# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
from unittest.mock import MagicMock

import pytest
import requests

from airbyte_cdk.sources.declarative.types import StreamSlice


@pytest.mark.parametrize(
    "json_response, expected_output",
    [
        ({"values": ["label 1", "label 2", "label 3"]}, [{"label": "label 1"}, {"label": "label 2"}, {"label": "label 3"}]),
        (["label 1", "label 2", "label 3"], []),
        ([], []),  # Testing an empty response
    ],
)
def test_labels_record_extractor(json_response, expected_output, components_module):
    extractor = components_module.LabelsRecordExtractor(["values"], {}, {})

    response_mock = MagicMock(spec=requests.Response)
    response_mock.json.return_value = json_response
    response_mock.content = json.dumps(json_response).encode("utf-8")
    response_mock.text = json.dumps(json_response)
    response_mock.status_code = 200

    extracted = extractor.extract_records(response_mock)
    assert extracted == expected_output


@pytest.mark.parametrize(
    "fields_data, other_data, expected_fields, expected_partition",
    [
        # Test case with one field value and one record from other parent stream
        (
            [{"partition_id": "field_value"}],  # fields parent stream output
            [{"partition_id": "other_value"}],  # other parent stream output
            [1, "key", "status", "created", "updated"],  # expected fields value in stream slices
            2,  # expected partition value in stream slices
        )
    ],
)
def test_sprint_issues_substream_partition_router(fields_data, other_data, expected_fields, expected_partition, components_module):
    fields_parent_stream = MagicMock()
    fields_parent_stream_config = MagicMock(stream=fields_parent_stream, partition_field=MagicMock())
    fields_parent_stream_config.partition_field.eval.return_value = "partition_id"
    fields_parent_stream_config.parent_key.eval.return_value = "id"
    other_parent_stream = MagicMock()
    other_parent_stream_config = MagicMock(stream=other_parent_stream, partition_field=MagicMock())
    other_parent_stream_config.partition_field.eval.return_value = "partition_id"
    other_parent_stream_config.parent_key.eval.return_value = "id"

    # Initialize the router inside the test
    router = components_module.SprintIssuesSubstreamPartitionRouter(
        parent_stream_configs=[fields_parent_stream_config, other_parent_stream_config], config={}, parameters={}
    )

    # Mocking fields_parent_stream to return specific stream slices
    fields_parent_stream.stream_slices.return_value = [StreamSlice(partition={"partition_id": val}, cursor_slice={}) for val in fields_data]
    fields_parent_stream.read_only_records.return_value = [{"id": 1, "partition_id": val} for val in fields_data]

    # Mocking other_parent_stream to return specific stream slices
    other_parent_stream.stream_slices.return_value = [StreamSlice(partition={"partition_id": val}, cursor_slice={}) for val in other_data]
    other_parent_stream.read_only_records.return_value = [{"id": 2, "partition_id": val} for val in other_data]

    # Collecting results from stream_slices
    slices = list(router.stream_slices())

    assert slices, "There should be at least one slice generated"
    # Asserting the correct parent stream fields are set in slices
    assert all(
        _slice.extra_fields["fields"] == expected_fields for _slice in slices
    ), f"Expected parent stream fields {expected_fields}, but got {slices}"
    assert all(
        _slice.partition["partition_id"] == expected_partition for _slice in slices
    ), f"Expected partition ID {expected_partition}, but got {slices}"
