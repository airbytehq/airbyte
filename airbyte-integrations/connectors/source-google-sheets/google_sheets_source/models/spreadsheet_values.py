#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Extra


class ValueRange(BaseModel):
    class Config:
        extra = Extra.allow

    values: Optional[List[List[str]]] = None


class SpreadsheetValues(BaseModel):
    class Config:
        extra = Extra.allow

    spreadsheetId: str
    valueRanges: List[ValueRange]
