#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import Mock, call

from airbyte_cdk.sources.declarative.incremental.declarative_cursor import DeclarativeCursor
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.pagination_strategy import PaginationStrategy
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.stop_condition import (
    CursorStopCondition,
    PaginationStopCondition,
    StopConditionPaginationStrategyDecorator,
)
from airbyte_cdk.sources.types import Record
from pytest import fixture

ANY_RECORD = Mock()
NO_RECORD = None
ANY_RESPONSE = Mock()


@fixture
def mocked_cursor():
    return Mock(spec=DeclarativeCursor)


@fixture
def mocked_pagination_strategy():
    return Mock(spec=PaginationStrategy)


@fixture
def mocked_stop_condition():
    return Mock(spec=PaginationStopCondition)


def test_given_record_should_be_synced_when_is_met_return_false(mocked_cursor):
    mocked_cursor.should_be_synced.return_value = True
    assert not CursorStopCondition(mocked_cursor).is_met(ANY_RECORD)


def test_given_record_should_not_be_synced_when_is_met_return_true(mocked_cursor):
    mocked_cursor.should_be_synced.return_value = False
    assert CursorStopCondition(mocked_cursor).is_met(ANY_RECORD)


def test_given_stop_condition_is_met_when_next_page_token_then_return_none(mocked_pagination_strategy, mocked_stop_condition):
    mocked_stop_condition.is_met.return_value = True
    last_record = Mock(spec=Record)

    decorator = StopConditionPaginationStrategyDecorator(mocked_pagination_strategy, mocked_stop_condition)

    assert not decorator.next_page_token(ANY_RESPONSE, 2, last_record)
    mocked_stop_condition.is_met.assert_has_calls([call(last_record)])


def test_given_last_record_meets_condition_when_next_page_token_then_do_not_check_for_other_records(
    mocked_pagination_strategy, mocked_stop_condition
):
    mocked_stop_condition.is_met.return_value = True
    last_record = Mock(spec=Record)

    StopConditionPaginationStrategyDecorator(mocked_pagination_strategy, mocked_stop_condition).next_page_token(
        ANY_RESPONSE, 2, last_record
    )

    mocked_stop_condition.is_met.assert_called_once_with(last_record)


def test_given_stop_condition_is_not_met_when_next_page_token_then_delegate(mocked_pagination_strategy, mocked_stop_condition):
    mocked_stop_condition.is_met.return_value = False
    last_record = Mock(spec=Record)
    decorator = StopConditionPaginationStrategyDecorator(mocked_pagination_strategy, mocked_stop_condition)

    next_page_token = decorator.next_page_token(ANY_RESPONSE, 2, last_record)

    assert next_page_token == mocked_pagination_strategy.next_page_token.return_value
    mocked_pagination_strategy.next_page_token.assert_called_once_with(ANY_RESPONSE, 2, last_record)
    mocked_stop_condition.is_met.assert_has_calls([call(last_record)])


def test_given_no_records_when_next_page_token_then_delegate(mocked_pagination_strategy, mocked_stop_condition):
    decorator = StopConditionPaginationStrategyDecorator(mocked_pagination_strategy, mocked_stop_condition)

    next_page_token = decorator.next_page_token(ANY_RESPONSE, 0, NO_RECORD)

    assert next_page_token == mocked_pagination_strategy.next_page_token.return_value
    mocked_pagination_strategy.next_page_token.assert_called_once_with(ANY_RESPONSE, 0, NO_RECORD)


def test_when_reset_then_delegate(mocked_pagination_strategy, mocked_stop_condition):
    decorator = StopConditionPaginationStrategyDecorator(mocked_pagination_strategy, mocked_stop_condition)
    decorator.reset()
    mocked_pagination_strategy.reset.assert_called_once_with()


def test_when_get_page_size_then_delegate(mocked_pagination_strategy, mocked_stop_condition):
    decorator = StopConditionPaginationStrategyDecorator(mocked_pagination_strategy, mocked_stop_condition)

    page_size = decorator.get_page_size()

    assert page_size == mocked_pagination_strategy.get_page_size.return_value
    mocked_pagination_strategy.get_page_size.assert_called_once_with()
