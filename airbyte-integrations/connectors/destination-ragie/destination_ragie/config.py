# ========================================================================
# FILE: config.py (Concept - often implemented within destination.py spec)
# ========================================================================
import logging
from typing import List, Optional, Dict, Any
import json
from pydantic import BaseModel, Field, validator, Json

# Configure logging for CDK usage
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

    api_url: str = Field(
        title="API URL",
        description="URL for the Ragie API. Defaults to https://api.ragie.ai",
        default="https://api.ragie.ai",
        order=1
    )

    partition: Optional[str] = Field(
        title="Partition Name",
        description="(Optional) Name of the partition (index/dataset) to write data into. Must be lowercase alphanumeric with '-' or '_'. If empty, uses default.",
        default="",
        pattern=r"^[a-z0-9_\-]*$", # Allow empty or matching pattern
        order=2
    )

    processing_mode: str = Field(
        title="Processing Mode",
        description="Processing mode for ingestion ('fast' or 'hi-res').",
        default="fast",
        enum=["fast", "hi-res"],
        order=3
    )

    content_fields: Optional[List[str]] = Field(
        title="Content Fields",
        description="(Optional) List of fields from the record to use as the main document content. If empty, the entire record is used. Use dot notation for nested fields (e.g., 'user.profile').",
        default=[],
        order=4
    )

    metadata_fields: Optional[List[str]] = Field(
        title="Metadata Fields",
        description="(Optional) List of fields from the record to store as metadata. If empty, no record fields are added as metadata. Use dot notation.",
        default=[],
        order=5
    )

    metadata_static: Optional[Dict[str, Any]] = Field(
        title="Static Metadata (JSON)",
        description="(Optional) Static key-value pairs (as a JSON object) to add to every document's metadata.",
        default={},
        order=6
    )

    document_name_field: Optional[str] = Field(
        title="Document Name Field",
        description="(Optional) Field from the record to use as the document name. If empty or field not found, a name is auto-generated.",
        default="",
        order=7
    )

    external_id_field: Optional[str] = Field(
        title="External ID Field",
        description="(Optional) Field from the record to use as the unique 'external_id' for Ragie documents. Required for 'append-dedup' mode if primary keys are not defined.",
        default="",
        order=8
    )

    batch_size: int = Field(
        title="Batch Size",
        description="Number of records to batch together before sending to Ragie.",
        default=100,
        ge=1,
        le=1000, # Adjust max based on Ragie limits / testing
        order=9
    )

    # Add validator if metadata_static needs to accept JSON string from UI
    @validator('metadata_static', pre=True, always=True)
    def ensure_metadata_dict(cls, v):
        if isinstance(v, str):
            if not v:
                return {}
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                raise ValueError("Static Metadata must be a valid JSON object string.")
        return v if v is not None else {}
