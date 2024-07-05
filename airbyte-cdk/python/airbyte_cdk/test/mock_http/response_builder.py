# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import functools
import json
from abc import ABC, abstractmethod
from pathlib import Path as FilePath
from typing import Any, Dict, List, Optional, Union

from airbyte_cdk.test.mock_http import HttpResponse


def _extract(path: List[str], response_template: Dict[str, Any]) -> Any:
    return functools.reduce(lambda a, b: a[b], path, response_template)


def _replace_value(dictionary: Dict[str, Any], path: List[str], value: Any) -> None:
    current = dictionary
    for key in path[:-1]:
        current = current[key]
    current[path[-1]] = value


def _write(dictionary: Dict[str, Any], path: List[str], value: Any) -> None:
    current = dictionary
    for key in path[:-1]:
        current = current.setdefault(key, {})
    current[path[-1]] = value


class Path(ABC):
    @abstractmethod
    def write(self, template: Dict[str, Any], value: Any) -> None:
        pass

    @abstractmethod
    def update(self, template: Dict[str, Any], value: Any) -> None:
        pass

    def extract(self, template: Dict[str, Any]) -> Any:
        pass


class FieldPath(Path):
    def __init__(self, field: str):
        self._path = [field]

    def write(self, template: Dict[str, Any], value: Any) -> None:
        _write(template, self._path, value)

    def update(self, template: Dict[str, Any], value: Any) -> None:
        _replace_value(template, self._path, value)

    def extract(self, template: Dict[str, Any]) -> Any:
        return _extract(self._path, template)

    def __str__(self) -> str:
        return f"FieldPath(field={self._path[0]})"


class NestedPath(Path):
    def __init__(self, path: List[str]):
        self._path = path

    def write(self, template: Dict[str, Any], value: Any) -> None:
        _write(template, self._path, value)

    def update(self, template: Dict[str, Any], value: Any) -> None:
        _replace_value(template, self._path, value)

    def extract(self, template: Dict[str, Any]) -> Any:
        return _extract(self._path, template)

    def __str__(self) -> str:
        return f"NestedPath(path={self._path})"


class PaginationStrategy(ABC):
    @abstractmethod
    def update(self, response: Dict[str, Any]) -> None:
        pass


class FieldUpdatePaginationStrategy(PaginationStrategy):
    def __init__(self, path: Path, value: Any):
        self._path = path
        self._value = value

    def update(self, response: Dict[str, Any]) -> None:
        self._path.update(response, self._value)


class RecordBuilder:
    def __init__(self, template: Dict[str, Any], id_path: Optional[Path], cursor_path: Optional[Union[FieldPath, NestedPath]]):
        self._record = template
        self._id_path = id_path
        self._cursor_path = cursor_path

        self._validate_template()

    def _validate_template(self) -> None:
        paths_to_validate = [
            ("_id_path", self._id_path),
            ("_cursor_path", self._cursor_path),
        ]
        for field_name, field_path in paths_to_validate:
            self._validate_field(field_name, field_path)

    def _validate_field(self, field_name: str, path: Optional[Path]) -> None:
        try:
            if path and not path.extract(self._record):
                raise ValueError(f"{field_name} `{path}` was provided but it is not part of the template `{self._record}`")
        except (IndexError, KeyError) as exception:
            raise ValueError(f"{field_name} `{path}` was provided but it is not part of the template `{self._record}`") from exception

    def with_id(self, identifier: Any) -> "RecordBuilder":
        self._set_field("id", self._id_path, identifier)
        return self

    def with_cursor(self, cursor_value: Any) -> "RecordBuilder":
        self._set_field("cursor", self._cursor_path, cursor_value)
        return self

    def with_field(self, path: Path, value: Any) -> "RecordBuilder":
        path.write(self._record, value)
        return self

    def _set_field(self, field_name: str, path: Optional[Path], value: Any) -> None:
        if not path:
            raise ValueError(
                f"{field_name}_path was not provided and hence, the record {field_name} can't be modified. Please provide `id_field` while "
                f"instantiating RecordBuilder to leverage this capability"
            )
        path.update(self._record, value)

    def build(self) -> Dict[str, Any]:
        return self._record


class HttpResponseBuilder:
    def __init__(
        self, template: Dict[str, Any], records_path: Union[FieldPath, NestedPath], pagination_strategy: Optional[PaginationStrategy]
    ):
        self._response = template
        self._records: List[RecordBuilder] = []
        self._records_path = records_path
        self._pagination_strategy = pagination_strategy
        self._status_code = 200

    def with_record(self, record: RecordBuilder) -> "HttpResponseBuilder":
        self._records.append(record)
        return self

    def with_pagination(self) -> "HttpResponseBuilder":
        if not self._pagination_strategy:
            raise ValueError(
                "`pagination_strategy` was not provided and hence, fields related to the pagination can't be modified. Please provide "
                "`pagination_strategy` while instantiating ResponseBuilder to leverage this capability"
            )
        self._pagination_strategy.update(self._response)
        return self

    def with_status_code(self, status_code: int) -> "HttpResponseBuilder":
        self._status_code = status_code
        return self

    def build(self) -> HttpResponse:
        self._records_path.update(self._response, [record.build() for record in self._records])
        return HttpResponse(json.dumps(self._response), self._status_code)


def _get_unit_test_folder(execution_folder: str) -> FilePath:
    path = FilePath(execution_folder)
    while path.name != "unit_tests":
        if path.name == path.root or path.name == path.drive:
            raise ValueError(f"Could not find `unit_tests` folder as a parent of {execution_folder}")
        path = path.parent
    return path


def find_template(resource: str, execution_folder: str) -> Dict[str, Any]:
    response_template_filepath = str(_get_unit_test_folder(execution_folder) / "resource" / "http" / "response" / f"{resource}.json")
    with open(response_template_filepath, "r") as template_file:
        return json.load(template_file)  # type: ignore  # we assume the dev correctly set up the resource file


def create_record_builder(
    response_template: Dict[str, Any],
    records_path: Union[FieldPath, NestedPath],
    record_id_path: Optional[Path] = None,
    record_cursor_path: Optional[Union[FieldPath, NestedPath]] = None,
) -> RecordBuilder:
    """
    This will use the first record define at `records_path` as a template for the records. If more records are defined, they will be ignored
    """
    try:
        record_template = records_path.extract(response_template)[0]
        if not record_template:
            raise ValueError(
                f"Could not extract any record from template at path `{records_path}`. "
                f"Please fix the template to provide a record sample or fix `records_path`."
            )
        return RecordBuilder(record_template, record_id_path, record_cursor_path)
    except (IndexError, KeyError):
        raise ValueError(f"Error while extracting records at path `{records_path}` from response template `{response_template}`")


def create_response_builder(
    response_template: Dict[str, Any], records_path: Union[FieldPath, NestedPath], pagination_strategy: Optional[PaginationStrategy] = None
) -> HttpResponseBuilder:
    return HttpResponseBuilder(response_template, records_path, pagination_strategy)
