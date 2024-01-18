"""Airbyte Instance, either on Cloud, OSS, or Enterprise."""

from __future__ import annotations

import os
from abc import ABC

from pydantic import BaseModel, validator


class AirbyteInstanceBase(ABC, BaseModel):
    """An Airbyte instance."""

    api_key: str | None = None
    """The API key to use for authentication."""

    @validator("api_key", pre=True, always=True)
    def validate_api_key(self, value: str) -> str:
        """Check the API key.

        If not provided, use the environment variable.
        If no value is available in either method, raise an error.
        """
        if not value:
            value = os.getenv("AIRBYTE_API_KEY")
            if not value:
                raise ValueError(
                    "API key is not provided and AIRBYTE_API_KEY environment variable is not set"
                )
        return value

    api_root: str
    """The Airbyte API root URL."""

    web_root: str
    """The Airbyte web root URL."""


class AirbyteCloud(AirbyteInstanceBase):
    """An Airbyte Cloud instance."""

    api_root: str = "https://api.airbyte.io/v1"
    """The Airbyte API root URL."""

    web_root: str = "https://cloud.airbyte.io"
    """The Airbyte web root URL."""


class AirbyteSelfManaged(AirbyteInstanceBase):
    """An Airbyte OSS or Enterprise instance."""
