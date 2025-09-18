# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MockAPIConfig(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"examples": [{"api_url": "https://68cc13e1716562cf50764f2b.mockapi.io/api/v1", "batch_size": 50, "timeout": 30}]}
    )

    api_url: str = Field(..., description="MockAPI endpoint URL", title="API URL")

    batch_size: int = Field(default=100, description="Number of records to process in each batch", title="Batch Size", ge=1, le=1000)

    timeout: int = Field(default=30, description="Request timeout in seconds", title="Timeout", ge=1, le=300)

    @field_validator("api_url")
    @classmethod
    def validate_api_url(cls, v):
        if not v.startswith(("http://", "https://")):
            raise ValueError("API URL must start with http:// or https://")
        return v.rstrip("/")


def get_config_from_dict(config_dict: Dict[str, Any]) -> MockAPIConfig:
    """Convert dictionary config to MockAPIConfig object"""
    return MockAPIConfig(**config_dict)
