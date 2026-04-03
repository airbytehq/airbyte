# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Any, Dict

from pydantic import BaseModel, Field


class StarRocksConfig(BaseModel):
    """Configuration for StarRocks destination connector."""

    host: str = Field(..., description="StarRocks FE hostname")
    port: int = Field(default=9030, description="MySQL protocol port")
    http_port: int = Field(default=8030, description="Stream Load API port")
    username: str = Field(..., description="Authentication username")
    password: str = Field(default="", description="Authentication password")
    database: str = Field(..., description="Target database name")
    ssl: bool = Field(default=False, description="Enable SSL/TLS encryption")
    loading_mode: Dict[str, Any] = Field(
        default={"mode": "typed"},
        description="Loading mode configuration"
    )
