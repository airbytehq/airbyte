# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Any, Dict, List

from .sheet_builder import SheetBuilder


class SpreadsheetBuilder:
    @classmethod
    def from_list_of_records(cls, spreadsheet_id: str, sheet_title: str, records: List[Dict[str, str]]) -> "SpreadsheetBuilder":
        builder = SpreadsheetBuilder(spreadsheet_id)
        builder.with_sheet(SheetBuilder(sheet_title).with_records(records))
        return builder

    def __init__(self, spreadsheet_id: str) -> None:
        self._spreadsheet = {
            "spreadsheetId": spreadsheet_id,
            "sheets": [],
        }

    def with_sheet(self, sheet: SheetBuilder) -> "SpreadsheetBuilder":
        self._spreadsheet["sheets"].append(sheet.build())
        return self

    def build(self) -> Any:
        return self._spreadsheet
