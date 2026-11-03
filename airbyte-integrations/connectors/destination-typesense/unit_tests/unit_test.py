#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pathlib import Path
from unittest.mock import patch

import pytest
import tomllib
from destination_typesense.writer import TypesenseWriter
from packaging.specifiers import SpecifierSet


@pytest.mark.parametrize("filename", ["pyproject.toml", "poetry.lock"])
@pytest.mark.parametrize("version, supported", [("3.10.20", False), ("3.11.0", True), ("3.11.15", True), ("3.12.0", False)])
def test_python_version_range(filename: str, version: str, supported: bool) -> None:
    with (Path(__file__).resolve().parents[1] / filename).open("rb") as file:
        metadata = tomllib.load(file)
    if filename == "pyproject.toml":
        constraint = metadata["tool"]["poetry"]["dependencies"]["python"]
    else:
        constraint = metadata["metadata"]["python-versions"]
    assert (version in SpecifierSet(constraint)) is supported


@patch("typesense.Client")
def test_default_batch_size(client):
    writer = TypesenseWriter(client)
    assert writer.batch_size == 10000


@patch("typesense.Client")
def test_empty_batch_size(client):
    writer = TypesenseWriter(client, "")
    assert writer.batch_size == 10000


@patch("typesense.Client")
def test_custom_batch_size(client):
    writer = TypesenseWriter(client, 9000)
    assert writer.batch_size == 9000


@patch("typesense.Client")
def test_queue_write_operation(client):
    writer = TypesenseWriter(client)
    writer.queue_write_operation("stream_name", {"a": "a"})
    assert len(writer.write_buffer) == 1


@patch("typesense.Client")
def test_flush(client):
    writer = TypesenseWriter(client)
    writer.queue_write_operation("stream_name", {"a": "a"})
    writer.flush()
    client.collections.__getitem__.assert_called_once_with("stream_name")
