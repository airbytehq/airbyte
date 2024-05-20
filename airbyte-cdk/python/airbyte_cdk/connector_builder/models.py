#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class HttpResponse:
    status: int
    body: Optional[str] = None
    headers: Optional[Dict[str, Any]] = None


@dataclass
class HttpRequest:
    url: str
    headers: Optional[Dict[str, Any]]
    http_method: str
    body: Optional[str] = None


@dataclass
class StreamReadPages:
    records: List[object]
    request: Optional[HttpRequest] = None
    response: Optional[HttpResponse] = None


@dataclass
class StreamReadSlices:
    pages: List[StreamReadPages]
    slice_descriptor: Optional[Dict[str, Any]]
    state: Optional[List[Dict[str, Any]]] = None


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
class StreamRead(object):
    logs: List[LogMessage]
    slices: List[StreamReadSlices]
    test_read_limit_reached: bool
    auxiliary_requests: List[AuxiliaryRequest]
    inferred_schema: Optional[Dict[str, Any]]
    inferred_datetime_formats: Optional[Dict[str, str]]
    latest_config_update: Optional[Dict[str, Any]]


@dataclass
class StreamReadRequestBody:
    manifest: Dict[str, Any]
    stream: str
    config: Dict[str, Any]
    state: Optional[Dict[str, Any]]
    record_limit: Optional[int]
