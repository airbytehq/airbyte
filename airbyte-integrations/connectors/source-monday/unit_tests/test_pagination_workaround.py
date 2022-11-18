from source_monday.pagination_workaround import PageIncrementWorkaround


def test_next_page_token_to_be_interpolated(mocker):
    page_increment = PageIncrementWorkaround(
        config=mocker.MagicMock(),
        page_size="{{ options['optionally_defined_page_size'] }}",
        options={"optionally_defined_page_size": 1}
    )
    assert page_increment.get_page_size() == 1


def test_next_page_token_has_more_records_flow(mocker):
    page_increment = PageIncrementWorkaround(
        config=mocker.MagicMock(),
        page_size="{{ options['optionally_defined_page_size'] }}",
        options={"optionally_defined_page_size": 1}
    )

    assert getattr(page_increment, "_page") == 1

    assert page_increment.next_page_token(
        response=mocker.MagicMock(),
        last_records=[{}]
    ) == 2

    assert getattr(page_increment, "_page") == 2

    assert page_increment.next_page_token(
        response=mocker.MagicMock(),
        last_records=[{}]
    ) == 3

    assert getattr(page_increment, "_page") == 3


def test_next_page_token_last_page(mocker):
    page_increment = PageIncrementWorkaround(
        config=mocker.MagicMock(),
        page_size="{{ options['optionally_defined_page_size'] }}",
        options={"optionally_defined_page_size": 2}
    )
    setattr(page_increment, "_page", 2)

    assert page_increment.next_page_token(
        response=mocker.MagicMock(),
        last_records=[{}]
    ) is None


def test_next_page_token_reset(mocker):
    page_increment = PageIncrementWorkaround(
        config=mocker.MagicMock(),
        page_size="{{ options['optionally_defined_page_size'] }}",
        options={"optionally_defined_page_size": 1}
    )

    assert getattr(page_increment, "_page") == 1

    page_increment.next_page_token(
        response=mocker.MagicMock(),
        last_records=[{}]
    )

    assert getattr(page_increment, "_page") == 2

    page_increment.reset()

    assert getattr(page_increment, "_page") == 1


def test_next_page_token_set_page_size_based_on_first_response_record_list(mocker):
    page_increment = PageIncrementWorkaround(
        config=mocker.MagicMock(),
        page_size="{{ options['optionally_defined_page_size'] }}",
        options={}
    )

    assert getattr(page_increment, "_page") == 1
    assert getattr(page_increment, "_page_size") is None
    assert page_increment.page_size.eval(page_increment.config) == ""

    page_increment.next_page_token(
        response=mocker.MagicMock(),
        last_records=[{}, {}, {}, {}]
    )

    assert getattr(page_increment, "_page") == 2
    assert getattr(page_increment, "_page_size") == 4
    assert page_increment.page_size.eval(page_increment.config) == ""

    page_increment.next_page_token(
        response=mocker.MagicMock(),
        last_records=[{}, {}, {}, {}]
    )

    assert getattr(page_increment, "_page") == 3
    assert getattr(page_increment, "_page_size") == 4
    assert page_increment.page_size.eval(page_increment.config) == ""

    page_increment.next_page_token(
        response=mocker.MagicMock(),
        last_records=[{}, {}]
    )

    assert getattr(page_increment, "_page") == 3
    assert getattr(page_increment, "_page_size") == 4
    assert page_increment.page_size.eval(page_increment.config) == ""
