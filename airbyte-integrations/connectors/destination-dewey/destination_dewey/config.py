#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class DeweyConfig(BaseModel):
    api_key: str = Field(
        ...,
        title="API Key",
        description="A Dewey project API key. Use a `dwy_test_...` key for sandbox runs and `dwy_live_...` for production.",
        airbyte_secret=True,
        order=0,
        group="auth",
    )
    base_url: str = Field(
        default="https://api.meetdewey.com/v1",
        title="Base URL",
        description="Dewey API base URL. Override only for self-hosted deployments.",
        order=1,
        group="auth",
    )

    stream_collections: Dict[str, str] = Field(
        default_factory=dict,
        title="Stream → Collection Mapping",
        description=(
            "Maps each Airbyte stream name to a Dewey collection ID. The map key is the stream name "
            "(prefix with `<namespace>__` if your source uses namespaces). Streams not listed here are "
            "skipped unless `auto_create_collections` is enabled."
        ),
        examples=[{"products": "col_abc123", "blog_posts": "col_def456"}],
        order=2,
        group="routing",
    )
    auto_create_collections: bool = Field(
        default=False,
        title="Auto-create Collections",
        description=(
            "If enabled, the destination will create a Dewey collection for any stream that has no entry "
            "in `stream_collections`. The collection name will be `airbyte_<namespace>__<stream>`."
        ),
        order=3,
        group="routing",
    )

    text_fields: Optional[List[str]] = Field(
        default=[],
        title="Text Fields",
        description=(
            "Dot-path fields to include as the indexed body of each document. If empty, the entire record "
            "is uploaded as JSON. Use `users.*.name` to pull values from arrays."
        ),
        always_show=True,
        examples=["title", "body", "user.name", "users.*.name"],
        order=4,
        group="document",
    )
    title_field: Optional[str] = Field(
        default="",
        title="Title Field",
        description=(
            "Dot-path field used as the document filename in Dewey. Falls back to the record's primary key, "
            "or a UUID when neither is set."
        ),
        always_show=True,
        examples=["title", "name"],
        order=5,
        group="document",
    )
    metadata_fields: Optional[List[str]] = Field(
        default=[],
        title="Metadata Fields",
        description=(
            "Dot-path fields to lift into Dewey's per-document `metadata` (filterable at query time). " "Non-existing fields are ignored."
        ),
        always_show=True,
        examples=["author", "tags", "published_at"],
        order=6,
        group="document",
    )

    parallelize: bool = Field(
        default=False,
        title="Parallelize",
        description="Upload documents to Dewey in parallel (up to 8 concurrent uploads).",
        always_show=True,
        order=7,
        group="performance",
    )
    flush_interval: int = Field(
        default=100,
        title="Flush Interval",
        description="Number of records to buffer before flushing to Dewey.",
        ge=1,
        le=1000,
        order=8,
        group="performance",
    )

    class Config:
        title = "Dewey Destination Config"
        schema_extra = {
            "description": "Configuration to ingest records into a Dewey project.",
            "groups": [
                {"id": "auth", "title": "Authentication"},
                {"id": "routing", "title": "Stream Routing"},
                {"id": "document", "title": "Document Shape"},
                {"id": "performance", "title": "Performance"},
            ],
        }
