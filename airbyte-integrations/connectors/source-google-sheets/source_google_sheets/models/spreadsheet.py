#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from __future__ import annotations

from pydantic import BaseModel, Extra


class SpreadsheetProperties(BaseModel):
    class Config:
        extra = Extra.allow

    title: str | None = None


class SheetProperties(BaseModel):
    class Config:
        extra = Extra.allow

    title: str | None = None


class CellData(BaseModel):
    class Config:
        extra = Extra.allow

    formattedValue: str | None = None


class RowData(BaseModel):
    class Config:
        extra = Extra.allow

    values: list[CellData] | None = None


class GridData(BaseModel):
    class Config:
        extra = Extra.allow

    rowData: list[RowData] | None = None


class Sheet(BaseModel):
    class Config:
        extra = Extra.allow

    data: list[GridData] | None = None
    properties: SheetProperties | None = None


class Spreadsheet(BaseModel):
    class Config:
        extra = Extra.allow

    spreadsheetId: str
    sheets: list[Sheet]
    properties: SpreadsheetProperties | None = None
