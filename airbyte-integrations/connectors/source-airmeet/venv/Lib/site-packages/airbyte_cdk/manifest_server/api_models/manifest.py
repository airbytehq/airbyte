"""
Manifest-related API models.

These models define the request and response structures for manifest operations
like reading, resolving, and full resolution.
"""

from typing import Any, List, Optional

from airbyte_protocol_dataclasses.models import AirbyteCatalog
from pydantic import BaseModel, Field

from .dicts import ConnectorConfig, Manifest


class RequestContext(BaseModel):
    """Optional context information for tracing and observability."""

    workspace_id: Optional[str] = None
    project_id: Optional[str] = None


class StreamTestReadRequest(BaseModel):
    """Request to test read from a specific stream."""

    manifest: Manifest
    config: ConnectorConfig
    stream_name: str
    state: List[Any] = Field(default_factory=list)
    custom_components_code: Optional[str] = None
    record_limit: int = Field(default=100, ge=1, le=5000)
    page_limit: int = Field(default=5, ge=1, le=20)
    slice_limit: int = Field(default=5, ge=1, le=20)
    context: Optional[RequestContext] = None


class CheckRequest(BaseModel):
    """Request to check a manifest."""

    manifest: Manifest
    config: ConnectorConfig
    context: Optional[RequestContext] = None


class CheckResponse(BaseModel):
    """Response to check a manifest."""

    success: bool
    message: Optional[str] = None


class DiscoverRequest(BaseModel):
    """Request to discover a manifest."""

    manifest: Manifest
    config: ConnectorConfig
    context: Optional[RequestContext] = None


class DiscoverResponse(BaseModel):
    """Response to discover a manifest."""

    catalog: AirbyteCatalog


class ResolveRequest(BaseModel):
    """Request to resolve a manifest."""

    manifest: Manifest
    context: Optional[RequestContext] = None


class ManifestResponse(BaseModel):
    """Response containing a manifest."""

    manifest: Manifest


class FullResolveRequest(BaseModel):
    """Request to fully resolve a manifest."""

    manifest: Manifest
    config: ConnectorConfig
    stream_limit: int = Field(default=100, ge=1, le=100)
    context: Optional[RequestContext] = None


class ErrorResponse(BaseModel):
    """Error response for API requests."""

    detail: str
