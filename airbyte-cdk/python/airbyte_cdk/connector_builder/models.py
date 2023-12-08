#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class HttpResponse:
    status: int
    body: Optional[str] = None
    headers: Optional[dict[str, Any]] = None


@dataclass
class HttpRequest:
    url: str
    parameters: Optional[dict[str, Any]]
    headers: Optional[dict[str, Any]]
    http_method: str
    body: Optional[str] = None


@dataclass
class StreamReadPages:
    records: list[object]
    request: Optional[HttpRequest] = None
    response: Optional[HttpResponse] = None


@dataclass
class StreamReadSlices:
    pages: list[StreamReadPages]
    slice_descriptor: Optional[dict[str, Any]]
    state: Optional[dict[str, Any]] = None


@dataclass
class LogMessage:
    message: str
    level: str


@dataclass
class AuxiliaryRequest:
    title: str
    description: str
    request: HttpRequest
    response: HttpResponse


@dataclass
class StreamRead:
    logs: list[LogMessage]
    slices: list[StreamReadSlices]
    test_read_limit_reached: bool
    auxiliary_requests: list[AuxiliaryRequest]
    inferred_schema: Optional[dict[str, Any]]
    inferred_datetime_formats: Optional[dict[str, str]]
    latest_config_update: Optional[dict[str, Any]]


@dataclass
class StreamReadRequestBody:
    manifest: dict[str, Any]
    stream: str
    config: dict[str, Any]
    state: Optional[dict[str, Any]]
    record_limit: Optional[int]
