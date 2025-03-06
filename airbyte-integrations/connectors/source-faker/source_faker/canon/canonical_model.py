# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from abc import abstractmethod
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class TimestampedModel(BaseModel):
    created_at: datetime | None
    updated_at: datetime | None


class CanonicalModel(TimestampedModel):
    id: str
    deleted_at: datetime | None
    additional_properties: dict[str, Any]

    @classmethod
    @abstractmethod
    def stream_name(cls) -> str:
        pass
