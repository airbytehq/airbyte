#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from datetime import date

from faunadb.objects import FaunaTime, Ref
from source_fauna.serialize import _fauna_value_to_airbyte


def check_value(fauna, airbyte):
    assert _fauna_value_to_airbyte(fauna) == airbyte


def test_date():
    check_value(date(2022, 3, 4), "2022-03-04")
    check_value(FaunaTime("2022-03-04T12:00:30Z"), "2022-03-04T12:00:30Z")


def test_fauna_time():
    check_value(FaunaTime("2022-03-04"), "2022-03-04")


def test_bytes():
    check_value(bytes("hello world", "utf-8"), "aGVsbG8gd29ybGQ=")
    check_value(bytearray("hello world", "utf-8"), "aGVsbG8gd29ybGQ=")


def test_ref():
    # Valid refs
    check_value(Ref("1234", Ref("foo", Ref("collections"))), {"id": "1234", "collection": "foo", "type": "document"})
    check_value(Ref("1234", Ref("foo", Ref("nopes"))), {"id": "1234", "type": "unknown"})
    check_value(Ref("foo", Ref("collections")), {"id": "foo", "type": "collection"})
    check_value(Ref("my_db", Ref("databases")), {"id": "my_db", "type": "database"})
    check_value(Ref("ts", Ref("indexes")), {"id": "ts", "type": "index"})

    check_value(Ref("value", Ref("keys")), {"id": "value", "type": "key"})
    check_value(Ref("value", Ref("credentials")), {"id": "value", "type": "credential"})
    check_value(Ref("value", Ref("tokens")), {"id": "value", "type": "token"})

    # Failure cases (we should never crash, but we will produce undefined data)
    check_value(Ref("1234"), {"id": "1234", "type": "unknown"})
    check_value(Ref("ts", Ref("indexes_typoed")), {"id": "ts", "type": "indexes_typoed"})
    check_value(
        Ref("ref_id?", Ref("or_am_i_ref_id?", Ref("bar", Ref("collections")))),
        {
            "id": "ref_id?",
            "type": "unknown",
        },
    )


def test_recursive():
    check_value({"nested_ref": Ref("3", Ref("collections"))}, {"nested_ref": {"id": "3", "type": "collection"}})
    check_value({"nested_date": date(2022, 3, 4)}, {"nested_date": "2022-03-04"})
    check_value({"nested_dict": {"nested_date": date(2022, 3, 4)}}, {"nested_dict": {"nested_date": "2022-03-04"}})
    check_value(
        {"array": [date(2022, 3, 4), Ref("3", Ref("collections"))]},
        {"array": ["2022-03-04", {"id": "3", "type": "collection"}]},
    )
    check_value(
        {"nested_array": {"value": [date(2022, 3, 4)]}},
        {"nested_array": {"value": ["2022-03-04"]}},
    )
