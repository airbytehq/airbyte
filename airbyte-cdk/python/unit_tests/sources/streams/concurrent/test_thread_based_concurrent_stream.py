#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import unittest
from unittest.mock import Mock

from airbyte_cdk.sources.streams.concurrent.availability_strategy import STREAM_AVAILABLE
from airbyte_cdk.sources.streams.concurrent.thread_based_concurrent_stream import ThreadBasedConcurrentStream


class ThreadBasedConcurrentStreamTest(unittest.TestCase):
    def setUp(self):
        self._partition_generator = Mock()
        self._max_workers = 1
        self._name = "name"
        self._json_schema = {}
        self._availability_strategy = Mock()
        self._primary_key = None
        self._cursor_field = None
        self._error_display_message_parser = Mock()
        self._slice_logger = Mock()
        self._message_repository = Mock()
        self._stream = ThreadBasedConcurrentStream(
            self._partition_generator,
            self._max_workers,
            self._name,
            self._json_schema,
            self._availability_strategy,
            self._primary_key,
            self._cursor_field,
            self._error_display_message_parser,
            self._slice_logger,
            self._message_repository,
        )

    def test_get_error_display_message_delegates_to_error_message_parser(self):
        self._error_display_message_parser.get_error_display_message.return_value = "error message"
        exception = Mock()
        error_message = self._stream.get_error_display_message(exception)

        assert error_message == "error message"
        self._error_display_message_parser.get_error_display_message.assert_called_once_with(exception)

    def test_get_json_schema(self):
        json_schema = self._stream.get_json_schema()
        assert json_schema == self._json_schema

    def test_check_availability(self):
        self._availability_strategy.check_availability.return_value = STREAM_AVAILABLE
        availability = self._stream.check_availability()
        assert availability == STREAM_AVAILABLE
        self._availability_strategy.check_availability.assert_called_once_with(self._stream.logger)

    def test_check_for_error_raises_no_exception_if_all_futures_succeeded(self):
        futures = [Mock() for _ in range(3)]
        for f in futures:
            f.exception.return_value = None

        self._stream._check_for_errors(futures)

    def test_check_for_error_raises_an_exception_if_any_of_the_futures_raised_an_exception(self):
        futures = [Mock() for _ in range(3)]
        for f in futures:
            f.exception.return_value = None
        futures[0].exception.return_value = Exception("error")

        with self.assertRaises(Exception):
            self._stream._check_for_errors(futures)

    def test_check_for_error_raises_an_exception_if_any_of_the_futures_are_not_done(self):
        futures = [Mock() for _ in range(3)]
        for f in futures:
            f.exception.return_value = None
        futures[0].done.return_value = False

        with self.assertRaises(Exception):
            self._stream._check_for_errors(futures)
