#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from contextlib import nullcontext as does_not_raise
from typing import List

import pytest
from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteStateBlob,
    AirbyteStateMessage,
    AirbyteStateMessageSerializer,
    AirbyteStateType,
    AirbyteStreamState,
    StreamDescriptor,
)
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager, HashableStreamDescriptor


@pytest.mark.parametrize(
    "input_stream_state, expected_stream_state, expected_error",
    (
        pytest.param(
            [
                {
                    "type": "STREAM",
                    "stream": {"stream_descriptor": {"name": "actors", "namespace": "public"}, "stream_state": {"id": "mando_michael"}},
                },
                {
                    "type": "STREAM",
                    "stream": {"stream_descriptor": {"name": "actresses", "namespace": "public"}, "stream_state": {"id": "seehorn_rhea"}},
                },
            ],
            {
                HashableStreamDescriptor(name="actors", namespace="public"): AirbyteStateBlob({"id": "mando_michael"}),
                HashableStreamDescriptor(name="actresses", namespace="public"): AirbyteStateBlob({"id": "seehorn_rhea"}),
            },
            does_not_raise(),
            id="test_incoming_per_stream_state",
        ),
        pytest.param([], {}, does_not_raise(), id="test_incoming_empty_stream_state"),
        pytest.param(
            [{"type": "STREAM", "stream": {"stream_descriptor": {"name": "actresses", "namespace": "public"}}}],
            {HashableStreamDescriptor(name="actresses", namespace="public"): None},
            does_not_raise(),
            id="test_stream_states_that_have_none_state_blob",
        ),
        pytest.param(
            [
                {
                    "type": "GLOBAL",
                    "global": {
                        "shared_state": {"television": "better_call_saul"},
                        "stream_states": [
                            {
                                "stream_descriptor": {"name": "actors", "namespace": "public"},
                                "stream_state": {"id": "mando_michael"},
                            },
                            {
                                "stream_descriptor": {"name": "actresses", "namespace": "public"},
                                "stream_state": {"id": "seehorn_rhea"},
                            },
                        ],
                    },
                },
            ],
            {
                HashableStreamDescriptor(name="actors", namespace="public"): AirbyteStateBlob({"id": "mando_michael"}),
                HashableStreamDescriptor(name="actresses", namespace="public"): AirbyteStateBlob({"id": "seehorn_rhea"}),
            },
            pytest.raises(ValueError),
            id="test_incoming_global_state_with_shared_state_throws_error",
        ),
        pytest.param(
            [
                {
                    "type": "GLOBAL",
                    "global": {
                        "stream_states": [
                            {"stream_descriptor": {"name": "actors", "namespace": "public"}, "stream_state": {"id": "mando_michael"}},
                        ],
                    },
                },
            ],
            {
                HashableStreamDescriptor(name="actors", namespace="public"): AirbyteStateBlob({"id": "mando_michael"}),
            },
            does_not_raise(),
            id="test_incoming_global_state_without_shared",
        ),
        pytest.param(
            [
                {
                    "type": "GLOBAL",
                    "global": {
                        "shared_state": None,
                        "stream_states": [
                            {
                                "stream_descriptor": {"name": "actors", "namespace": "public"},
                                "stream_state": {"id": "mando_michael"},
                            },
                        ],
                    },
                },
            ],
            {
                HashableStreamDescriptor(name="actors", namespace="public"): AirbyteStateBlob({"id": "mando_michael"}),
            },
            does_not_raise(),
            id="test_incoming_global_state_with_none_shared",
        ),
        pytest.param(
            [
                {
                    "type": "GLOBAL",
                    "global": {
                        "stream_states": [
                            {"stream_descriptor": {"name": "actresses", "namespace": "public"}},
                        ],
                    },
                },
            ],
            {HashableStreamDescriptor(name="actresses", namespace="public"): None},
            does_not_raise(),
            id="test_incoming_global_state_without_stream_state",
        ),
    ),
)
def test_initialize_state_manager(input_stream_state, expected_stream_state, expected_error):
    if isinstance(input_stream_state, List):
        input_stream_state = [AirbyteStateMessageSerializer.load(state_obj) for state_obj in list(input_stream_state)]

    with expected_error:
        state_manager = ConnectorStateManager(input_stream_state)

        assert state_manager.per_stream_states == expected_stream_state


