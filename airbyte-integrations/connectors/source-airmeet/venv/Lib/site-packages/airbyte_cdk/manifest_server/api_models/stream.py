"""
Stream-related API models.

These models define the structure for stream reading operations and responses.
They accurately reflect the runtime types returned by the CDK, particularly
fixing type mismatches like slice_descriptor being a string rather than an object.
"""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel


class HttpRequest(BaseModel):
    """HTTP request details."""

    url: str
    headers: Optional[Dict[str, Any]]
    http_method: str
    body: Optional[str] = None


class HttpResponse(BaseModel):
    """HTTP response details."""

    status: int
    body: Optional[str] = None
    headers: Optional[Dict[str, Any]] = None


class LogMessage(BaseModel):
    """Log message from stream processing."""

    message: str
    level: str
    internal_message: Optional[str] = None
    stacktrace: Optional[str] = None


class AuxiliaryRequest(BaseModel):
    """Auxiliary HTTP request made during stream processing."""

    title: str
    type: str
    description: str
    request: HttpRequest
    response: HttpResponse


class StreamReadPages(BaseModel):
    """Pages of data read from a stream slice."""

    records: List[object]
    request: Optional[HttpRequest] = None
    response: Optional[HttpResponse] = None


class StreamReadSlices(BaseModel):
    """Slices of data read from a stream."""

    pages: List[StreamReadPages]
    slice_descriptor: Optional[Union[Dict[str, Any], str]]  # We're seeing strings at runtime
    state: Optional[List[Dict[str, Any]]] = None
    auxiliary_requests: Optional[List[AuxiliaryRequest]] = None


class StreamReadResponse(BaseModel):
    """Complete stream read response with properly typed fields."""

    logs: List[LogMessage]
    slices: List[StreamReadSlices]
    test_read_limit_reached: bool
    auxiliary_requests: List[AuxiliaryRequest]
    inferred_schema: Optional[Dict[str, Any]]
    inferred_datetime_formats: Optional[Dict[str, str]]
    latest_config_update: Optional[Dict[str, Any]]
