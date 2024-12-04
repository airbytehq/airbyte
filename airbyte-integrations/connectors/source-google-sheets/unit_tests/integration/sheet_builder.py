# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Any, Dict, Iterable, List, Mapping, Optional


class SheetBuilder:
    @classmethod
    def empty(cls, title: str) -> "SheetBuilder":
        builder = SheetBuilder(title)
        return builder

    def __init__(self, title: str) -> None:
        self._sheet = {
            "properties": {
                "title": title,
                "gridProperties": {
                    "rowCount": 0
                },
                "sheetType": "GRID",
            }
        }

    def with_records(self, records: List[Dict[str, str]]) -> "SheetBuilder":
        fields = list(records[0].keys())
        fields.sort()

        rows = []
        rows.append(fields)
        for record in records:
            if record.keys() != set(fields):
                raise ValueError("Records do not have all the same columns")
            rows.append([record[key] for key in sorted(record.keys())])

        self.with_data(rows)
        return self

    def with_data(self, rows: List[List[str]]) -> "SheetBuilder":
        self._sheet["data"] = [{"rowData": [self._create_row(row) for row in rows]}]
        self._sheet["properties"]["gridProperties"]["rowCount"] = len(rows)
        return self

    def _create_row(self, values: List[str]) -> Dict[str, List[Dict[str, str]]]:
        return {"values": [{"formattedValue": value} for value in values]}

    def with_properties(self, properties: Dict[str, str]) -> "SheetBuilder":
        self._sheet["properties"] = properties
        return self

    def with_sheet_type(self, sheet_type: str) -> "SheetBuilder":
        self._sheet["properties"]["sheetType"] = sheet_type
        return self

    def build(self) -> Any:
        return self._sheet
