#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
from typing import Any

from requests import Response
from source_alpha_vantage.object_dpath_extractor import ObjectDpathExtractor


def _create_response_with_body(body: Any) -> Response:
    response = Response()
    response._content = json.dumps(body).encode("utf-8")
    return response


def _create_response_with_dict_of_records() -> Response:
    response_body = {
        "data": {
            "2022-01-01": {
                "id": "id1",
                "name": "name1",
            },
            "2022-01-02": {
                "id": "id2",
                "name": "name2",
            },
        }
    }
    return _create_response_with_body(response_body)


def _create_response_with_list_of_records() -> Response:
    response_body = {
        "data": [
            {
                "id": "id1",
                "name": "name1",
            },
            {
                "id": "id2",
                "name": "name2",
            },
        ]
    }
    return _create_response_with_body(response_body)


def test_no_key_injection():
    extractor = ObjectDpathExtractor(
        field_pointer=["data"],
        config={},
        options={},
    )

    response = _create_response_with_dict_of_records()
    records = extractor.extract_records(response)

    assert records == [
        {
            "id": "id1",
            "name": "name1",
        },
        {
            "id": "id2",
            "name": "name2",
        },
    ]


def test_key_injection():
    extractor = ObjectDpathExtractor(
        field_pointer=["data"],
        inject_key_as_field="date",
        config={},
        options={},
    )

    response = _create_response_with_dict_of_records()
    records = extractor.extract_records(response)

    assert records == [
        {
            "date": "2022-01-01",
            "id": "id1",
            "name": "name1",
        },
        {
            "date": "2022-01-02",
            "id": "id2",
            "name": "name2",
        },
    ]


def test_key_injection_with_interpolation():
    extractor = ObjectDpathExtractor(
        field_pointer=["data"],
        inject_key_as_field="{{ config['key_field'] }}",
        config={"key_field": "date"},
        options={},
    )

    response = _create_response_with_dict_of_records()
    records = extractor.extract_records(response)

    assert records == [
        {
            "date": "2022-01-01",
            "id": "id1",
            "name": "name1",
        },
        {
            "date": "2022-01-02",
            "id": "id2",
            "name": "name2",
        },
    ]


def test_list_of_records():
    extractor = ObjectDpathExtractor(
        field_pointer=["data"],
        config={},
        options={},
    )

    response = _create_response_with_dict_of_records()
    records = extractor.extract_records(response)

    assert records == [
        {
            "id": "id1",
            "name": "name1",
        },
        {
            "id": "id2",
            "name": "name2",
        },
    ]


def test_no_records():
    extractor = ObjectDpathExtractor(
        field_pointer=["data"],
        config={},
        options={},
    )

    obj_response = _create_response_with_body({"data": {}})
    obj_records = extractor.extract_records(obj_response)

    assert obj_records == []

    list_response = _create_response_with_body({"data": []})
    list_records = extractor.extract_records(list_response)

    assert list_records == []


def test_single_record():
    extractor = ObjectDpathExtractor(
        field_pointer=["data"],
        config={},
        options={},
    )

    response = _create_response_with_body({"data": {"id": "id1", "name": "name1"}})
    records = extractor.extract_records(response)

    assert records == [{"id": "id1", "name": "name1"}]
