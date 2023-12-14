# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
import json
from copy import deepcopy
from pathlib import Path as FilePath
from typing import Any, Dict, Optional, Union
from unittest import TestCase
from unittest.mock import Mock

import pytest
from airbyte_cdk.test.mock_http.response import HttpResponse
from airbyte_cdk.test.mock_http.response_builder import (
    FieldPath,
    FieldUpdatePaginationStrategy,
    HttpResponseBuilder,
    NestedPath,
    PaginationStrategy,
    Path,
    RecordBuilder,
    create_record_builder,
    create_response_builder,
    find_template,
)

_RECORDS_FIELD = "records_field"
_ID_FIELD = "record_id"
_CURSOR_FIELD = "record_cursor"
_ANY_RECORD = {"a_record_field": "a record value"}
_SOME_RECORDS = {_RECORDS_FIELD: [_ANY_RECORD]}
_A_RESPONSE_TEMPLATE = _SOME_RECORDS

_RECORD_BUILDER = 0
_RESPONSE_BUILDER = 1


def _record_builder(
    response_template: Dict[str, Any],
    records_path: Union[FieldPath, NestedPath],
    record_id_path: Optional[Path] = None,
    record_cursor_path: Optional[Union[FieldPath, NestedPath]] = None,
) -> RecordBuilder:
    return create_record_builder(deepcopy(response_template), records_path, record_id_path, record_cursor_path)


def _any_record_builder() -> RecordBuilder:
    return create_record_builder({"record_path": [{"a_record": "record value"}]}, FieldPath("record_path"))


def _response_builder(
    response_template: Dict[str, Any],
    records_path: Union[FieldPath, NestedPath],
    pagination_strategy: Optional[PaginationStrategy] = None
) -> HttpResponseBuilder:
    return create_response_builder(deepcopy(response_template), records_path, pagination_strategy=pagination_strategy)


def _body(response: HttpResponse) -> Dict[str, Any]:
    return json.loads(response.body)


class RecordBuilderTest(TestCase):
    def test_given_with_id_when_build_then_set_id(self) -> None:
        builder = _record_builder({_RECORDS_FIELD: [{_ID_FIELD: "an id"}]}, FieldPath(_RECORDS_FIELD), FieldPath(_ID_FIELD))
        record = builder.with_id("another id").build()
        assert record[_ID_FIELD] == "another id"

    def test_given_nested_id_when_build_then_set_id(self) -> None:
        builder = _record_builder({_RECORDS_FIELD: [{"nested": {_ID_FIELD: "id"}}]}, FieldPath(_RECORDS_FIELD), NestedPath(["nested", _ID_FIELD]))
        record = builder.with_id("another id").build()
        assert record["nested"][_ID_FIELD] == "another id"

    def test_given_id_path_not_provided_but_with_id_when_build_then_raise_error(self) -> None:
        builder = _record_builder(_A_RESPONSE_TEMPLATE, FieldPath(_RECORDS_FIELD), None)
        with pytest.raises(ValueError):
            builder.with_id("any_id").build()

    def test_given_no_id_in_template_for_path_when_build_then_raise_error(self) -> None:
        with pytest.raises(ValueError):
            _record_builder({_RECORDS_FIELD: [{"record without id": "should fail"}]}, FieldPath(_RECORDS_FIELD), FieldPath(_ID_FIELD))

    def test_given_with_cursor_when_build_then_set_id(self) -> None:
        builder = _record_builder(
            {_RECORDS_FIELD: [{_CURSOR_FIELD: "a cursor"}]},
            FieldPath(_RECORDS_FIELD),
            record_cursor_path=FieldPath(_CURSOR_FIELD)
        )
        record = builder.with_cursor("another cursor").build()
        assert record[_CURSOR_FIELD] == "another cursor"

    def test_given_nested_cursor_when_build_then_set_cursor(self) -> None:
        builder = _record_builder(
            {_RECORDS_FIELD: [{"nested": {_CURSOR_FIELD: "a cursor"}}]},
            FieldPath(_RECORDS_FIELD),
            record_cursor_path=NestedPath(["nested", _CURSOR_FIELD])
        )
        record = builder.with_cursor("another cursor").build()
        assert record["nested"][_CURSOR_FIELD] == "another cursor"

    def test_given_with_field_when_build_then_write_field(self) -> None:
        builder = _any_record_builder()
        record = builder.with_field(FieldPath("to_write_field"), "a field value").build()
        assert record["to_write_field"] == "a field value"

    def test_given_nested_cursor_when_build_then_write_field(self) -> None:
        builder = _any_record_builder()
        record = builder.with_field(NestedPath(["path", "to_write_field"]), "a field value").build()
        assert record["path"]["to_write_field"] == "a field value"

    def test_given_cursor_path_not_provided_but_with_id_when_build_then_raise_error(self) -> None:
        builder = _record_builder(_A_RESPONSE_TEMPLATE, FieldPath(_RECORDS_FIELD))
        with pytest.raises(ValueError):
            builder.with_cursor("any cursor").build()

    def test_given_no_cursor_in_template_for_path_when_build_then_raise_error(self) -> None:
        with pytest.raises(ValueError):
            _record_builder(
                {_RECORDS_FIELD: [{"record without cursor": "should fail"}]},
                FieldPath(_RECORDS_FIELD),
                record_cursor_path=FieldPath(_ID_FIELD)
            )


