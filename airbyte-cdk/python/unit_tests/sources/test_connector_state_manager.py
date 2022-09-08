#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from contextlib import nullcontext as does_not_raise
from typing import Any, Iterable, List, Mapping, Optional, Union

import pytest
from airbyte_cdk.models import AirbyteStateBlob, AirbyteStateMessage, AirbyteStateType, AirbyteStreamState, StreamDescriptor, SyncMode
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager, HashableStreamDescriptor
from airbyte_cdk.sources.streams import Stream


class StreamWithNamespace(Stream):
    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        return {}

    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return ""

    @property
    def namespace(self) -> Optional[str]:
        return "public"


@pytest.mark.parametrize(
    "input_stream_state, expected_stream_state, expected_shared_state, expected_legacy_state, expected_error",
    (
        pytest.param(
            [
                {
                    "type": AirbyteStateType.STREAM,
                    "stream": {"stream_descriptor": {"name": "actors", "namespace": "public"}, "stream_state": {"id": "mando_michael"}},
                },
                {
                    "type": AirbyteStateType.STREAM,
                    "stream": {"stream_descriptor": {"name": "actresses", "namespace": "public"}, "stream_state": {"id": "seehorn_rhea"}},
                },
            ],
            {
                HashableStreamDescriptor(name="actors", namespace="public"): AirbyteStreamState(
                    stream_descriptor=StreamDescriptor(name="actors", namespace="public"),
                    stream_state=AirbyteStateBlob.parse_obj({"id": "mando_michael"}),
                ),
                HashableStreamDescriptor(name="actresses", namespace="public"): AirbyteStreamState(
                    stream_descriptor=StreamDescriptor(name="actresses", namespace="public"),
                    stream_state=AirbyteStateBlob.parse_obj({"id": "seehorn_rhea"}),
                ),
            },
            None,
            {"actors": {"id": "mando_michael"}, "actresses": {"id": "seehorn_rhea"}},
            does_not_raise(),
            id="test_incoming_per_stream_state",
        ),
        pytest.param(
            [
                {
                    "type": AirbyteStateType.GLOBAL,
                    "global": {
                        "shared_state": {"television": "better_call_saul"},
                        "stream_states": [
                            {
                                "stream_descriptor": StreamDescriptor(name="actors", namespace="public"),
                                "stream_state": AirbyteStateBlob.parse_obj({"id": "mando_michael"}),
                            },
                            {
                                "stream_descriptor": StreamDescriptor(name="actresses", namespace="public"),
                                "stream_state": AirbyteStateBlob.parse_obj({"id": "seehorn_rhea"}),
                            },
                        ],
                    },
                },
            ],
            {
                HashableStreamDescriptor(name="actors", namespace="public"): AirbyteStreamState(
                    stream_descriptor=StreamDescriptor(name="actors", namespace="public"),
                    stream_state=AirbyteStateBlob.parse_obj({"id": "mando_michael"}),
                ),
                HashableStreamDescriptor(name="actresses", namespace="public"): AirbyteStreamState(
                    stream_descriptor=StreamDescriptor(name="actresses", namespace="public"),
                    stream_state=AirbyteStateBlob.parse_obj({"id": "seehorn_rhea"}),
                ),
            },
            AirbyteStateBlob.parse_obj({"television": "better_call_saul"}),
            {"actors": {"id": "mando_michael"}, "actresses": {"id": "seehorn_rhea"}},
            does_not_raise(),
            id="test_incoming_global_state",
        ),
        pytest.param(
            [
                {
                    "type": AirbyteStateType.LEGACY,
                    "data": {"actors": {"id": "fabian_patrick"}, "actresses": {"id": "seehorn_rhea"}, "writers": {"id": "gilligan_vince"}},
                }
            ],
            {
                HashableStreamDescriptor(name="actors", namespace="public"): AirbyteStreamState(
                    stream_descriptor=StreamDescriptor(name="actors"), stream_state=AirbyteStateBlob.parse_obj({"id": "fabian_patrick"})
                ),
                HashableStreamDescriptor(name="actresses"): AirbyteStreamState(
                    stream_descriptor=StreamDescriptor(name="actresses"), stream_state=AirbyteStateBlob.parse_obj({"id": "seehorn_rhea"})
                ),
                HashableStreamDescriptor(name="writers"): AirbyteStreamState(
                    stream_descriptor=StreamDescriptor(name="writers"), stream_state=AirbyteStateBlob.parse_obj({"id": "gilligan_vince"})
                ),
            },
            None,
            {"actors": {"id": "fabian_patrick"}, "actresses": {"id": "seehorn_rhea"}, "writers": {"id": "gilligan_vince"}},
            does_not_raise(),
            id="test_incoming_legacy_state_and_uses_stream_namespace",
        ),
        pytest.param([], {}, None, {}, does_not_raise(), id="test_incoming_empty_stream_state"),
        pytest.param(
            [{"type": AirbyteStateType.STREAM, "stream": {"stream_descriptor": {"name": "actresses", "namespace": "public"}}}],
            {
                HashableStreamDescriptor(name="actresses", namespace="public"): AirbyteStreamState(
                    stream_descriptor=StreamDescriptor(name="actresses", namespace="public")
                )
            },
            None,
            {"actresses": {}},
            does_not_raise(),
            id="test_stream_states_that_have_none_state_blob",
        ),
        pytest.param(
            [
                {
                    "type": AirbyteStateType.GLOBAL,
                    "global": {
                        "stream_states": [
                            {"stream_descriptor": {"name": "actors", "namespace": "public"}, "stream_state": {"id": "mando_michael"}},
                        ],
                    },
                },
            ],
            {
                HashableStreamDescriptor(name="actors", namespace="public"): AirbyteStreamState(
                    stream_descriptor=StreamDescriptor(name="actors", namespace="public"),
                    stream_state=AirbyteStateBlob.parse_obj({"id": "mando_michael"}),
                )
            },
            None,
            {"actors": {"id": "mando_michael"}},
            does_not_raise(),
            id="test_incoming_global_state_without_shared",
        ),
        pytest.param(
            [
                {
                    "type": AirbyteStateType.GLOBAL,
                    "global": {
                        "shared_state": {"television": "better_call_saul"},
                        "stream_states": [
                            {"stream_descriptor": {"name": "actresses", "namespace": "public"}},
                        ],
                    },
                },
            ],
            {
                HashableStreamDescriptor(name="actresses", namespace="public"): AirbyteStreamState(
                    stream_descriptor=StreamDescriptor(name="actresses", namespace="public")
                )
            },
            AirbyteStateBlob.parse_obj({"television": "better_call_saul"}),
            {"actresses": {}},
            does_not_raise(),
            id="test_incoming_global_state_without_stream_state",
        ),
        pytest.param(
            {"actors": {"id": "esposito_giancarlo"}, "actresses": {"id": "seehorn_rhea"}},
            {
                HashableStreamDescriptor(name="actors", namespace="public"): AirbyteStreamState(
                    stream_descriptor=StreamDescriptor(name="actors"), stream_state=AirbyteStateBlob.parse_obj({"id": "esposito_giancarlo"})
                ),
                HashableStreamDescriptor(name="actresses"): AirbyteStreamState(
                    stream_descriptor=StreamDescriptor(name="actresses"), stream_state=AirbyteStateBlob.parse_obj({"id": "seehorn_rhea"})
                ),
            },
            None,
            {"actors": {"id": "esposito_giancarlo"}, "actresses": {"id": "seehorn_rhea"}},
            does_not_raise(),
            id="test_incoming_legacy_json_blob_and_uses_stream_namespace",
        ),
        pytest.param({}, {}, None, {}, does_not_raise(), id="test_legacy_state_empty_object"),
        pytest.param(
            "strings_are_not_allowed", {}, None, {}, pytest.raises(ValueError), id="test_value_error_is_raised_on_invalid_state_input"
        ),
    ),
)
def test_initialize_state_manager(input_stream_state, expected_stream_state, expected_shared_state, expected_legacy_state, expected_error):
    stream_to_instance_map = {"actors": StreamWithNamespace()}

    if isinstance(input_stream_state, List):
        input_stream_state = [AirbyteStateMessage.parse_obj(state_obj) for state_obj in input_stream_state]

    with expected_error:
        state_manager = ConnectorStateManager(stream_to_instance_map, input_stream_state)

        assert state_manager.streams == expected_stream_state
        assert state_manager.shared_state == expected_shared_state
        assert state_manager.legacy == expected_legacy_state


