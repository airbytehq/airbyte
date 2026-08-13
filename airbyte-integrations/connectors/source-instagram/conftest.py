# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest


def pytest_collection_modifyitems(config, items):
    skip_basic_read = pytest.mark.skip(
        reason="No Instagram Business Account linked to test Facebook Page " "(see: https://github.com/airbytehq/oncall/issues/11217)"
    )
    for item in items:
        if "test_airbyte_standards" in str(item.fspath) and item.name.startswith("test_basic_read"):
            item.add_marker(skip_basic_read)
