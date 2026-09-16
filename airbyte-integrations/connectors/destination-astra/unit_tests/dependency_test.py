#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from importlib.metadata import version

from packaging.version import Version


def test_patched_langchain_core_and_vector_db_imports_are_available():
    assert Version(version("langchain-core")) >= Version("1.2.5")

    from airbyte_cdk.destinations.vector_db_based.document_processor import DocumentProcessor
    from airbyte_cdk.destinations.vector_db_based.embedder import Embedder, create_from_config
    from airbyte_cdk.destinations.vector_db_based.indexer import Indexer
    from airbyte_cdk.destinations.vector_db_based.writer import Writer

    assert all((DocumentProcessor, Embedder, Indexer, Writer, create_from_config))