@pytest.mark.parametrize(
    "input_state, stream_name, namespace, expected_state",
    [
        pytest.param(
            [
                {
                    "type": "STREAM",
                    "stream": {"stream_descriptor": {"name": "users", "namespace": "public"}, "stream_state": {"created_at": 12345}},
                },
                {
                    "type": "STREAM",
                    "stream": {"stream_descriptor": {"name": "accounts", "namespace": "public"}, "stream_state": {"id": "abc"}},
                },
            ],
            "users",
            "public",
            {"created_at": 12345},
            id="test_get_stream_only",
        ),
        pytest.param(
            [
                {
                    "type": "STREAM",
                    "stream": {"stream_descriptor": {"name": "users"}, "stream_state": {"created_at": 12345}},
                },
                {"type": "STREAM", "stream": {"stream_descriptor": {"name": "accounts"}, "stream_state": {"id": "abc"}}},
            ],
            "users",
            None,
            {"created_at": 12345},
            id="test_get_stream_without_namespace",
        ),
        pytest.param(
            [
                {"type": "STREAM", "stream": {"stream_descriptor": {"name": "users"}}},
                {"type": "STREAM", "stream": {"stream_descriptor": {"name": "accounts"}, "stream_state": {"id": "abc"}}},
            ],
            "users",
            None,
            {},
            id="test_get_stream_without_stream_state",
        ),
        pytest.param(
            [
                {
                    "type": "STREAM",
                    "stream": {"stream_descriptor": {"name": "users", "namespace": "public"}, "stream_state": {"created_at": 12345}},
                },
                {
                    "type": "STREAM",
                    "stream": {"stream_descriptor": {"name": "accounts", "namespace": "public"}, "stream_state": {"id": "abc"}},
                },
            ],
            "missing",
            "public",
            {},
            id="test_get_missing_stream",
        ),
        pytest.param(
            [
                {
                    "type": "STREAM",
                    "stream": {"stream_descriptor": {"name": "users", "namespace": "public"}, "stream_state": {"created_at": 12345}},
                },
                {
                    "type": "STREAM",
                    "stream": {"stream_descriptor": {"name": "accounts", "namespace": "public"}, "stream_state": {"id": "abc"}},
                },
            ],
            "users",
            "wrong_namespace",
            {},
            id="test_get_stream_wrong_namespace",
        ),
        pytest.param([], "users", "public", {}, id="test_get_empty_stream_state_defaults_to_empty_dictionary"),
        pytest.param(
            [
                {
                    "type": "STREAM",
                    "stream": {"stream_descriptor": {"name": "users", "namespace": "public"}, "stream_state": None},
                },
            ],
            "users",
            "public",
            {},
            id="test_get_stream_with_stream_state_none_returns_empty_map",
        ),
    ],
)
def test_get_stream_state(input_state, stream_name, namespace, expected_state):
    state_messages = [AirbyteStateMessageSerializer.load(state_obj) for state_obj in list(input_state)]
    state_manager = ConnectorStateManager(state_messages)

    actual_state = state_manager.get_stream_state(stream_name, namespace)

    assert actual_state == expected_state


def test_get_state_returns_deep_copy():
    input_state = [
        AirbyteStateMessage(
            type=AirbyteStateType.STREAM,
            stream=AirbyteStreamState(
                stream_descriptor=StreamDescriptor(name="episodes", namespace="public"),
                stream_state=AirbyteStateBlob({"id": [109]}),
            ),
        )
    ]
    state_manager = ConnectorStateManager(input_state)

    per_stream_state = state_manager.get_stream_state("episodes", "public")
    per_stream_state["id"].append(309)

    assert state_manager.get_stream_state("episodes", "public") == {"id": [109]}


