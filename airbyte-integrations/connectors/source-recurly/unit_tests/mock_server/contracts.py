# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest
from conftest import get_source
from jsonschema import Draft7Validator, FormatChecker

from airbyte_cdk.models import AirbyteStateMessage, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse

from .config import BEGIN_TIME, END_TIME, ConfigBuilder
from .request_builder import RequestBuilder
from .response_builder import ResponseBuilder


@dataclass
class Parent:
    path: str
    params: dict[str, str]
    records: list[dict[str, Any]]


@dataclass
class Partition:
    path: str
    fields: dict[str, str] = field(default_factory=dict)


@dataclass
class StreamCase:
    name: str
    path: str
    params: dict[str, str]
    record: dict[str, Any]
    parents: tuple[Parent, ...] = ()
    partitions: tuple[Partition, ...] = ()


def dated_params(begin: str = BEGIN_TIME) -> dict[str, str]:
    return {"sort": "updated_at", "order": "asc", "limit": "200", "begin_time": begin, "end_time": END_TIME}


def register(http_mocker: HttpMocker, requests: list[HttpRequest], builder: RequestBuilder, response: HttpResponse) -> None:
    request = builder.build()
    http_mocker.get(request, response)
    requests.append(request)


def given_parents(http_mocker: HttpMocker, requests: list[HttpRequest], case: StreamCase) -> None:
    for parent in case.parents:
        register(
            http_mocker,
            requests,
            RequestBuilder.endpoint(parent.path).with_query_params(**parent.params),
            ResponseBuilder().with_records(*parent.records).build(),
        )


def assert_requests(http_mocker: HttpMocker, requests: list[HttpRequest], total: int) -> None:
    assert len(requests) == total
    for request in requests:
        http_mocker.assert_number_of_calls(request, 1)
    assert http_mocker._mocker.call_count == total


def read_case(
    case: StreamCase, sync_mode: SyncMode = SyncMode.full_refresh, state: list[AirbyteStateMessage] | None = None
) -> EntrypointOutput:
    config = ConfigBuilder().build()
    catalog = CatalogBuilder().with_stream(case.name, sync_mode).build()
    source = get_source(config, state=state, catalog=catalog)
    discovered = {stream.name: stream.json_schema for stream in source.discover(logging.getLogger(__name__), config).streams}
    assert case.name in discovered, f"Stream {case.name} is missing from discovery"
    schema = discovered[case.name]
    output = read(source, config=config, catalog=catalog, state=state)
    assert not output.errors
    assert not any(message.log.level == "ERROR" for message in output.logs)
    validator = Draft7Validator(schema, format_checker=FormatChecker())
    for message in output.records:
        record = message.record.data
        assert record.keys() <= schema["properties"].keys()
        validator.validate(record)
    return output


@pytest.mark.parametrize("empty", [False, True], ids=["two_pages", "empty"])
def test_full_refresh(stream_case: StreamCase, empty: bool) -> None:
    case = stream_case
    requests = []
    expected = []
    partitions = case.partitions or (Partition(case.path),)
    with HttpMocker() as http_mocker:
        given_parents(http_mocker, requests, case)
        for index, partition in enumerate(partitions):
            first = RequestBuilder.endpoint(partition.path).with_query_params(**case.params)
            response = ResponseBuilder()
            if not empty:
                record = dict(deepcopy(case.record), id=f"{case.name}-{index}-1")
                expected.append(dict(record, **partition.fields))
                response.with_records(record)
                if index == 0:
                    second = RequestBuilder.endpoint(partition.path).with_query_params(**case.params, cursor="page2")
                    response.with_next_page(second)
                    second_record = dict(deepcopy(case.record), id=f"{case.name}-{index}-2")
                    expected.append(dict(second_record, **partition.fields))
                    third = RequestBuilder.endpoint(partition.path).with_query_params(**case.params, cursor="must-not-fetch")
                    terminal = ResponseBuilder().with_records(second_record).with_next_page(third).with_has_more(False)
                    register(http_mocker, requests, second, terminal.build())
            register(http_mocker, requests, first, response.build())
        output = read_case(case)
        records = [message.record.data for message in output.records]
        expected = [{key: value for key, value in record.items() if value is not None} for record in expected]
        assert sorted(record["id"] for record in records) == sorted(record["id"] for record in expected)
        assert sorted(records, key=lambda record: record["id"]) == sorted(expected, key=lambda record: record["id"]), (records, expected)
        total = len(case.parents) + len(partitions) + (0 if empty else 1)
        assert_requests(http_mocker, requests, total)


def test_incremental_resume(stream_case: StreamCase, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    case = stream_case
    first_record = dict(deepcopy(case.record), id="first", updated_at="2025-01-01T12:00:00Z")
    latest_record = dict(deepcopy(case.record), id="latest", updated_at="2025-01-02T00:00:00Z")
    with HttpMocker() as http_mocker:
        requests = []
        register(
            http_mocker,
            requests,
            RequestBuilder.endpoint(case.path).with_query_params(**dated_params()),
            ResponseBuilder().with_records(first_record, latest_record).build(),
        )
        first_output = read_case(case, SyncMode.incremental)
        assert [message.record.data["id"] for message in first_output.records] == ["first", "latest"]
        state = [first_output.state_messages[-1].state]
        assert state[0].stream.stream_state.__dict__ == {"updated_at": latest_record["updated_at"]}
        assert_requests(http_mocker, requests, 1)

    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path / "resumed"))
    new_record = dict(deepcopy(case.record), id="new", updated_at="2025-01-02T12:00:00Z")
    with HttpMocker() as http_mocker:
        requests = []
        register(
            http_mocker,
            requests,
            RequestBuilder.endpoint(case.path).with_query_params(**dated_params(latest_record["updated_at"])),
            ResponseBuilder().with_records(latest_record, new_record).build(),
        )
        resumed = read_case(case, SyncMode.incremental, state)
        assert [message.record.data["id"] for message in resumed.records] == ["latest", "new"]
        assert resumed.state_messages[-1].state.stream.stream_state.__dict__ == {"updated_at": new_record["updated_at"]}
        assert_requests(http_mocker, requests, 1)
