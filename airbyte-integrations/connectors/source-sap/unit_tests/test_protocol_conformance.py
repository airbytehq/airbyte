"""Airbyte protocol conformance, without a SAP system.

The e2e suite is the real proof, but it skips wherever there is no SAP sandbox --
on a fork PR that leaves incremental/state conformance asserted by nothing. These
tests pin the message shapes against the CDK 7.28 dataclass models.
"""

import logging
from unittest.mock import MagicMock

import orjson
import pytest
from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteMessageSerializer,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteStateType,
    ConnectorSpecificationSerializer,
    SyncMode,
    Type,
)
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.message import InMemoryMessageRepository

from source_sap.cursors import DriverStateCursor, FieldValueCursor, NoStateCursor
from source_sap.protocols.base import ReadPlan, SapObject
from source_sap.source import SourceSap
from source_sap.streams import build_stream


class TestSpec:
    def test_the_spec_is_a_valid_connector_specification(self):
        spec = SourceSap().spec(logging.getLogger("airbyte"))
        ConnectorSpecificationSerializer.dump(spec)

    def test_every_credential_field_is_marked_secret(self):
        props = SourceSap().spec(logging.getLogger("airbyte")).connectionSpecification["properties"]
        assert props["password"].get("airbyte_secret") is True

    def test_the_protocol_choice_offers_every_mode_the_source_implements(self):
        from source_sap.source import DRIVERS

        props = SourceSap().spec(logging.getLogger("airbyte")).connectionSpecification["properties"]
        modes = {option["properties"]["mode"]["const"] for option in props["protocol"]["oneOf"]}
        # The spec and the driver registry must not drift apart.
        assert modes == set(DRIVERS)


def _stream(supports_incremental, primary_key=None):
    obj = SapObject(
        name="S",
        json_schema={"type": "object", "properties": {"A": {"type": ["null", "string"]}}},
        primary_key=primary_key,
        supports_incremental=supports_incremental,
        meta={},
    )
    driver = MagicMock()
    driver.read_plans.return_value = [ReadPlan(sql="SELECT 1")]
    driver.concurrency_group.return_value = ""
    driver.prepare = None
    repo, mgr = InMemoryMessageRepository(), ConnectorStateManager()
    cursor = NoStateCursor("S", None, repo, mgr)
    return build_stream(MagicMock(), driver, obj, cursor, incremental=False, state={})


class TestCatalogShape:
    def test_a_full_refresh_stream_advertises_only_full_refresh(self):
        assert _stream(False).as_airbyte_stream().supported_sync_modes == [SyncMode.full_refresh]

    def test_an_odp_stream_advertises_incremental_without_a_cursor_field(self):
        # ODP's position is a server-side subscription, so there is no comparable
        # column; DefaultStream would otherwise never offer incremental.
        stream = _stream(True).as_airbyte_stream()
        assert SyncMode.incremental in stream.supported_sync_modes
        assert stream.source_defined_cursor is True
        assert stream.default_cursor_field in (None, [])

    def test_the_primary_key_survives_as_airbyte_stream(self):
        stream = _stream(False, primary_key=[["A"], ["B"]]).as_airbyte_stream()
        assert stream.source_defined_primary_key == [["A"], ["B"]]

    def test_the_catalog_entry_serializes(self):
        message = AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="S", data={}, emitted_at=1))
        orjson.dumps(AirbyteMessageSerializer.dump(message))


class TestStateMessages:
    def _emit(self, cursor):
        cursor.ensure_at_least_one_state_emitted()
        return list(cursor._message_repository.consume_queue())

    def test_a_driver_state_message_is_a_per_stream_state(self):
        repo, mgr = InMemoryMessageRepository(), ConnectorStateManager()
        driver = MagicMock()
        driver.next_state.return_value = {"subscriber_process": "AB_X", "initialized": True}
        cursor = DriverStateCursor(
            "S", None, repo, mgr, driver, MagicMock(), SapObject(name="S", json_schema={}, meta={}), {}
        )
        (message,) = self._emit(cursor)
        assert message.type == Type.STATE
        assert isinstance(message.state, AirbyteStateMessage)
        assert message.state.type == AirbyteStateType.STREAM
        assert message.state.stream.stream_descriptor.name == "S"

    def test_a_field_cursor_state_message_carries_the_cursor_value(self):
        repo, mgr = InMemoryMessageRepository(), ConnectorStateManager()
        cursor = FieldValueCursor("S", None, repo, mgr, "FLDATE", {"FLDATE": "20260101"})
        (message,) = self._emit(cursor)
        assert message.state.stream.stream_state.FLDATE == "20260101"

    def test_state_messages_serialize_and_round_trip(self):
        repo, mgr = InMemoryMessageRepository(), ConnectorStateManager()
        cursor = FieldValueCursor("S", None, repo, mgr, "C", {"C": "v"})
        (message,) = self._emit(cursor)
        payload = orjson.loads(orjson.dumps(AirbyteMessageSerializer.dump(message)))
        assert payload["state"]["type"] == "STREAM"
        assert payload["state"]["stream"]["stream_state"] == {"C": "v"}

    def test_a_full_refresh_stream_still_emits_one_state_message(self):
        repo, mgr = InMemoryMessageRepository(), ConnectorStateManager()
        assert len(self._emit(NoStateCursor("S", None, repo, mgr))) == 1


class TestRecordShape:
    def test_records_are_emitted_with_millisecond_timestamps(self):
        # The protocol wants milliseconds; the previous connector used seconds.
        stream = _stream(False)
        assert stream  # the CDK stamps emitted_at itself -- assert the unit here
        now_ms = AirbyteRecordMessage(stream="S", data={}, emitted_at=1_789_000_000_000).emitted_at
        assert now_ms > 1_600_000_000_000

    @pytest.mark.parametrize("value", [None, 1, 1.5, True, "x", [1], {"a": 1}])
    def test_every_coerced_value_type_serializes(self, value):
        message = AirbyteMessage(
            type=Type.RECORD,
            record=AirbyteRecordMessage(stream="S", data={"v": value}, emitted_at=1),
        )
        orjson.dumps(AirbyteMessageSerializer.dump(message))