@pytest.mark.parametrize(
    "start_state, update_name, update_namespace, update_value",
    [
        pytest.param(
            [
                {
                    "type": "STREAM",
                    "stream": {"stream_descriptor": {"name": "actors", "namespace": "public"}, "stream_state": {"id": "mckean_michael"}},
                },
                {
                    "type": "STREAM",
                    "stream": {"stream_descriptor": {"name": "actresses", "namespace": "public"}, "stream_state": {"id": "seehorn_rhea"}},
                },
            ],
            "actors",
            "public",
            {"id": "fabian_patrick"},
            id="test_update_existing_stream_state",
        ),
        pytest.param(
            [],
            "actresses",
            None,
            {"id": "seehorn_rhea"},
            id="test_update_first_time_sync_without_namespace",
        ),
        pytest.param(
            [
                {
                    "type": "STREAM",
                    "stream": {"stream_descriptor": {"name": "actresses", "namespace": "public"}, "stream_state": {"id": "seehorn_rhea"}},
                }
            ],
            "actors",
            "public",
            {"id": "banks_jonathan"},
            id="test_update_missing_state",
        ),
        pytest.param(
            [
                {
                    "type": "STREAM",
                    "stream": {"stream_descriptor": {"name": "actresses", "namespace": "public"}, "stream_state": {"id": "seehorn_rhea"}},
                }
            ],
            "actors",
            "public",
            {"id": "banks_jonathan"},
            id="test_ignore_when_per_stream_state_value_is_none",
        ),
    ],
)
def test_update_state_for_stream(start_state, update_name, update_namespace, update_value):
    state_messages = [AirbyteStateMessage(state_obj) for state_obj in list(start_state)]
    state_manager = ConnectorStateManager(state_messages)

    state_manager.update_state_for_stream(update_name, update_namespace, update_value)

    assert state_manager.per_stream_states[HashableStreamDescriptor(name=update_name, namespace=update_namespace)] == AirbyteStateBlob(
        update_value
    )


@pytest.mark.parametrize(
    "start_state, update_name, update_namespace, expected_state_message",
    [
        pytest.param(
            [
                AirbyteStateMessage(
                    type=AirbyteStateType.STREAM,
                    stream=AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name="episodes", namespace="public"),
                        stream_state=AirbyteStateBlob({"created_at": "2022_05_22"}),
                    ),
                ),
                AirbyteStateMessage(
                    type=AirbyteStateType.STREAM,
                    stream=AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name="seasons", namespace="public"),
                        stream_state=AirbyteStateBlob({"id": 1}),
                    ),
                ),
            ],
            "episodes",
            "public",
            AirbyteMessage(
                type=MessageType.STATE,
                state=AirbyteStateMessage(
                    type=AirbyteStateType.STREAM,
                    stream=AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name="episodes", namespace="public"),
                        stream_state=AirbyteStateBlob({"created_at": "2022_05_22"}),
                    ),
                ),
            ),
            id="test_emit_state_message",
        ),
        pytest.param(
            [
                AirbyteStateMessage(
                    type=AirbyteStateType.STREAM,
                    stream=AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name="episodes", namespace="public"),
                        stream_state=None,
                    ),
                ),
            ],
            "episodes",
            "public",
            AirbyteMessage(
                type=MessageType.STATE,
                state=AirbyteStateMessage(
                    type=AirbyteStateType.STREAM,
                    stream=AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name="episodes", namespace="public"),
                        stream_state=AirbyteStateBlob(),
                    ),
                ),
            ),
            id="test_always_emit_message_with_stream_state_blob",
        ),
        pytest.param(
            [
                AirbyteStateMessage(
                    type=AirbyteStateType.STREAM,
                    stream=AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name="episodes", namespace="public"),
                        stream_state=AirbyteStateBlob({"id": 507}),
                    ),
                )
            ],
            "missing",
            "public",
            AirbyteMessage(
                type=MessageType.STATE,
                state=AirbyteStateMessage(
                    type=AirbyteStateType.STREAM,
                    stream=AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name="missing", namespace="public"), stream_state=AirbyteStateBlob()
                    ),
                ),
            ),
            id="test_emit_state_nonexistent_stream_name",
        ),
        pytest.param(
            [
                AirbyteStateMessage(
                    type=AirbyteStateType.STREAM,
                    stream=AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name="episodes", namespace="public"),
                        stream_state=AirbyteStateBlob({"id": 507}),
                    ),
                )
            ],
            "episodes",
            "nonexistent",
            AirbyteMessage(
                type=MessageType.STATE,
                state=AirbyteStateMessage(
                    type=AirbyteStateType.STREAM,
                    stream=AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name="episodes", namespace="nonexistent"), stream_state=AirbyteStateBlob()
                    ),
                ),
            ),
            id="test_emit_state_wrong_namespace",
        ),
    ],
)
def test_create_state_message(start_state, update_name, update_namespace, expected_state_message):
    state_manager = ConnectorStateManager(start_state)

    actual_state_message = state_manager.create_state_message(stream_name=update_name, namespace=update_namespace)
    assert actual_state_message == expected_state_message
