import contextlib
import functools
import json
import os
from pathlib import Path
from types import TracebackType
from typing import Mapping, Union, Optional, Any, Dict, List, Tuple, Callable

import requests_mock

from urllib.parse import parse_qs, urlencode, urlparse
from airbyte_protocol.models import SyncMode, ConfiguredAirbyteCatalog


class CatalogBuilder:
    def __init__(self) -> None:
        self._streams: Any = []

    def with_stream(self, name: str, sync_mode: SyncMode) -> "CatalogBuilder":
        self._streams.append({
            "stream": {
                "name": name,
                "json_schema": {},
                "supported_sync_modes": ["full_refresh", "incremental"],
                "source_defined_primary_key": [["id"]]
            },
            "primary_key": [["id"]],
            "sync_mode": sync_mode.name,
            "destination_sync_mode": "overwrite"
        })
        return self

    def build(self) -> ConfiguredAirbyteCatalog:
        return ConfiguredAirbyteCatalog.parse_obj({"streams": self._streams})


def _extract(records_field: List[str], response_template: Dict[str, Any]) -> Any:
    return functools.reduce(lambda a, b: a[b], records_field, response_template)


def _replace_value(dictionary: Dict[str, Any], path: List[str], value: Any) -> None:
    current = dictionary
    for key in path[:-1]:
        current = current[key]
    current[path[-1]] = value


class RecordBuilder:
    def __init__(self, template: Dict[str, Any], id_field: Optional[List[str]]):
        self._record = template
        self._id_field = id_field

    def with_id(self, identifier: Any) -> "RecordBuilder":
        if not self._id_field:
            raise ValueError(
                "`id_field` was not provided and hence, the record ID can't be modified. Please provide `id_field` while instantiating "
                "RecordBuilder to leverage this capability"
            )
        _replace_value(self._record, self._id_field, identifier)
        return self

    def build(self) -> Dict[str, Any]:
        return self._record


class ResponseBuilder:
    def __init__(self, template: Dict[str, Any], records_field: List[str], pagination_strategy: Optional[Callable[[Dict[str, Any]], None]]):
        self._response = template
        self._records: List[RecordBuilder] = []
        self._records_field = records_field
        self._pagination_strategy = pagination_strategy

    def with_record(self, record: RecordBuilder) -> "ResponseBuilder":
        self._records.append(record)
        return self

    def with_pagination(self) -> "ResponseBuilder":
        if not self._pagination_strategy:
            raise ValueError(
                "`pagination_strategy` was not provided and hence, fields related to the pagination can't be modified. Please provide "
                "`pagination_strategy` while instantiating ResponseBuilder to leverage this capability"
            )
        self._pagination_strategy(self._response)
        return self

    def build_json(self) -> Dict[str, Any]:
        _replace_value(self._response, self._records_field, [record.build() for record in self._records])
        return self._response


def _get_unit_test_folder() -> Path:
    path = Path(os.getcwd())
    while path.name != "unit_tests":
        path = path.parent
    return path


def create_builders_from_file(
    resource: str,
    records_field: List[str],
    record_id_field: Optional[List[str]] = None,
    pagination_strategy: Optional[Callable[[Dict[str, Any]], None]] = None
) -> Tuple[RecordBuilder, ResponseBuilder]:
    response_template_filepath = str(_get_unit_test_folder() / "http" / "responses" / f"{resource}.json")
    with open(response_template_filepath, "r") as template_file:
        response_template = json.load(template_file)
        try:
            record_template = _extract(records_field, response_template)[0]
            return RecordBuilder(record_template, record_id_field), ResponseBuilder(response_template, records_field, pagination_strategy)
        except IndexError as exception:
            raise ValueError(f"Could not extract field {records_field} from response template {response_template_filepath}") from exception


def _is_subdict(small: Mapping[Any, Any], big: Mapping[Any, Any]) -> bool:
    return dict(big, **small) == big


class HttpRequestMatcher:
    def __init__(self, url: str, query_params: Optional[Mapping[str, Union[int, str]]] = None, headers: Optional[Mapping[str, str]] = None):
        self._url = urlparse(url)
        if not self._url.params and query_params:
            self._url = urlparse(f"{url}?{urlencode(query_params)}")
        self._headers = headers if headers else {}

        self._called = False

    def match(self, request: requests_mock.request._RequestObjectProxy) -> bool:
        hit = self._match_url(request.url) and _is_subdict(self._headers, request.headers)
        if hit:
            self._called = True
        return hit

    def _match_url(self, url: str) -> bool:
        request_url = urlparse(url)
        return request_url.scheme == self._url.scheme and request_url.hostname == self._url.hostname and request_url.path == self._url.path and parse_qs(request_url.query) == parse_qs(self._url.query)

    def was_called(self) -> bool:
        return self._called

    def __str__(self) -> str:
        return f'HttpRequestMatcher(url={self._url}, headers={self._headers})'


class HttpMocker(contextlib.ContextDecorator):
    """
    WARNING: This implementation only works if the lib for performing HTTP requests is `requests`
    """
    def __init__(self) -> None:
        self._mocker = requests_mock.Mocker()
        self._matchers: List[HttpRequestMatcher] = []

    def __enter__(self) -> "HttpMocker":
        self._mocker.__enter__()
        return self

    def __exit__(self, exc_type: Optional[BaseException], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]) -> None:
        self._mocker.__exit__(exc_type, exc_val, exc_tb)

    def _validate_all_matchers_called(self) -> None:
        for matcher in self._matchers:
            if not matcher.was_called():
                raise ValueError(f"Expected all matchers to be called at least once but {matcher} wasn't")

    def get(self, matcher: HttpRequestMatcher, response: Any) -> None:
        self._matchers.append(matcher)
        self._mocker.get(
            requests_mock.ANY,
            additional_matcher=matcher.match,
            json=response
        )

    def __call__(self, f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            with self:
                kwargs['http_mocker'] = self
                try:
                    result = f(*args, **kwargs)
                    self._validate_all_matchers_called()
                    return result
                except AssertionError:
                    try:
                        self._validate_all_matchers_called()
                    except ValueError as http_mocker_exception:
                        raise ValueError(http_mocker_exception) from None
        return wrapper
