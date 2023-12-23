#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import Mock

import pytest
from airbyte_cdk.sources.declarative.decoders import JsonDecoder
from airbyte_cdk.sources.declarative.incremental import Cursor
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.pagination_strategy import PaginationStrategy
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.stop_condition import (
    CursorStopCondition,
    InterpolatedStopCondition,
    PaginationStopCondition,
    StopConditionPaginationStrategyDecorator,
)
from airbyte_cdk.sources.declarative.types import Record
from pytest import fixture
from requests.models import Response

ANY_RECORD = Mock()
NO_RECORDS = []
ANY_RESPONSE = Mock()


@fixture
def mocked_cursor():
    return Mock(spec=Cursor)


@fixture
def mocked_pagination_strategy():
    return Mock(spec=PaginationStrategy)


@fixture
def mocked_stop_condition():
    return Mock(spec=PaginationStopCondition)


def test_given_record_should_be_synced_when_is_met_return_false(mocked_cursor):
    mocked_cursor.should_be_synced.return_value = True
    assert not CursorStopCondition(mocked_cursor).is_met(response=ANY_RESPONSE, last_records=[ANY_RECORD, ANY_RECORD])


def test_given_record_should_not_be_synced_when_is_met_return_true(mocked_cursor):
    mocked_cursor.should_be_synced.return_value = False
    assert CursorStopCondition(mocked_cursor).is_met(response=ANY_RESPONSE, last_records=[ANY_RECORD, ANY_RECORD])


def test_given_stop_condition_is_met_when_next_page_token_then_return_none(mocked_pagination_strategy):
    cursor_mock = Mock(spec=Cursor)
    stop_condition = CursorStopCondition(cursor=cursor_mock)
    cursor_mock.should_be_synced.side_effect = [True, False]

    first_record = Mock(spec=Record)
    last_record = Mock(spec=Record)

    decorator = StopConditionPaginationStrategyDecorator(mocked_pagination_strategy, stop_condition)

    assert not decorator.next_page_token(ANY_RESPONSE, [last_record, first_record])


def test_given_stop_condition_is_not_met_when_next_page_token_then_delegate(mocked_pagination_strategy, mocked_stop_condition):
    mocked_stop_condition.is_met.return_value = False
    first_record = Mock(spec=Record)
    last_record = Mock(spec=Record)
    decorator = StopConditionPaginationStrategyDecorator(mocked_pagination_strategy, mocked_stop_condition)

    next_page_token = decorator.next_page_token(ANY_RESPONSE, [first_record, last_record])

    assert next_page_token == mocked_pagination_strategy.next_page_token.return_value
    mocked_pagination_strategy.next_page_token.assert_called_once_with(ANY_RESPONSE, [first_record, last_record])
    mocked_stop_condition.is_met.assert_called_once_with(ANY_RESPONSE, [first_record, last_record])


def test_given_no_records_when_next_page_token_then_delegate(mocked_pagination_strategy, mocked_stop_condition):
    decorator = StopConditionPaginationStrategyDecorator(mocked_pagination_strategy, mocked_stop_condition)

    next_page_token = decorator.next_page_token(ANY_RESPONSE, NO_RECORDS)

    assert next_page_token == mocked_pagination_strategy.next_page_token.return_value
    mocked_pagination_strategy.next_page_token.assert_called_once_with(ANY_RESPONSE, NO_RECORDS)


def test_when_reset_then_delegate(mocked_pagination_strategy, mocked_stop_condition):
    decorator = StopConditionPaginationStrategyDecorator(mocked_pagination_strategy, mocked_stop_condition)
    decorator.reset()
    mocked_pagination_strategy.reset.assert_called_once_with()


def test_when_get_page_size_then_delegate(mocked_pagination_strategy, mocked_stop_condition):
    decorator = StopConditionPaginationStrategyDecorator(mocked_pagination_strategy, mocked_stop_condition)

    page_size = decorator.get_page_size()

    assert page_size == mocked_pagination_strategy.get_page_size.return_value
    mocked_pagination_strategy.get_page_size.assert_called_once_with()


def make_response(**kwargs):
    response = Response()
    for k, v in kwargs.items():
        setattr(response, k, v)
    return response


@pytest.mark.parametrize(
    "test_name,condition,response,last_records,expected_result",
    [
        ("empty", "", make_response(), [ANY_RECORD], False),
        ("true_const", "{{ True }}", make_response(), [ANY_RECORD], True),
        ("false_const", "{{ False }}", make_response(), [ANY_RECORD], False),
        ("response_headers_false", "{{ headers['stop'] }}", make_response(headers={"stop": False}), [ANY_RECORD], False),
        ("response_headers_true", "{{ headers['stop'] }}", make_response(headers={"stop": True}), [ANY_RECORD], True),
        ("response_body_false", "{{ 'records' not in response }}", make_response(_content=b'{"records": []}'), [ANY_RECORD], False),
        ("response_body_true", "{{ 'records' not in response }}", make_response(_content=b'{}'), [ANY_RECORD], True),
        ("last_records", "{{ last_records[0] }}", make_response(), [ANY_RECORD], True),
    ],
)
def test_interpolated_with_const(test_name, condition, response, last_records, expected_result):
    condition = InterpolatedStopCondition(condition=condition, decoder=JsonDecoder(parameters={}), parameters={}, config={})
    assert condition.is_met(response=response, last_records=last_records) == expected_result
