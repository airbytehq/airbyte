from orchestrator.utils.dagster_helpers import string_array_to_hash


def test_string_array_to_hash_is_deterministic():
    strings = ["hello", "world", "foo", "bar", "baz"]
    assert string_array_to_hash(strings) == string_array_to_hash(strings)


def test_string_array_to_hash_ignores_repeated_strings():
    strings = ["hello", "world", "foo", "bar", "baz"]
    repeated_strings = ["hello", "world", "foo", "bar", "baz", "foo", "bar"]
    assert string_array_to_hash(strings) == string_array_to_hash(repeated_strings)


def test_string_array_to_hash_outputs_on_empty_list():
    assert string_array_to_hash([])


def test_string_array_to_hash_ignores_value_order_input():
    strings = ["baz", "bar", "foo", "world", "hello"]
    same_but_different_order = ["hello", "world", "foo", "bar", "baz"]
    assert string_array_to_hash(strings) == string_array_to_hash(same_but_different_order)


def test_string_array_to_hash_differs():
    unique_cursor_1 = string_array_to_hash(["hello", "world", "foo"])
    unique_cursor_2 = string_array_to_hash(["hello", "world", "foo", "bar", "baz", "foo", "bar"])
    unique_cursor_3 = string_array_to_hash(["hello", "world", "baz"])
    unique_cursor_4 = string_array_to_hash(["world", "baz"])

    unique_set = set([unique_cursor_1, unique_cursor_2, unique_cursor_3, unique_cursor_4])
    assert len(unique_set) == 4
