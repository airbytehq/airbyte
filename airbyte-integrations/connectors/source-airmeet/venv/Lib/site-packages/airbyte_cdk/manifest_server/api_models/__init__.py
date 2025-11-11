"""
API Models for the Manifest Server Service.

This package contains all Pydantic models used for API requests and responses.
"""

from .dicts import ConnectorConfig, Manifest
from .manifest import (
    CheckRequest,
    CheckResponse,
    DiscoverRequest,
    DiscoverResponse,
    ErrorResponse,
    FullResolveRequest,
    ManifestResponse,
    RequestContext,
    ResolveRequest,
    StreamTestReadRequest,
)
from .stream import (
    AuxiliaryRequest,
    HttpRequest,
    HttpResponse,
    LogMessage,
    StreamReadPages,
    StreamReadResponse,
    StreamReadSlices,
)

__all__ = [
    # Typed Dicts
    "ConnectorConfig",
    "Manifest",
    # Manifest request/response models
    "RequestContext",
    "FullResolveRequest",
    "ManifestResponse",
    "StreamTestReadRequest",
    "ResolveRequest",
    "CheckRequest",
    "CheckResponse",
    "DiscoverRequest",
    "DiscoverResponse",
    "ErrorResponse",
    # Stream models
    "AuxiliaryRequest",
    "HttpRequest",
    "HttpResponse",
    "LogMessage",
    "StreamReadResponse",
    "StreamReadPages",
    "StreamReadSlices",
]
