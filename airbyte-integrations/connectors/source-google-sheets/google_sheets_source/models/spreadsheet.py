#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Extra


class SpreadsheetProperties(BaseModel):
    class Config:
        extra = Extra.allow

    title: Optional[str] = None


class SheetProperties(BaseModel):
    class Config:
        extra = Extra.allow

    title: Optional[str] = None


class CellData(BaseModel):
    class Config:
        extra = Extra.allow

    formattedValue: Optional[str] = None


class RowData(BaseModel):
    class Config:
        extra = Extra.allow

    values: Optional[List[CellData]] = None


class GridData(BaseModel):
    class Config:
        extra = Extra.allow

    rowData: Optional[List[RowData]] = None


class Sheet(BaseModel):
    class Config:
        extra = Extra.allow

    data: Optional[List[GridData]] = None
    properties: Optional[SheetProperties] = None


class Spreadsheet(BaseModel):
    class Config:
        extra = Extra.allow

    spreadsheetId: str
    sheets: List[Sheet]
    properties: Optional[SpreadsheetProperties] = None
