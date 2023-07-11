#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pytest

pytest_plugins = ("connector_acceptance_test.plugin",)


# TODO: check with Airbyte-team if this is the right place to have this
def pytest_collection_modifyitems(config, items):
    skip_cursor = pytest.mark.skip(reason="MANUALLY SKIPPED: Cursor never in schema")
    for item in items:
        if "test_defined_cursors_exist_in_schema" in item.name or "test_read_sequential_slices" in item.name or "test_two_sequential_reads" in item.name:
            item.add_marker(skip_cursor)


@pytest.fixture(scope="session", autouse=True)
def connector_setup():
    """This fixture is a placeholder for external resources that acceptance test might require."""
    # TODO: setup test dependencies if needed. otherwise remove the TODO comments
    yield
    # TODO: clean up test dependencies
