#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Extra


class ValueRange(BaseModel):
    class Config:
        extra = Extra.allow

    values: Optional[list[list[str]]] = None


class SpreadsheetValues(BaseModel):
    class Config:
        extra = Extra.allow

    spreadsheetId: str
    valueRanges: list[ValueRange]
