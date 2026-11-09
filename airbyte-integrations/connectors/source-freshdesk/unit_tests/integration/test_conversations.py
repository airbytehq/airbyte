# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from unittest import TestCase

import pytest
from config_builder import ConfigBuilder

from airbyte_cdk import ConfiguredAirbyteCatalog, SyncMode, TState, YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.entrypoint_wrapper import read as entrypoint_read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import (
    FieldPath,
    HttpResponseBuilder,
    RecordBuilder,
    RootPath,
    create_record_builder,
    create_response_builder,
    find_template,
)
from airbyte_cdk.test.state_builder import StateBuilder


def _get_manifest_path() -> Path:
    source_declarative_manifest_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if source_declarative_manifest_path.exists():
        return source_declarative_manifest_path
    return Path(__file__).parent.parent.parent


_SOURCE_FOLDER_PATH = _get_manifest_path()
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"

sys.path.append(str(_SOURCE_FOLDER_PATH))

_DOMAIN = "a-domain.freshdesk.com"
_START_DATE = "2022-01-01T00:00:00Z"
_TICKETS_URL = (
    f"https://{_DOMAIN}/api/v2/tickets?include=description%2Crequester%2Cstats&order_by=updated_at&order_type=asc"
    f"&per_page=100&updated_since={_START_DATE.replace(':', '%3A')}"
)


def _catalog(sync_mode: SyncMode = SyncMode.incremental) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream("conversations", sync_mode).build()


def _source(catalog: ConfiguredAirbyteCatalog, config: Dict[str, Any], state: Optional[TState]) -> YamlDeclarativeSource:
    return YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)


def _response_template() -> Dict[str, Any]:
    return find_template("conversations", __file__)


def _record() -> RecordBuilder:
    return create_record_builder(
        _response_template(), RootPath(), record_id_path=FieldPath("id"), record_cursor_path=FieldPath("created_at")
    )


def _response() -> HttpResponseBuilder:
    return create_response_builder(response_template=_response_template(), records_path=RootPath())


def _read(
    sync_mode: SyncMode = SyncMode.incremental,
    config_builder: Optional[ConfigBuilder] = None,
    state_builder: Optional[StateBuilder] = None,
) -> EntrypointOutput:
    catalog = _catalog(sync_mode)
    config = config_builder.build() if config_builder else ConfigBuilder().build()
    state = state_builder.build() if state_builder else StateBuilder().build()
    return entrypoint_read(_source(catalog, config, state), config, catalog, state)


def _ticket(ticket_id: int, updated_at: str) -> Dict[str, Any]:
    return {
        "id": ticket_id,
        "created_at": "2022-01-01T00:00:00Z",
        "updated_at": updated_at,
        "subject": f"Ticket {ticket_id}",
        "status": 2,
        "priority": 1,
    }


def _ticket_response(tickets: list[Dict[str, Any]]) -> HttpResponse:
    return HttpResponse(json.dumps(tickets), 200)


def _record_data(output: EntrypointOutput) -> list[Dict[str, Any]]:
    return [record.record.data for record in output.records]


