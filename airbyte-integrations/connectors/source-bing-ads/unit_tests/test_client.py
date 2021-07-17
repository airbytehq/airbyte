#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from datetime import datetime

import source_bing_ads.client
from suds import sudsobject


def test_sudsobject_todict_primitive_types():
    test_arr = ["1", "test", 1, [0, 0]]
    test_dict = {"k1": {"k2": 2, "k3": [1, 2, 3]}}
    test_date = datetime.utcnow()
    suds_obj = sudsobject.Object()
    suds_obj["int"] = 1
    suds_obj["arr"] = test_arr
    suds_obj["dict"] = test_dict
    suds_obj["date"] = test_date

    serialized_obj = source_bing_ads.client.Client.asdict(suds_obj)
    assert serialized_obj["int"] == 1
    assert serialized_obj["arr"] == test_arr
    assert serialized_obj["dict"] == test_dict
    assert serialized_obj["date"] == test_date.isoformat()


def test_sudsobject_todict_nested():
    test_date = datetime.utcnow()

    suds_obj = sudsobject.Object()
    nested_suds_1, nested_suds_2, nested_suds_3, nested_suds_4 = (
        sudsobject.Object(),
        sudsobject.Object(),
        sudsobject.Object(),
        sudsobject.Object(),
    )

    nested_suds_1["value"] = test_date
    nested_suds_2["value"] = 1
    nested_suds_3["value"] = "str"
    nested_suds_4["value"] = object()

    suds_obj["obj1"] = nested_suds_1
    suds_obj["arr"] = [nested_suds_2, nested_suds_3, nested_suds_4]

    serialized_obj = source_bing_ads.client.Client.asdict(suds_obj)
    assert serialized_obj["obj1"]["value"] == test_date.isoformat()
    assert serialized_obj["arr"][0]["value"] == nested_suds_2["value"]
    assert serialized_obj["arr"][1]["value"] == nested_suds_3["value"]
    assert serialized_obj["arr"][2]["value"] == nested_suds_4["value"]
