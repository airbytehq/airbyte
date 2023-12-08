#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from __future__ import annotations

from typing import Optional

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

    values: Optional[list[CellData]] = None


class GridData(BaseModel):
    class Config:
        extra = Extra.allow

    rowData: Optional[list[RowData]] = None


class Sheet(BaseModel):
    class Config:
        extra = Extra.allow

    data: Optional[list[GridData]] = None
    properties: Optional[SheetProperties] = None


class Spreadsheet(BaseModel):
    class Config:
        extra = Extra.allow

    spreadsheetId: str
    sheets: list[Sheet]
    properties: Optional[SpreadsheetProperties] = None
