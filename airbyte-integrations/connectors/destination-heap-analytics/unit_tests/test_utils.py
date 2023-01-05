#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pendulum
from destination_heap_analytics.utils import datetime_to_string, flatten_json


class TestDatetimeToString:
    def test_min_date_time_to_string(self):
        assert datetime_to_string(pendulum.DateTime.min) == "0001-01-01T00:00:00Z"

    def test_valid_date_time_to_string(self):
        in_utc = pendulum.datetime(2022, 10, 26, 3, 6, 59)
        assert datetime_to_string(in_utc) == "2022-10-26T03:06:59Z"


class TestFlattenJson:
    def test_flatten_none(self):
        assert flatten_json({"myUndefined": None}) == {"myUndefined": None}
        assert flatten_json({"myNull": None}) == {"myNull": None}

    def test_flatten_number(self):
        assert flatten_json({"myNumber": 1}) == {"myNumber": 1}

    def test_flatten_string(self):
        assert flatten_json({"myString": "1"}) == {"myString": "1"}

    def test_flatten_boolean(self):
        assert flatten_json({"myTrue": True}) == {"myTrue": True}
        assert flatten_json({"myFalse": False}) == {"myFalse": False}

    def test_flatten_array_of_nulls(self):
        assert flatten_json({"myNulls": [None, 1, None, 3]}) == {"myNulls.0": None, "myNulls.1": 1, "myNulls.2": None, "myNulls.3": 3}

    def test_flatten_array_of_numbers(self):
        assert flatten_json({"myNumbers": [1, 2, 3, 4]}) == {"myNumbers.0": 1, "myNumbers.1": 2, "myNumbers.2": 3, "myNumbers.3": 4}

    def test_flatten_array_of_strings(self):
        assert flatten_json({"myStrings": ["a", "1", "b", "2"]}) == {
            "myStrings.0": "a",
            "myStrings.1": "1",
            "myStrings.2": "b",
            "myStrings.3": "2",
        }

    def test_flatten_array_of_booleans(self):
        assert flatten_json({"myBools": [True, False, True, False]}) == {
            "myBools.0": True,
            "myBools.1": False,
            "myBools.2": True,
            "myBools.3": False,
        }

    def test_flatten_a_complex_object(self):
        embeded_object = {
            "firstName": "John",
            "middleName": "",
            "lastName": "Green",
            "car": {
                "make": "Honda",
                "model": "Civic",
                "year": None,
                "revisions": [
                    {"miles": 10150, "code": "REV01", "changes": 0, "firstTime": True},
                    {
                        "miles": 20021,
                        "code": "REV02",
                        "firstTime": False,
                        "changes": [
                            {"type": "asthetic", "desc": "Left tire cap", "price": 123.45},
                            {"type": "mechanic", "desc": "Engine pressure regulator", "engineer": None},
                        ],
                    },
                ],
            },
            "visits": [{"date": "2015-01-01", "dealer": "DEAL-001", "useCoupon": True}, {"date": "2015-03-01", "dealer": "DEAL-002"}],
        }
        assert flatten_json(embeded_object) == (
            {
                "car.make": "Honda",
                "car.model": "Civic",
                "car.revisions.0.changes": 0,
                "car.revisions.0.code": "REV01",
                "car.revisions.0.miles": 10150,
                "car.revisions.0.firstTime": True,
                "car.revisions.1.changes.0.desc": "Left tire cap",
                "car.revisions.1.changes.0.price": 123.45,
                "car.revisions.1.changes.0.type": "asthetic",
                "car.revisions.1.changes.1.desc": "Engine pressure regulator",
                "car.revisions.1.changes.1.engineer": None,
                "car.revisions.1.changes.1.type": "mechanic",
                "car.revisions.1.firstTime": False,
                "car.revisions.1.code": "REV02",
                "car.revisions.1.miles": 20021,
                "car.year": None,
                "firstName": "John",
                "lastName": "Green",
                "middleName": "",
                "visits.0.date": "2015-01-01",
                "visits.0.dealer": "DEAL-001",
                "visits.0.useCoupon": True,
                "visits.1.date": "2015-03-01",
                "visits.1.dealer": "DEAL-002",
            }
        )
