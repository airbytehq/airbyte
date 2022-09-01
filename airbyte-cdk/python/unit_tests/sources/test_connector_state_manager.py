#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.models import AirbyteStateMessage, AirbyteStateType
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager


@pytest.mark.parametrize(
    "test_name, input_state, expected_legacy_state",
    [
        (
            "test_legacy_input_state",
            [AirbyteStateMessage(type=AirbyteStateType.LEGACY, data={"actresses": {"id": "seehorn_rhea"}})],
            {"actresses": {"id": "seehorn_rhea"}},
        ),
        (
            "test_supports_legacy_json_blob",
            {
                "actors": {"created_at": "1962-10-22"},
                "actresses": {"id": "seehorn_rhea"},
            },
            {"actors": {"created_at": "1962-10-22"}, "actresses": {"id": "seehorn_rhea"}},
        ),
        ("test_initialize_empty_mapping_by_default", {}, {}),
        ("test_initialize_empty_state", [], {}),
    ],
)
def test_get_legacy_state(test_name, input_state, expected_legacy_state):
    state_manager = ConnectorStateManager(input_state)

    actual_legacy_state = state_manager.get_legacy_state()
    assert actual_legacy_state == expected_legacy_state
