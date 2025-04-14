import logging
from typing import List, Optional, Dict, Any
import json
from pydantic import BaseModel, Field, field_validator


logging.basicConfig(level=logging.INFO)


class RagieConfig(BaseModel):
    class Config:
        title = "Ragie Destination Config"

    api_key: str = Field(
        title="API Key",
        description="API Key for Ragie.ai.",
        airbyte_secret=True,
        order=0
    )

    content_fields: List[str] = Field(
        title="Content Fields",
        description="(Optional) List of fields from the record to use as the main document content. If empty, the entire record is used. Use dot notation for nested fields (e.g., 'user.profile').",
        default=[],
        order=1,
        examples=["description", "message", "details.notes"],
        always_show=True
    )

    metadata_fields: List[str] = Field(
        title="Metadata Fields",
        description="(Optional) List of fields from the record to store as metadata. If empty, no record fields are added as metadata. Use dot notation.",
        default=[],
        order=2,
        examples=["user.id", "user.email", "user.profile.created_at"],
        always_show=True
    )

    partition: Optional[str] = Field(
        title="Partition Name",
        description="(Optional) Name of the partition (index/dataset) to write data into. Must be lowercase alphanumeric with '-' or '_'. If empty, uses default.",
        default="",
        pattern=r"^[a-z0-9_\-]*$",
        order=3,
        always_show=True
    )

    processing_mode: str = Field(
        title="Mode",
        description="Processing mode for ingestion ('fast' or 'hi-res').",
        default="fast",
        enum=["fast", "hi-res"],
        order=3,
        always_show=True
    )

    document_name_field: Optional[str] = Field(
        title="Document Name Field",
        description="(Optional) Field from the record to use as the document name. If empty or field not found, a name is auto-generated.",
        default="",
        order=4,
        always_show=True
    )

    metadata_static: Optional[Dict[str, Any]] = Field(
        title="Static Metadata (JSON)",
        description="(Optional) Static key-value pairs (as a JSON object) to add to every document's metadata.",
        examples=[
            '{"source": "airbyte", "ingestion_time": "2023-10-01T12:00:00Z"}'
        ],
        order=6,
        default=''
    )

    external_id_field: Optional[str] = Field(
        title="External ID Field",
        description="(Optional) Field from the record to use as the unique 'external_id' for Ragie documents.",
        default="",
        order=8
    )

    api_url: str = Field(
        title="API URL",
        description="URL for the Ragie API. Defaults to https://api.ragie.ai",
        default="https://api.ragie.ai",
        order=9
    )


    @field_validator('metadata_static')
    def ensure_metadata_dict(cls, v):
        if isinstance(v, str): 
            if not v:
                return {}
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                raise ValueError("Static Metadata must be a valid JSON object string.")
        return v if v is not None else {}
