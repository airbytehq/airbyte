#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import unittest
from unittest.mock import Mock

from airbyte_cdk.models import AirbyteStream, SyncMode
from airbyte_cdk.sources.message import InMemoryMessageRepository
from airbyte_cdk.sources.streams.concurrent.availability_strategy import STREAM_AVAILABLE
from airbyte_cdk.sources.streams.concurrent.cursor import Cursor, FinalStateCursor
from airbyte_cdk.sources.streams.concurrent.default_stream import DefaultStream


class ThreadBasedConcurrentStreamTest(unittest.TestCase):
    def setUp(self):
        self._partition_generator = Mock()
        self._name = "name"
        self._json_schema = {}
        self._availability_strategy = Mock()
        self._primary_key = []
        self._cursor_field = None
        self._logger = Mock()
        self._cursor = Mock(spec=Cursor)
        self._message_repository = InMemoryMessageRepository()
        self._stream = DefaultStream(
            self._partition_generator,
            self._name,
            self._json_schema,
            self._availability_strategy,
            self._primary_key,
            self._cursor_field,
            self._logger,
            FinalStateCursor(stream_name=self._name, stream_namespace=None, message_repository=self._message_repository),
        )

    def test_get_json_schema(self):
        json_schema = self._stream.get_json_schema()
        assert json_schema == self._json_schema

    def test_check_availability(self):
        self._availability_strategy.check_availability.return_value = STREAM_AVAILABLE
        availability = self._stream.check_availability()
        assert availability == STREAM_AVAILABLE
        self._availability_strategy.check_availability.assert_called_once_with(self._logger)

    def test_check_for_error_raises_an_exception_if_any_of_the_futures_are_not_done(self):
        futures = [Mock() for _ in range(3)]
        for f in futures:
            f.exception.return_value = None
        futures[0].done.return_value = False

        with self.assertRaises(Exception):
            self._stream._check_for_errors(futures)

    def test_check_for_error_raises_an_exception_if_any_of_the_futures_raised_an_exception(self):
        futures = [Mock() for _ in range(3)]
        for f in futures:
            f.exception.return_value = None
        futures[0].exception.return_value = Exception("error")

        with self.assertRaises(Exception):
            self._stream._check_for_errors(futures)

    def test_as_airbyte_stream(self):
        expected_airbyte_stream = AirbyteStream(
            name=self._name,
            json_schema=self._json_schema,
            supported_sync_modes=[SyncMode.full_refresh],
            source_defined_cursor=None,
            default_cursor_field=None,
            source_defined_primary_key=None,
            namespace=None,
        )
        actual_airbyte_stream = self._stream.as_airbyte_stream()

        assert actual_airbyte_stream == expected_airbyte_stream

    def test_as_airbyte_stream_with_primary_key(self):
        json_schema = {
            "type": "object",
            "properties": {
                "id_a": {"type": ["null", "string"]},
                "id_b": {"type": ["null", "string"]},
            },
        }
        stream = DefaultStream(
            self._partition_generator,
            self._name,
            json_schema,
            self._availability_strategy,
            ["id"],
            self._cursor_field,
            self._logger,
            FinalStateCursor(stream_name=self._name, stream_namespace=None, message_repository=self._message_repository),
        )

        expected_airbyte_stream = AirbyteStream(
            name=self._name,
            json_schema=json_schema,
            supported_sync_modes=[SyncMode.full_refresh],
            source_defined_cursor=None,
            default_cursor_field=None,
            source_defined_primary_key=[["id"]],
            namespace=None,
        )

        airbyte_stream = stream.as_airbyte_stream()
        assert airbyte_stream == expected_airbyte_stream

    def test_as_airbyte_stream_with_composite_primary_key(self):
        json_schema = {
            "type": "object",
            "properties": {
                "id_a": {"type": ["null", "string"]},
                "id_b": {"type": ["null", "string"]},
            },
        }
        stream = DefaultStream(
            self._partition_generator,
            self._name,
            json_schema,
            self._availability_strategy,
            ["id_a", "id_b"],
            self._cursor_field,
            self._logger,
            FinalStateCursor(stream_name=self._name, stream_namespace=None, message_repository=self._message_repository),
        )

        expected_airbyte_stream = AirbyteStream(
            name=self._name,
            json_schema=json_schema,
            supported_sync_modes=[SyncMode.full_refresh],
            source_defined_cursor=None,
            default_cursor_field=None,
            source_defined_primary_key=[["id_a", "id_b"]],
            namespace=None,
        )

        airbyte_stream = stream.as_airbyte_stream()
        assert airbyte_stream == expected_airbyte_stream

    def test_as_airbyte_stream_with_a_cursor(self):
        json_schema = {
            "type": "object",
            "properties": {
                "id": {"type": ["null", "string"]},
                "date": {"type": ["null", "string"]},
            },
        }
        stream = DefaultStream(
            self._partition_generator,
            self._name,
            json_schema,
            self._availability_strategy,
            self._primary_key,
            "date",
            self._logger,
            FinalStateCursor(stream_name=self._name, stream_namespace=None, message_repository=self._message_repository),
        )

        expected_airbyte_stream = AirbyteStream(
            name=self._name,
            json_schema=json_schema,
            supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
            source_defined_cursor=True,
            default_cursor_field=["date"],
            source_defined_primary_key=None,
            namespace=None,
        )

        airbyte_stream = stream.as_airbyte_stream()
        assert airbyte_stream == expected_airbyte_stream

    def test_as_airbyte_stream_with_namespace(self):
        stream = DefaultStream(
            self._partition_generator,
            self._name,
            self._json_schema,
            self._availability_strategy,
            self._primary_key,
            self._cursor_field,
            self._logger,
            FinalStateCursor(stream_name=self._name, stream_namespace=None, message_repository=self._message_repository),
            namespace="test",
        )
        expected_airbyte_stream = AirbyteStream(
            name=self._name,
            json_schema=self._json_schema,
            supported_sync_modes=[SyncMode.full_refresh],
            source_defined_cursor=None,
            default_cursor_field=None,
            source_defined_primary_key=None,
            namespace="test",
        )
        actual_airbyte_stream = stream.as_airbyte_stream()

        assert actual_airbyte_stream == expected_airbyte_stream
