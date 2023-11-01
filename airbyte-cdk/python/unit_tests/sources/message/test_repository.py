#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import Mock

import pytest
from airbyte_cdk.models import AirbyteControlConnectorConfigMessage, AirbyteControlMessage, AirbyteMessage, Level, OrchestratorType, Type
from airbyte_cdk.sources.message import (
    InMemoryMessageRepository,
    LogAppenderMessageRepositoryDecorator,
    MessageRepository,
    NoopMessageRepository,
)
from pydantic.error_wrappers import ValidationError

A_CONTROL = AirbyteControlMessage(
    type=OrchestratorType.CONNECTOR_CONFIG,
    emitted_at=0,
    connectorConfig=AirbyteControlConnectorConfigMessage(config={"a config": "value"}),
)
ANY_MESSAGE = AirbyteMessage(
    type=Type.CONTROL,
    control=AirbyteControlMessage(
        type=OrchestratorType.CONNECTOR_CONFIG,
        emitted_at=0,
        connectorConfig=AirbyteControlConnectorConfigMessage(config={"any message": "value"}),
    ),
)
ANOTHER_CONTROL = AirbyteControlMessage(
    type=OrchestratorType.CONNECTOR_CONFIG,
    emitted_at=0,
    connectorConfig=AirbyteControlConnectorConfigMessage(config={"another config": "another value"}),
)
UNKNOWN_LEVEL = "potato"


class TestInMemoryMessageRepository:
    def test_given_no_messages_when_consume_queue_then_return_empty(self):
        repo = InMemoryMessageRepository()
        messages = list(repo.consume_queue())
        assert messages == []

    def test_given_messages_when_consume_queue_then_return_messages(self):
        repo = InMemoryMessageRepository()
        first_message = AirbyteMessage(type=Type.CONTROL, control=A_CONTROL)
        repo.emit_message(first_message)
        second_message = AirbyteMessage(type=Type.CONTROL, control=ANOTHER_CONTROL)
        repo.emit_message(second_message)

        messages = repo.consume_queue()

        assert list(messages) == [first_message, second_message]

    def test_given_message_is_consumed_when_consume_queue_then_remove_message_from_queue(self):
        repo = InMemoryMessageRepository()
        first_message = AirbyteMessage(type=Type.CONTROL, control=A_CONTROL)
        repo.emit_message(first_message)
        second_message = AirbyteMessage(type=Type.CONTROL, control=ANOTHER_CONTROL)
        repo.emit_message(second_message)

        message_generator = repo.consume_queue()
        consumed_message = next(message_generator)
        assert consumed_message == first_message

        second_message_generator = repo.consume_queue()
        assert list(second_message_generator) == [second_message]

    def test_given_log_level_is_severe_enough_when_log_message_then_allow_message_to_be_consumed(self):
        repo = InMemoryMessageRepository(Level.DEBUG)
        repo.log_message(Level.INFO, lambda: {"message": "this is a log message"})
        assert list(repo.consume_queue())

    def test_given_log_level_is_severe_enough_when_log_message_then_filter_secrets(self, mocker):
        filtered_message = "a filtered message"
        mocker.patch("airbyte_cdk.sources.message.repository.filter_secrets", return_value=filtered_message)
        repo = InMemoryMessageRepository(Level.DEBUG)

        repo.log_message(Level.INFO, lambda: {"message": "this is a log message"})

        assert list(repo.consume_queue())[0].log.message == filtered_message

    def test_given_log_level_not_severe_enough_when_log_message_then_do_not_allow_message_to_be_consumed(self):
        repo = InMemoryMessageRepository(Level.ERROR)
        repo.log_message(Level.INFO, lambda: {"message": "this is a log message"})
        assert not list(repo.consume_queue())

    def test_given_unknown_log_level_as_threshold_when_log_message_then_allow_message_to_be_consumed(self):
        repo = InMemoryMessageRepository(UNKNOWN_LEVEL)
        repo.log_message(Level.DEBUG, lambda: {"message": "this is a log message"})
        assert list(repo.consume_queue())

    def test_given_unknown_log_level_for_log_when_log_message_then_raise_error(self):
        """
        Pydantic will fail if the log level is unknown but on our side, we should try to log at least
        """
        repo = InMemoryMessageRepository(Level.ERROR)
        with pytest.raises(ValidationError):
            repo.log_message(UNKNOWN_LEVEL, lambda: {"message": "this is a log message"})


class TestNoopMessageRepository:
    def test_given_message_emitted_when_consume_queue_then_return_empty(self):
        repo = NoopMessageRepository()
        repo.emit_message(AirbyteMessage(type=Type.CONTROL, control=A_CONTROL))
        repo.log_message(Level.INFO, lambda: {"message": "this is a log message"})

        assert not list(repo.consume_queue())


class TestLogAppenderMessageRepositoryDecorator:

    _DICT_TO_APPEND = {"airbyte_cdk": {"stream": {"is_substream": False}}}

    @pytest.fixture()
    def decorated(self):
        return Mock(spec=MessageRepository)

    def test_when_emit_message_then_delegate_call(self, decorated):
        repo = LogAppenderMessageRepositoryDecorator(self._DICT_TO_APPEND, decorated, Level.DEBUG)
        repo.emit_message(ANY_MESSAGE)
        decorated.emit_message.assert_called_once_with(ANY_MESSAGE)

    def test_when_log_message_then_append(self, decorated):
        repo = LogAppenderMessageRepositoryDecorator({"a": {"dict_to_append": "appended value"}}, decorated, Level.DEBUG)
        repo.log_message(Level.INFO, lambda: {"a": {"original": "original value"}})
        assert decorated.log_message.call_args_list[0].args[1]() == {
            "a": {"dict_to_append": "appended value", "original": "original value"}
        }

    def test_given_value_clash_when_log_message_then_overwrite_value(self, decorated):
        repo = LogAppenderMessageRepositoryDecorator({"clash": "appended value"}, decorated, Level.DEBUG)
        repo.log_message(Level.INFO, lambda: {"clash": "original value"})
        assert decorated.log_message.call_args_list[0].args[1]() == {"clash": "appended value"}

    def test_given_log_level_is_severe_enough_when_log_message_then_allow_message_to_be_consumed(self, decorated):
        repo = LogAppenderMessageRepositoryDecorator(self._DICT_TO_APPEND, decorated, Level.DEBUG)
        repo.log_message(Level.INFO, lambda: {})
        assert decorated.log_message.call_count == 1

    def test_given_log_level_not_severe_enough_when_log_message_then_do_not_allow_message_to_be_consumed(self, decorated):
        repo = LogAppenderMessageRepositoryDecorator(self._DICT_TO_APPEND, decorated, Level.ERROR)
        repo.log_message(Level.INFO, lambda: {})
        assert decorated.log_message.call_count == 0

    def test_when_consume_queue_then_return_delegate_queue(self, decorated):
        repo = LogAppenderMessageRepositoryDecorator(self._DICT_TO_APPEND, decorated, Level.DEBUG)
        queue = [ANY_MESSAGE, ANY_MESSAGE, ANY_MESSAGE]
        decorated.consume_queue.return_value = iter(queue)

        result = list(repo.consume_queue())

        assert result == queue
