#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from typing import Tuple

import pytest

pytest_plugins = ("source_acceptance_test.plugin",)


def extract_state(record, current_state, stream_mapping, state_cursor_paths) -> Tuple[str, str, str]:
    stream_name = record.record.stream
    record_data = record.record.data
    try:
        state_value = current_state[stream_name][record_data["site_url"]][record_data["search_type"]]["date"]
    except KeyError:
        # In case if state for search type appeared in latest records consider its date as current state.
        state_value = record_data["date"]
    return (
        record_data["date"],
        state_value,
        record.record.stream,
    )


pytest.sat_overrides = {
    "TestIncremental": {
        "extract_state": extract_state,
    }
}


@pytest.fixture(scope="session", autouse=True)
def connector_setup():
    """This fixture is a placeholder for external resources that acceptance test might require."""
    yield
