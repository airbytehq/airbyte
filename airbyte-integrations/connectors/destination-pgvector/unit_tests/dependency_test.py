#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from importlib.metadata import version

import pandas as pd
from packaging.version import Version


def test_patched_langchain_core_and_vector_db_imports_are_available():
    assert Version(version("langchain-core")) >= Version("1.2.5")

    from airbyte_cdk.destinations.vector_db_based.config import VectorDBConfigModel
    from airbyte_cdk.destinations.vector_db_based.document_processor import (
        DocumentProcessor,
        ProcessingConfigModel,
    )
    from airbyte_cdk.destinations.vector_db_based.embedder import Embedder, create_from_config

    assert all((
        VectorDBConfigModel,
        DocumentProcessor,
        ProcessingConfigModel,
        Embedder,
        create_from_config,
    ))


def test_pandas_to_sql_accepts_sqlite_uri():
    pd.DataFrame({"value": [1]}).to_sql("table", "sqlite://", if_exists="append", index=False)
