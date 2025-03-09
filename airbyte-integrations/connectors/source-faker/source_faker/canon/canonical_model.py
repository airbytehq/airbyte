# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from abc import abstractmethod
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class TimestampedModel(BaseModel):
    created_at: datetime | None = Field(default=None, description="The date and time the record was created.")
    updated_at: datetime | None = Field(default=None, description="The date and time the record was last updated.")


class CanonicalModel(TimestampedModel):
    id: str = Field(description="The unique identifier for the record.")
    deleted_at: datetime | None = Field(default=None, description="The date and time the record was deleted.")
    additional_properties: dict[str, Any] = Field(default_factory=dict, description="Additional properties for the record.")

    @classmethod
    @abstractmethod
    def stream_name(cls) -> str:
        pass
