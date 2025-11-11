"""
Common API models shared across different endpoints.
"""

from pydantic import BaseModel, ConfigDict


class Manifest(BaseModel):
    """Base manifest model. Allows client generation to replace with proper JsonNode types."""

    model_config = ConfigDict(extra="allow")


class ConnectorConfig(BaseModel):
    """Base connector configuration model. Allows client generation to replace with proper JsonNode types."""

    model_config = ConfigDict(extra="allow")