@pytest.mark.parametrize(
    "input_state, stream_name, namespace, expected_state",
    [
        pytest.param(
            [
                {
                    "type": AirbyteStateType.STREAM,
                    "stream": {"stream_descriptor": {"name": "users", "namespace": "public"}, "stream_state": {"created_at": 12345}},
                },
                {
                    "type": AirbyteStateType.STREAM,
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
                    "type": AirbyteStateType.STREAM,
                    "stream": {"stream_descriptor": {"name": "users"}, "stream_state": {"created_at": 12345}},
                },
                {"type": AirbyteStateType.STREAM, "stream": {"stream_descriptor": {"name": "accounts"}, "stream_state": {"id": "abc"}}},
            ],
            "users",
            None,
            {"created_at": 12345},
            id="test_get_stream_without_namespace",
        ),
        pytest.param(
            [
                {"type": AirbyteStateType.STREAM, "stream": {"stream_descriptor": {"name": "users"}}},
                {"type": AirbyteStateType.STREAM, "stream": {"stream_descriptor": {"name": "accounts"}, "stream_state": {"id": "abc"}}},
            ],
            "users",
            None,
            {},
            id="test_get_stream_without_stream_state",
        ),
        pytest.param(
            [{"type": AirbyteStateType.LEGACY, "data": {"users": {"created_at": 12345}, "accounts": {"id": "abc"}}}],
            "users",
            "public",
            {"created_at": 12345},
            id="test_get_stream_from_legacy_state",
        ),
        pytest.param(
            [{"type": AirbyteStateType.GLOBAL, "global": {"shared_state": {"shared": "value"}, "stream_states": []}}],
            "users",
            "public",
            {"shared": "value"},
            id="test_get_shared_only",
        ),
        pytest.param(
            [
                {
                    "type": AirbyteStateType.GLOBAL,
                    "global": {
                        "shared_state": {"shared": "value"},
                        "stream_states": [
                            {
                                "stream_descriptor": {"name": "users", "namespace": "public"},
                                "stream_state": AirbyteStateBlob.parse_obj({"created_at": 12345}),
                            },
                            {
                                "stream_descriptor": {"name": "accounts", "namespace": "public"},
                                "stream_state": AirbyteStateBlob.parse_obj({"id": "abc"}),
                            },
                        ],
                    },
                },
            ],
            "accounts",
            "public",
            {"id": "abc", "shared": "value"},
            id="test_get_stream_with_shared",
        ),
        pytest.param(
            [
                {
                    "type": AirbyteStateType.STREAM,
                    "stream": {"stream_descriptor": {"name": "users", "namespace": "public"}, "stream_state": {"created_at": 12345}},
                },
                {
                    "type": AirbyteStateType.STREAM,
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
                    "type": AirbyteStateType.STREAM,
                    "stream": {"stream_descriptor": {"name": "users", "namespace": "public"}, "stream_state": {"created_at": 12345}},
                },
                {
                    "type": AirbyteStateType.STREAM,
                    "stream": {"stream_descriptor": {"name": "accounts", "namespace": "public"}, "stream_state": {"id": "abc"}},
                },
            ],
            "users",
            "wrong_namespace",
            {},
            id="test_get_stream_wrong_namespace",
        ),
        pytest.param(
            [
                {
                    "type": AirbyteStateType.GLOBAL,
                    "global": {
                        "shared_state": {"shared": "value"},
                        "stream_states": [
                            {
                                "stream_descriptor": {"name": "users", "namespace": "public"},
                                "stream_state": AirbyteStateBlob.parse_obj({"created_at": 12345}),
                            },
                            {
                                "stream_descriptor": {"name": "accounts", "namespace": "public"},
                                "stream_state": AirbyteStateBlob.parse_obj({"id": "abc"}),
                            },
                        ],
                    },
                },
            ],
            "missing",
            "public",
            {"shared": "value"},
            id="test_get_missing_still_includes_shared_stream",
        ),
        pytest.param([], "users", "public", {}, id="test_get_empty_stream_state_defaults_to_empty_dictionary"),
    ],
)
def test_get_stream_state(input_state, stream_name, namespace, expected_state):
    stream_to_instance_map = {"users": StreamWithNamespace()}
    state_messages = [AirbyteStateMessage.parse_obj(state_obj) for state_obj in input_state]
    state_manager = ConnectorStateManager(stream_to_instance_map, state_messages)

    actual_state = state_manager.get_stream_state(stream_name, namespace)

    assert actual_state == expected_state


