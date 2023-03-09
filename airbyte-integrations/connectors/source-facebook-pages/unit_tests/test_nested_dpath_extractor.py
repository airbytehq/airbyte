#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
from typing import Any

from requests import Response
from source_facebook_pages.components import NestedDpathExtractor


def _create_response(content: Any) -> Response:
    response = Response()
    response._content = json.dumps(content).encode("utf-8")
    return response


def test_list_of_records():
    extractor = NestedDpathExtractor(
        field_pointer=["data", "insights", "data"],
        config={},
        options={},
    )
    content = {"data": [
        {"insights": {"data": [{"id": "id1", "name": "name1"}, {"id": "id2", "name": "name2"}]}},
        {"insights": {"data": [{"id": "id3", "name": "name3"}, {"id": "id4", "name": "name4"}]}},
    ]
    }
    response = _create_response(content)
    records = extractor.extract_records(response)

    assert records == [
        {"id": "id1", "name": "name1"}, {"id": "id2", "name": "name2"},
        {"id": "id3", "name": "name3"}, {"id": "id4", "name": "name4"}
    ]


def test_no_field_pointer():
    extractor = NestedDpathExtractor(
        field_pointer=[],
        config={},
        options={},
    )
    obj_response = _create_response({"data": {}})
    obj_records = extractor.extract_records(obj_response)

    assert obj_records == [{"data": {}}]


def test_no_records():
    extractor = NestedDpathExtractor(
        field_pointer=["data", "insights", "data"],
        config={},
        options={},
    )
    obj_response = _create_response({"data": {}})
    obj_records = extractor.extract_records(obj_response)

    assert obj_records == []


def test_single_record():
    extractor = NestedDpathExtractor(
        field_pointer=["data", "insights", "data"],
        config={},
        options={},
    )
    content = {"data": [
        {"insights": {"data": [{"id": "id1", "name": "name1"}]}}
    ]}
    response = _create_response(content)
    records = extractor.extract_records(response)

    assert records == [{"id": "id1", "name": "name1"}]
