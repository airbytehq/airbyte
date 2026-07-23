# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Shared test fixtures for unit tests."""

import pytest


MOCK_CONFIG = {
    "subdomain": "test",
    "api_key": "test-key",
    "api_secret": "test-secret",
    "workspace_id": "W456",
    "sync_from_date": "2026-01-01T00:00:00Z",
    "custom_filter_json": "[]",
}

MOCK_CONFIG_MINIMAL = {
    "subdomain": "test",
    "api_key": "test-key",
    "api_secret": "test-secret",
}

MOCK_TABLE_METADATA = {
    "id": "T123",
    "label": "Test Table",
    "columns": [
        {"name": "field1", "label": "Field One", "dataType": {"type": "string"}},
        {"name": "field2", "label": "Field Two", "dataType": {"type": "integer"}},
        {"name": "link1", "label": "Link Field", "dataType": {"type": "tableLink"}},
    ],
}

MOCK_TABLES_LIST = [
    {
        "id": "tbl_abc123",
        "label": "Inventory",
        "columns": [
            {"name": "sku", "label": "SKU", "dataType": {"type": "string"}},
            {"name": "qty", "label": "Quantity", "dataType": {"type": "integer"}},
        ],
    },
    {
        "id": "tbl_def456",
        "label": "Quality Checks",
        "columns": [
            {"name": "status", "label": "Status", "dataType": {"type": "string"}},
            {"name": "passed", "label": "Passed", "dataType": {"type": "boolean"}},
        ],
    },
]


@pytest.fixture
def mock_config():
    return MOCK_CONFIG.copy()


@pytest.fixture
def mock_config_minimal():
    return MOCK_CONFIG_MINIMAL.copy()


@pytest.fixture
def mock_table_metadata():
    return MOCK_TABLE_METADATA.copy()


@pytest.fixture
def mock_tables_list():
    import copy

    return copy.deepcopy(MOCK_TABLES_LIST)