@pytest.mark.parametrize(
    "input_state, expected_legacy_state, expected_error",
    [
        pytest.param(
            [AirbyteStateMessage(type=AirbyteStateType.LEGACY, data={"actresses": {"id": "seehorn_rhea"}})],
            {"actresses": {"id": "seehorn_rhea"}},
            does_not_raise(),
            id="test_get_legacy_legacy_state_message",
        ),
        pytest.param(
            [
                AirbyteStateMessage(
                    type=AirbyteStateType.STREAM,
                    stream=AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name="actresses", namespace="public"),
                        stream_state=AirbyteStateBlob.parse_obj({"id": "seehorn_rhea"}),
                    ),
                )
            ],
            {"actresses": {"id": "seehorn_rhea"}},
            does_not_raise(),
            id="test_get_legacy_from_stream_state",
        ),
        pytest.param(
            {
                "actors": {"created_at": "1962-10-22"},
                "actresses": {"id": "seehorn_rhea"},
            },
            {"actors": {"created_at": "1962-10-22"}, "actresses": {"id": "seehorn_rhea"}},
            does_not_raise(),
            id="test_get_legacy_from_legacy_state_blob",
        ),
    ],
)
def test_get_legacy_state(input_state, expected_legacy_state, expected_error):
    with expected_error:
        state_manager = ConnectorStateManager({}, input_state)
        actual_legacy_state = state_manager.get_legacy_state()
        assert actual_legacy_state == expected_legacy_state


