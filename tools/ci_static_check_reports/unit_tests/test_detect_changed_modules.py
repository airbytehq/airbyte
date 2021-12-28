#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from typing import List, Set

import pytest

from ..detect_changed_modules import list_changed_modules


@pytest.mark.parametrize(
    "changed_files,changed_modules",
    [
        (["path/to/file1", "file2.txt", "path/to/file3.txt"], set()),
        (
            [
                "airbyte-cdk/python/airbyte_cdk/entrypoint.py",
                "airbyte-cdk/python/airbyte_cdk/file1",
                "airbyte-cdk/python/airbyte_cdk/file2.py",
            ],
            {"airbyte-cdk/python"},
        ),
        (
            [
                "airbyte-cdk/python/airbyte_cdk/entrypoint.py",
                "airbyte-integrations/connectors/source-asana/source_asana/streams.py",
                "airbyte-integrations/connectors/source-asana/source_asana/source.py",
                "airbyte-integrations/connectors/source-braintree/integration_tests/abnormal_state.json",
            ],
            {"airbyte-cdk/python", "airbyte-integrations/connectors/source-asana"},
        ),
    ],
)
def test_list_changed_modules(changed_files: List[str], changed_modules: Set[str]) -> None:
    calculated_changed_modules = list_changed_modules(changed_files)

    assert calculated_changed_modules == changed_modules