class ConversationsTest(TestCase):
    @HttpMocker()
    def test_incremental_without_state_reads_conversations_for_each_updated_ticket(self, http_mocker: HttpMocker) -> None:
        first_updated_at = "2024-05-01T00:00:00Z"
        second_updated_at = "2024-05-02T00:00:00Z"
        http_mocker.get(HttpRequest(_TICKETS_URL), _ticket_response([_ticket(11, first_updated_at), _ticket(22, second_updated_at)]))
        http_mocker.get(
            HttpRequest(f"https://{_DOMAIN}/api/v2/tickets/11/conversations?per_page=100"),
            _response().with_record(_record().with_id(101)).build(),
        )
        http_mocker.get(
            HttpRequest(f"https://{_DOMAIN}/api/v2/tickets/22/conversations?per_page=100"),
            _response().with_record(_record().with_id(202)).build(),
        )

        output = _read(config_builder=ConfigBuilder().domain(_DOMAIN).start_date(datetime(2022, 1, 1)))

        records = _record_data(output)
        assert [record["ticket_updated_at"] for record in records] == [first_updated_at, second_updated_at]
        state = output.most_recent_state.stream_state.__dict__
        assert state["use_global_cursor"] is True
        assert state["state"]["ticket_updated_at"] == second_updated_at
        assert state["parent_state"]["tickets"]["updated_at"] == second_updated_at

    @HttpMocker()
    def test_incremental_with_parent_state_reads_only_updated_tickets(self, http_mocker: HttpMocker) -> None:
        parent_state = "2024-05-01T00:00:00Z"
        returned_ticket_state = "2024-05-02T00:00:00Z"
        tickets_url = _TICKETS_URL.replace(_START_DATE.replace(":", "%3A"), parent_state.replace(":", "%3A"))
        http_mocker.get(HttpRequest(tickets_url), _ticket_response([_ticket(22, returned_ticket_state)]))
        http_mocker.get(
            HttpRequest(f"https://{_DOMAIN}/api/v2/tickets/22/conversations?per_page=100"),
            _response().with_record(_record().with_id(202)).build(),
        )

        output = _read(
            config_builder=ConfigBuilder().domain(_DOMAIN).start_date(datetime(2022, 1, 1)),
            state_builder=StateBuilder().with_stream_state(
                "conversations",
                {
                    "use_global_cursor": True,
                    "state": {"ticket_updated_at": parent_state},
                    "parent_state": {"tickets": {"updated_at": parent_state}},
                },
            ),
        )

        assert [record["ticket_updated_at"] for record in _record_data(output)] == [returned_ticket_state]

    @HttpMocker()
    def test_full_refresh_reads_all_ticket_conversations(self, http_mocker: HttpMocker) -> None:
        first_updated_at = "2024-05-01T00:00:00Z"
        second_updated_at = "2024-05-02T00:00:00Z"
        http_mocker.get(HttpRequest(_TICKETS_URL), _ticket_response([_ticket(11, first_updated_at), _ticket(22, second_updated_at)]))
        http_mocker.get(
            HttpRequest(f"https://{_DOMAIN}/api/v2/tickets/11/conversations?per_page=100"),
            _response().with_record(_record().with_id(101)).build(),
        )
        http_mocker.get(
            HttpRequest(f"https://{_DOMAIN}/api/v2/tickets/22/conversations?per_page=100"),
            _response().with_record(_record().with_id(202)).build(),
        )

        output = _read(
            sync_mode=SyncMode.full_refresh,
            config_builder=ConfigBuilder().domain(_DOMAIN).start_date(datetime(2022, 1, 1)),
        )

        assert [record["ticket_updated_at"] for record in _record_data(output)] == [first_updated_at, second_updated_at]


@pytest.mark.parametrize(
    "state",
    [
        {"use_global_cursor": True, "state": {"ticket_updated_at": "2024-05-01T00:00:00Z"}},
        {"__ab_no_cursor_state_message": True},
    ],
)
def test_state_without_parent_state_and_full_refresh_sentinel_use_start_date(state: Dict[str, Any]) -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(HttpRequest(_TICKETS_URL), _ticket_response([_ticket(11, "2024-05-01T00:00:00Z")]))
        http_mocker.get(
            HttpRequest(f"https://{_DOMAIN}/api/v2/tickets/11/conversations?per_page=100"),
            _response().with_record(_record().with_id(101)).build(),
        )

        output = _read(
            config_builder=ConfigBuilder().domain(_DOMAIN).start_date(datetime(2022, 1, 1)),
            state_builder=StateBuilder().with_stream_state("conversations", state),
        )

        assert [record["ticket_updated_at"] for record in _record_data(output)] == ["2024-05-01T00:00:00Z"]