@pytest.mark.parametrize(
    "start_state, update_name, update_namespace, update_value, expected_legacy_state",
    [
        pytest.param(
            [
                {
                    "type": AirbyteStateType.STREAM,
                    "stream": {"stream_descriptor": {"name": "actors", "namespace": "public"}, "stream_state": {"id": "mckean_michael"}},
                },
                {
                    "type": AirbyteStateType.STREAM,
                    "stream": {"stream_descriptor": {"name": "actresses", "namespace": "public"}, "stream_state": {"id": "seehorn_rhea"}},
                },
            ],
            "actors",
            "public",
            {"id": "fabian_patrick"},
            {"actors": {"id": "fabian_patrick"}, "actresses": {"id": "seehorn_rhea"}},
            id="test_update_existing_stream_state",
        ),
        pytest.param(
            [],
            "actresses",
            None,
            {"id": "seehorn_rhea"},
            {"actresses": {"id": "seehorn_rhea"}},
            id="test_update_first_time_sync_without_namespace",
        ),
        pytest.param(
            [
                {
                    "type": AirbyteStateType.STREAM,
                    "stream": {"stream_descriptor": {"name": "actresses", "namespace": "public"}, "stream_state": {"id": "seehorn_rhea"}},
                }
            ],
            "actors",
            "public",
            {"id": "banks_jonathan"},
            {"actors": {"id": "banks_jonathan"}, "actresses": {"id": "seehorn_rhea"}},
            id="test_update_missing_state",
        ),
    ],
)
def test_update_state_for_stream(start_state, update_name, update_namespace, update_value, expected_legacy_state):
    state_messages = [AirbyteStateMessage.parse_obj(state_obj) for state_obj in start_state]
    state_manager = ConnectorStateManager({}, state_messages)

    state_manager.update_state_for_stream(update_name, update_namespace, update_value)

    assert state_manager.streams[HashableStreamDescriptor(name=update_name, namespace=update_namespace)] == AirbyteStreamState(
        stream_descriptor=StreamDescriptor(name=update_name, namespace=update_namespace), stream_state=update_value
    )

    assert state_manager.get_legacy_state() == expected_legacy_state
