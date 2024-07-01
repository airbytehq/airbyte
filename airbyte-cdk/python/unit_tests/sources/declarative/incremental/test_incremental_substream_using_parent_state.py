def test_given_parent_cursor_child_cursor_and_record_cursor_all_have_the_same_value_then_record_is_synced_and_state_is_unchanged():
    current_state = {
        "states": [
            {
                "partition": {"parent_id": "ABC"},
                "cursor": {"updated_at": "2021-01-01T00:00:00"},
            }
        ],
        "parent_state": {"updated_at": "2021-01-01T00:00:00"},
    }

    parent_record = {
        "id": "ABC",
        "updated_at": "2021-01-01T00:00:00",
    }

    record_should_be_synced = True
    expected_output_state = {
        "states": [
            {
                "partition": {"parent_id": "ABC"},
                "cursor": {"updated_at": "2021-01-01T00:00:00"},
            }
        ],
        "parent_state": {"updated_at": "2021-01-01T00:00:00"},
    }

    assert False


def test_given_parent_cursor_child_cursor_are_equal_and_record_cursor_is_more_recent_then_record_is_synced_and_state_is_updated():
    current_state = {
        "states": [
            {
                "partition": {"parent_id": "ABC"},
                "cursor": {"updated_at": "2021-01-01T00:00:00"},
            }
        ],
        "parent_state": {"updated_at": "2021-01-01T00:00:00"}
    }

    parent_record = {
        "id": "ABC",
        "updated_at": "2021-01-01T00:00:00",
    }
    record = {
        "id": "123",
        "parent_id": "ABC",
        "updated_at": "2021-01-02T00:00:00",
    }

    record_should_be_synced = True
    expected_output_state = {
        "states": [
            {
                "partition": {"parent_id": "ABC"},
                "cursor": {"updated_at": "2021-01-02T00:00:00"},
            }
        ],
        "parent_state": {"updated_at": "2021-01-01T00:00:00"},
    }

    assert False


def test_given_parent_cursor_is_more_recent_than_parent_record_and_record_cursor_is_more_recent_then_record_is_synced():
    """
    This is the case I think is problematic with the suggested approach.
    """
    current_state = {
        "states": [
            {
                "partition": {"parent_id": "ABC"},
                "cursor": {"updated_at": "2021-01-02T00:00:00"},
            }
        ],
        "parent_state": {"updated_at": "2021-01-01T00:00:00"},
    }

    parent_record = {
        "id": "ABC",
        "updated_at": "2020-01-01T00:00:00",
    }
    record = {
        "id": "123",
        "parent_id": "ABC",
        "updated_at": "2021-01-03T00:00:00",
    }

    record_should_be_synced = True
    expected_output_state = {
        "states": [
            {
                "partition": {"parent_id": "ABC"},
                "cursor": {"updated_at": "2021-01-03T00:00:00"},
            }
        ],
        "parent_state": {"updated_at": "2021-01-01T00:00:00"},
    }

    assert False
