#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
from source_close_com import OffsetIncrementWorkaround


def test_next_page_token_to_be_interpolated(mocker):
    offset_increment = OffsetIncrementWorkaround(
        config=mocker.MagicMock(),
        page_size="{{ options['optionally_defined_page_size'] }}",
        options={"optionally_defined_page_size": 1}
    )
    assert offset_increment.get_page_size() == 1


def test_next_page_token_has_more_records_flow(mocker):
    offset_increment = OffsetIncrementWorkaround(
        config=mocker.MagicMock(),
        page_size="{{ options['optionally_defined_page_size'] }}",
        options={"optionally_defined_page_size": 1}
    )

    assert getattr(offset_increment, "_offset") == 0

    assert offset_increment.next_page_token(
        response=mocker.MagicMock(),
        last_records=[{}]
    ) == 1

    assert getattr(offset_increment, "_offset") == 1

    assert offset_increment.next_page_token(
        response=mocker.MagicMock(),
        last_records=[{}]
    ) == 2

    assert getattr(offset_increment, "_offset") == 2


def test_next_page_token_last_page(mocker):
    offset_increment = OffsetIncrementWorkaround(
        config=mocker.MagicMock(),
        page_size="{{ options['optionally_defined_page_size'] }}",
        options={"optionally_defined_page_size": 2}
    )
    setattr(offset_increment, "_offset", 2)

    assert offset_increment.next_page_token(
        response=mocker.MagicMock(),
        last_records=[{}]
    ) is None


def test_next_page_token_reset(mocker):
    offset_increment = OffsetIncrementWorkaround(
        config=mocker.MagicMock(),
        page_size="{{ options['optionally_defined_page_size'] }}",
        options={"optionally_defined_page_size": 1}
    )

    assert getattr(offset_increment, "_offset") == 0

    offset_increment.next_page_token(
        response=mocker.MagicMock(),
        last_records=[{}]
    )

    assert getattr(offset_increment, "_offset") == 1

    offset_increment.reset()

    assert getattr(offset_increment, "_offset") == 0
