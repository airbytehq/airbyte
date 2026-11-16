# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any
from urllib.parse import urlsplit

from conftest import get_source
from freezegun import freeze_time

from airbyte_cdk.models import AirbyteStateMessage, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker

from .config import ConfigBuilder


_NOW = "2026-06-01T00:00:00Z"


def read_streams(
    stream_names: list[str],
    sync_mode: SyncMode,
    config: dict[str, Any] | None = None,
    state: list[AirbyteStateMessage] | None = None,
) -> EntrypointOutput:
    """Read the streams on a frozen clock. The caller mocks the HTTP responses. A sync that reports an error fails the test."""
    config = config or ConfigBuilder().build()
    catalog_builder = CatalogBuilder()
    for stream_name in stream_names:
        catalog_builder.with_stream(stream_name, sync_mode)
    catalog = catalog_builder.build()
    with freeze_time(_NOW):
        output = read(get_source(config, catalog, state), config, catalog, state)
    if output.errors:
        # Raised, not asserted: `HttpMocker` replaces a failed assertion with its own report of the mock that was
        # not called, and the request that had no mock would be lost.
        raise RuntimeError("\n".join(f"{error.trace.error.message} {error.trace.error.internal_message}" for error in output.errors))
    return output


def read_stream(
    stream_name: str,
    sync_mode: SyncMode = SyncMode.full_refresh,
    config: dict[str, Any] | None = None,
    state: list[AirbyteStateMessage] | None = None,
) -> EntrypointOutput:
    return read_streams([stream_name], sync_mode, config, state)


def record_ids(output: EntrypointOutput) -> list[Any]:
    return [message.record.data["id"] for message in output.records]


def stream_state(output: EntrypointOutput) -> dict[str, Any]:
    """The last state the read saved."""
    return dict(output.most_recent_state.stream_state.__dict__)


def sent_queries(http_mocker: HttpMocker) -> list[str]:
    """The query string of each data request as it went out, in the order sent."""
    # `HttpMocker` has no public view of the requests it saw.
    return [urlsplit(request.url).query for request in http_mocker._mocker.request_history if request.method == "GET"]
