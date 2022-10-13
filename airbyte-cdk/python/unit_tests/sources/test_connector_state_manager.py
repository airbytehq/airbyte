#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from contextlib import nullcontext as does_not_raise

import pytest
from airbyte_cdk.models import AirbyteStateMessage, AirbyteStateType
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager


@pytest.mark.parametrize(
    "input_state, expected_legacy_state, expected_error",
    [
        pytest.param(
            [AirbyteStateMessage(type=AirbyteStateType.LEGACY, data={"actresses": {"id": "seehorn_rhea"}})],
            {"actresses": {"id": "seehorn_rhea"}},
            does_not_raise(),
            id="test_legacy_input_state",
        ),
        pytest.param(
            {
                "actors": {"created_at": "1962-10-22"},
                "actresses": {"id": "seehorn_rhea"},
            },
            {"actors": {"created_at": "1962-10-22"}, "actresses": {"id": "seehorn_rhea"}},
            does_not_raise(),
            id="test_supports_legacy_json_blob",
        ),
        pytest.param({}, {}, does_not_raise(), id="test_initialize_empty_mapping_by_default"),
        pytest.param([], {}, does_not_raise(), id="test_initialize_empty_state"),
        pytest.param("strings_are_not_allowed", None, pytest.raises(ValueError), id="test_value_error_is_raised_on_invalid_state_input"),
    ],
)
def test_get_legacy_state(input_state, expected_legacy_state, expected_error):
    with expected_error:
        state_manager = ConnectorStateManager(input_state)
        actual_legacy_state = state_manager.get_legacy_state()
        assert actual_legacy_state == expected_legacy_state
