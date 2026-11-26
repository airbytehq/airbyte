#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from importlib.metadata import version
from pathlib import Path

import pytest
import tomllib
from packaging.version import Version


@pytest.mark.parametrize("filename", ["pyproject.toml", "poetry.lock"])
def test_python_requirement_is_limited_to_python_311(filename: str) -> None:
    with (Path(__file__).resolve().parents[1] / filename).open("rb") as file:
        metadata = tomllib.load(file)

    if filename == "pyproject.toml":
        requirement = metadata["tool"]["poetry"]["dependencies"]["python"]
    else:
        requirement = metadata["metadata"]["python-versions"]

    assert requirement == "^3.11,<3.12"


def test_patched_langchain_core_and_vector_db_imports_are_available():
    assert Version(version("langchain-core")) >= Version("1.2.5")

    from airbyte_cdk.destinations.vector_db_based.document_processor import DocumentProcessor
    from airbyte_cdk.destinations.vector_db_based.embedder import Embedder, create_from_config
    from airbyte_cdk.destinations.vector_db_based.indexer import Indexer
    from airbyte_cdk.destinations.vector_db_based.writer import Writer

    assert all((DocumentProcessor, Embedder, Indexer, Writer, create_from_config))
