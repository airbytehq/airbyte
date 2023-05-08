#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class HttpResponse:
    status: int
    body: Optional[str] = None
    headers: Optional[Dict[str, Any]] = None


@dataclass
class HttpRequest:
    url: str
    parameters: Optional[Dict[str, Any]]
    body: Optional[Dict[str, Any]]
    headers: Optional[Dict[str, Any]]
    http_method: str


@dataclass
class StreamReadPages:
    records: List[object]
    request: Optional[HttpRequest] = None
    response: Optional[HttpResponse] = None


@dataclass
class StreamReadSlicesInnerPagesInner:
    records: List[object]
    request: Optional[HttpRequest]
    response: Optional[HttpResponse]


@dataclass
class StreamReadSlicesInnerSliceDescriptor:
    start_datetime: Optional[datetime]
    list_item: Optional[str]


@dataclass
class StreamReadSlicesInner:
    pages: List[StreamReadSlicesInnerPagesInner]
    slice_descriptor: Optional[StreamReadSlicesInnerSliceDescriptor]
    state: Optional[Dict[str, Any]]


@dataclass
class LogMessage:
    message: str
    level: str


@dataclass
class StreamRead(object):
    logs: List[LogMessage]
    slices: List[StreamReadSlicesInner]
    test_read_limit_reached: bool
    inferred_schema: Optional[Dict[str, Any]]


@dataclass
class StreamReadRequestBody:
    manifest: Dict[str, Any]
    stream: str
    config: Dict[str, Any]
    state: Optional[Dict[str, Any]]
    record_limit: Optional[int]


@dataclass
class StreamReadSliceDescriptor:
    start_datetime: Optional[datetime] = None
    list_item: Optional[str] = None


@dataclass
class StreamReadSlices:
    pages: List[StreamReadPages]
    slice_descriptor: Optional[StreamReadSliceDescriptor] = None
    state: Optional[Dict[str, Any]] = None
