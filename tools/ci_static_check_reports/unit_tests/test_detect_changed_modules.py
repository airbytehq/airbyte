#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from typing import List, Set

import pytest
from ci_detect_changed_modules.main import list_changed_modules


@pytest.mark.parametrize(
    "changed_files,changed_modules",
    [
        (["path/to/file1", "file2.txt", "path/to/file3.txt"], []),
        (
            [
                "airbyte-cdk/python/airbyte_cdk/entrypoint.py",
                "airbyte-cdk/python/airbyte_cdk/file1",
                "airbyte-cdk/python/airbyte_cdk/file2.py",
            ],
            [{"dir": "airbyte-cdk/python", "lang": "py"}],
        ),
        (
            [
                "airbyte-cdk/python/airbyte_cdk/entrypoint.py",
                "airbyte-integrations/connectors/source-asana/source_asana/streams.py",
                "airbyte-integrations/connectors/source-asana/source_asana/source.py",
                "airbyte-integrations/connectors/source-braintree/integration_tests/abnormal_state.json",
            ],
            [{"dir": "airbyte-cdk/python", "lang": "py"}, {"dir": "airbyte-integrations/connectors/source-asana", "lang": "py"}],
        ),
        (
            [],
            [],
        ),
        # TODO: update test after non-python modules are supported
        (
            [
                "airbyte-integrations/connectors/source-clickhouse-strict-encrypt/src/main/"
                "java/io/airbyte/integrations/source/clickhouse/ClickHouseStrictEncryptSource.java"
            ],
            [],
        ),
        (
            ["airbyte-integrations/connectors/source-instagram/source_instagram/schemas/stories.json"],
            [],
        ),
        (
            ["airbyte-integrations/connectors/destination-amazon-sqs/destination_amazon_sqs/destination.py"],
            [
                {"dir": "airbyte-integrations/connectors/destination-amazon-sqs", "lang": "py"},
            ],
        ),
    ],
)
def test_list_changed_modules(changed_files: List[str], changed_modules: Set[str]) -> None:
    calculated_changed_modules = list_changed_modules(changed_files)

    assert calculated_changed_modules == changed_modules
