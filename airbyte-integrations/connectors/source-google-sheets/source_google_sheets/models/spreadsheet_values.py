#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from __future__ import annotations

from pydantic import BaseModel, Extra


class ValueRange(BaseModel):
    class Config:
        extra = Extra.allow

    values: list[list[str]] | None = None


class SpreadsheetValues(BaseModel):
    class Config:
        extra = Extra.allow

    spreadsheetId: str
    valueRanges: list[ValueRange]
