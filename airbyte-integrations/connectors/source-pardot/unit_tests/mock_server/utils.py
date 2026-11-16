# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any
from urllib.parse import urlsplit

from conftest import get_source

from airbyte_cdk.models import AirbyteErrorTraceMessage, AirbyteStateMessage, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker

from .config import ConfigBuilder


def read_streams(
    stream_names: list[str],
    sync_mode: SyncMode,
    config: dict[str, Any] | None = None,
    state: list[AirbyteStateMessage] | None = None,
    expecting_error: bool = False,
) -> EntrypointOutput:
    """Read the streams. The caller mocks the HTTP responses. Unless an error is expected, a sync that reports one fails the test."""
    config = config or ConfigBuilder().build()
    catalog_builder = CatalogBuilder()
    for stream_name in stream_names:
        catalog_builder.with_stream(stream_name, sync_mode)
    catalog = catalog_builder.build()
    output = read(get_source(config, catalog, state), config, catalog, state, expecting_exception=expecting_error)
    if output.errors and not expecting_error:
        # Raised, not asserted: `HttpMocker` replaces a failed assertion with its own report of the mock that was
        # not called, and the request that had no mock would be lost.
        raise RuntimeError("\n".join(f"{error.trace.error.message} {error.trace.error.internal_message}" for error in output.errors))
    return output


def read_stream(
    stream_name: str,
    sync_mode: SyncMode = SyncMode.full_refresh,
    config: dict[str, Any] | None = None,
    state: list[AirbyteStateMessage] | None = None,
    expecting_error: bool = False,
) -> EntrypointOutput:
    return read_streams([stream_name], sync_mode, config, state, expecting_error)


def stream_error(output: EntrypointOutput) -> AirbyteErrorTraceMessage:
    """The error a stream reported. The summary error that closes a failed sync comes after it."""
    assert output.errors, "expected the sync to report an error"
    return output.errors[0].trace.error


def record_ids(output: EntrypointOutput) -> list[Any]:
    return [message.record.data["id"] for message in output.records]


def stream_state(output: EntrypointOutput) -> dict[str, Any]:
    """The last state the read saved."""
    return dict(output.most_recent_state.stream_state.__dict__)


def sent_queries(http_mocker: HttpMocker) -> list[str]:
    """The query string of each data request as it went out, in the order sent."""
    # `HttpMocker` has no public view of the requests it saw.
    return [urlsplit(request.url).query for request in http_mocker._mocker.request_history if request.method == "GET"]
