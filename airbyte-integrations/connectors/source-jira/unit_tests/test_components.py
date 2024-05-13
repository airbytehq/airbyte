# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from unittest.mock import MagicMock

import pytest
import requests
from airbyte_cdk.sources.declarative.types import StreamSlice
from source_jira.components.extractors import LabelsRecordExtractor
from source_jira.components.partition_routers import SprintIssuesSubstreamPartitionRouter, SubstreamPartitionRouterWithContext


@pytest.mark.parametrize(
    "json_response, expected_output",
    [
        ({"values": ["label 1", "label 2", "label 3"]}, [{"label": "label 1"}, {"label": "label 2"}, {"label": "label 3"}]),
        (["label 1", "label 2", "label 3"], []),
        ([], []),  # Testing an empty response
    ],
)
def test_labels_record_extractor(json_response, expected_output):
    # Create the extractor instance directly in the test function
    extractor = LabelsRecordExtractor(["values"], {}, {})
    # Set up the mocked response
    response_mock = MagicMock(spec=requests.Response)
    response_mock.json.return_value = json_response  # Parameterized JSON response

    # Call the extract_records to process the mocked response
    extracted = extractor.extract_records(response_mock)

    # Assert to check if the output matches the expected result
    assert extracted == expected_output, "The extracted records do not match the expected output"


@pytest.mark.parametrize(
    "records, expected_slices",
    [
        # No records in parent stream
        ([], []),
        # Valid records generating stream slices, including checking parent records
        (
            [{"id": 1, "parent_id": 100}, {"id": 2, "parent_id": 200}],
            [
                {"partition": {"partition_id": 100, "parent_slice": {}}, "parent_record": {"id": 1, "parent_id": 100}},
                {"partition": {"partition_id": 200, "parent_slice": {}}, "parent_record": {"id": 2, "parent_id": 200}},
            ],
        ),
    ],
)
def test_stream_slices(records, expected_slices):
    # Mock configuration and parent stream config
    config = MagicMock()
    parent_stream = MagicMock()
    parent_key = MagicMock()
    partition_field = MagicMock()

    parent_key.eval.return_value = "parent_id"
    partition_field.eval.return_value = "partition_id"

    parent_stream_config = MagicMock()
    parent_stream_config.stream = parent_stream
    parent_stream_config.parent_key = parent_key
    parent_stream_config.partition_field = partition_field

    # Initialize the router instance
    router = SubstreamPartitionRouterWithContext(parent_stream_configs=[parent_stream_config], config=config, parameters={})

    # Mocking parent stream's stream_slices and read_records
    parent_stream.stream_slices.return_value = [{}]
    parent_stream.read_records.return_value = records

    slices = list(router.stream_slices())

    # Preparing the output for assertion
    output = [{"partition": slice.partition, "parent_record": getattr(slice, "parent_record", None)} for slice in slices]

    assert output == expected_slices, f"Expected {expected_slices} but got {output}"


@pytest.mark.parametrize(
    "fields_data, other_data, expected_fields, expected_partition",
    [
        # Test case with one field value and one record from other parent stream
        (
            [{"partition_id": "field_value"}],  # fields parent stream output
            [{"partition_id": "other_value"}],  # other parent stream output
            ["field_value"],  # expected fields value in stream slices
            "other_value",  # expected partition value in stream slices
        )
    ],
)
def test_sprint_issues_substream_partition_router(fields_data, other_data, expected_fields, expected_partition):
    fields_parent_stream = MagicMock()
    fields_parent_stream_config = MagicMock(stream=fields_parent_stream, partition_field=MagicMock())
    fields_parent_stream_config.partition_field.eval.return_value = "partition_id"
    other_parent_stream = MagicMock()
    other_parent_stream_config = MagicMock(stream=other_parent_stream, partition_field=MagicMock())
    other_parent_stream_config.partition_field.eval.return_value = "partition_id"

    # Initialize the router inside the test
    router = SprintIssuesSubstreamPartitionRouter(
        parent_stream_configs=[fields_parent_stream_config, other_parent_stream_config], config={}, parameters={}
    )

    # Mocking fields_parent_stream to return specific stream slices
    fields_parent_stream.stream_slices.return_value = [StreamSlice(partition={"partition_id": val}, cursor_slice={}) for val in fields_data]
    fields_parent_stream.read_records.return_value = [{"id": 1, "partition_id": val} for val in fields_data]

    # Mocking other_parent_stream to return specific stream slices
    other_parent_stream.stream_slices.return_value = [StreamSlice(partition={"partition_id": val}, cursor_slice={}) for val in other_data]
    other_parent_stream.read_records.return_value = [{"id": 2, "partition_id": val} for val in other_data]

    # Collecting results from stream_slices
    slices = list(router.stream_slices())

    # Asserting the correct parent stream fields are set in slices
    assert all(
        slice.parent_stream_fields == expected_fields for slice in slices
    ), f"Expected parent stream fields {expected_fields}, but got {slice.parent_stream_fields}"
    assert all(
        slice.partition["partition_id"] == expected_partition for slice in slices
    ), f"Expected partition ID {expected_partition}, but got {slice.partition['partition_id']}"