class HttpResponseBuilderTest(TestCase):
    def test_given_records_in_template_but_no_with_records_when_build_then_no_records(self) -> None:
        builder = _response_builder({_RECORDS_FIELD: [{"a_record_field": "a record value"}]}, FieldPath(_RECORDS_FIELD))
        response = builder.build()
        assert len(_body(response)[_RECORDS_FIELD]) == 0

    def test_given_many_records_when_build_then_response_has_records(self) -> None:
        builder = _response_builder(_A_RESPONSE_TEMPLATE, FieldPath(_RECORDS_FIELD))
        a_record_builder = Mock(spec=RecordBuilder)
        a_record_builder.build.return_value = {"a record": 1}
        another_record_builder = Mock(spec=RecordBuilder)
        another_record_builder.build.return_value = {"another record": 2}

        response = builder.with_record(a_record_builder).with_record(another_record_builder).build()

        assert len(_body(response)[_RECORDS_FIELD]) == 2

    def test_when_build_then_default_status_code_is_200(self) -> None:
        builder = _response_builder(_A_RESPONSE_TEMPLATE, FieldPath(_RECORDS_FIELD))
        response = builder.build()
        assert response.status_code == 200

    def test_given_status_code_when_build_then_status_code_is_set(self) -> None:
        builder = _response_builder(_A_RESPONSE_TEMPLATE, FieldPath(_RECORDS_FIELD))
        response = builder.with_status_code(239).build()
        assert response.status_code == 239

    def test_given_pagination_with_strategy_when_build_then_apply_strategy(self) -> None:
        builder = _response_builder(
            {"has_more_pages": False} | _SOME_RECORDS,
            FieldPath(_RECORDS_FIELD),
            pagination_strategy=FieldUpdatePaginationStrategy(FieldPath("has_more_pages"), "yes more page")
        )

        response = builder.with_pagination().build()

        assert _body(response)["has_more_pages"] == "yes more page"

    def test_given_no_pagination_strategy_but_pagination_when_build_then_raise_error(self) -> None:
        builder = _response_builder(_A_RESPONSE_TEMPLATE, FieldPath(_RECORDS_FIELD))
        with pytest.raises(ValueError):
            builder.with_pagination()


class UtilMethodsTest(TestCase):
    def test_from_resource_file(self) -> None:
        template = find_template("test-resource", __file__)
        assert template == {"test-source template": "this is a template for test-resource"}

    def test_given_cwd_doesnt_have_unit_tests_as_parent_when_from_resource_file__then_raise_error(self) -> None:
        with pytest.raises(ValueError):
            find_template("test-resource", str(FilePath(__file__).parent.parent.parent.parent))

    def test_given_records_path_invalid_when_create_builders_from_resource_then_raise_exception(self) -> None:
        with pytest.raises(ValueError):
            create_record_builder(_A_RESPONSE_TEMPLATE, NestedPath(["invalid", "record", "path"]))
