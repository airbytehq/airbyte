# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from unittest import mock

from dagster import build_op_context
from google.cloud.storage import Blob
from orchestrator.assets import registry_entry
from orchestrator.jobs.registry import add_new_metadata_partitions_op, remove_stale_metadata_partitions_op


def test_basic_partition():
    context = build_op_context()
    partition_key = "test_partition_key"

    existing_partitions = context.instance.get_dynamic_partitions(partition_key)
    assert len(existing_partitions) == 0
    context.instance.add_dynamic_partitions(partition_key, ["partition_1", "partition_2"])
    existing_partitions = context.instance.get_dynamic_partitions(partition_key)
    assert len(existing_partitions) == 2


def test_metadata_partition_remove():
    mock_fresh_blob_1 = mock.create_autospec(Blob, instance=True)
    mock_fresh_blob_1.etag = "fresh_etag_1"
    mock_fresh_blob_1.name = "fresh_metadata"

    mock_fresh_blob_2 = mock.create_autospec(Blob, instance=True)
    mock_fresh_blob_2.etag = "fresh_etag_2"
    mock_fresh_blob_2.name = "fresh_metadata"

    mock_stale_blob = mock.create_autospec(Blob, instance=True)
    mock_stale_blob.etag = "stale_etag"
    mock_stale_blob.name = "stale_metadata"

    mock_metadata_file_blobs = [mock_fresh_blob_1, mock_fresh_blob_2]

    resources = {"all_metadata_file_blobs": mock_metadata_file_blobs}

    context = build_op_context(resources=resources)

    partition_key = registry_entry.metadata_partitions_def.name

    existing_partitions = context.instance.get_dynamic_partitions(partition_key)
    assert len(existing_partitions) == 0

    context.instance.add_dynamic_partitions(partition_key, [mock_fresh_blob_1.etag, mock_stale_blob.etag])
    existing_partitions = context.instance.get_dynamic_partitions(partition_key)
    assert len(existing_partitions) == 2

    remove_stale_metadata_partitions_op(context)

    existing_partitions = context.instance.get_dynamic_partitions(partition_key)
    assert len(existing_partitions) == 1
    assert mock_stale_blob.etag not in existing_partitions


def test_metadata_partition_add():
    mock_fresh_blob_1 = mock.create_autospec(Blob, instance=True)
    mock_fresh_blob_1.etag = "fresh_etag_1"
    mock_fresh_blob_1.name = "fresh_metadata"

    mock_fresh_blob_2 = mock.create_autospec(Blob, instance=True)
    mock_fresh_blob_2.etag = "fresh_etag_2"
    mock_fresh_blob_2.name = "fresh_metadata"

    mock_existing_blob = mock.create_autospec(Blob, instance=True)
    mock_existing_blob.etag = "existing_etag"
    mock_existing_blob.name = "existing_metadata"

    mock_stale_blob = mock.create_autospec(Blob, instance=True)
    mock_stale_blob.etag = "stale_etag"
    mock_stale_blob.name = "stale_metadata"

    mock_metadata_file_blobs = [mock_fresh_blob_1, mock_fresh_blob_2]

    mock_slack = mock.MagicMock()
    mock_slack.get_client = mock.MagicMock()
    chat_postMessage = mock.MagicMock()
    mock_slack.get_client.return_value = chat_postMessage

    resources = {"slack": mock_slack, "all_metadata_file_blobs": mock_metadata_file_blobs}

    context = build_op_context(resources=resources)

    partition_key = registry_entry.metadata_partitions_def.name

    existing_partitions = context.instance.get_dynamic_partitions(partition_key)
    assert len(existing_partitions) == 0

    context.instance.add_dynamic_partitions(partition_key, [mock_stale_blob.etag, mock_existing_blob.etag])
    existing_partitions = context.instance.get_dynamic_partitions(partition_key)
    assert len(existing_partitions) == 2

    add_new_metadata_partitions_op(context)

    existing_partitions = context.instance.get_dynamic_partitions(partition_key)
    expected_partitions = [mock_fresh_blob_1.etag, mock_fresh_blob_2.etag, mock_existing_blob.etag, mock_stale_blob.etag]

    # assert all expected partitions are in the existing partitions, and no other partitions are present, order does not matter
    assert all([etag in existing_partitions for etag in expected_partitions])
