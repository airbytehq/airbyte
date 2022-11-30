#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from functools import cached_property
from typing import Any, Dict, Iterable, Mapping, Optional, Tuple

import smartsheet


class SmartSheetAPIWrapper:
    def __init__(self, config: Mapping[str, Any]):
        self._spreadsheet_id = config["spreadsheet_id"]
        self._access_token = config["access_token"]
        api_client = smartsheet.Smartsheet(self._access_token)
        api_client.errors_as_exceptions(True)
        # each call to `Sheets` makes a new instance, so we save it here to make no more new objects
        self._get_sheet = api_client.Sheets.get_sheet
        self._data = None

    def _fetch_sheet(self, from_dt: Optional[str] = None) -> None:
        kwargs = {"rows_modified_since": from_dt}
        if not from_dt:
            kwargs["page_size"] = 1
        self._data = self._get_sheet(self._spreadsheet_id, **kwargs)

    @staticmethod
    def _column_to_property(column_type: str) -> Dict[str, any]:
        type_mapping = {
            "TEXT_NUMBER": {"type": "string"},
            "DATE": {"type": "string", "format": "date"},
            "DATETIME": {"type": "string", "format": "date-time"},
        }
        return type_mapping.get(column_type, {"type": "string"})

    def _construct_record(self, row: smartsheet.models.Row) -> Dict[str, str]:
        values_column_map = {cell.column_id: str(cell.value or "") for cell in row.cells}
        record = {column.title: values_column_map[column.id] for column in self.data.columns}
        record["modifiedAt"] = row.modified_at.isoformat()
        return record

    @property
    def data(self) -> smartsheet.models.Row:
        if not self._data:
            self._fetch_sheet()
        return self._data

    @property
    def name(self) -> str:
        return self.data.name

    @property
    def row_count(self) -> int:
        return len(self.data.rows)

    @cached_property
    def primary_key(self) -> str:
        for column in self.data.columns:
            if column.primary:
                return column.title

    @cached_property
    def json_schema(self) -> Dict[str, Any]:
        column_info = {column.title: self._column_to_property(column.type.value) for column in self.data.columns}
        column_info["modifiedAt"] = {"type": "string", "format": "date-time"}  # add cursor field explicitly
        json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": column_info,
        }
        return json_schema

    def read_records(self, from_dt: str) -> Iterable[Dict[str, str]]:
        self._fetch_sheet(from_dt)
        for row in self.data.rows:
            yield self._construct_record(row)

    def check_connection(self, logger: logging.Logger) -> Tuple[bool, Optional[str]]:
        try:
            _ = self.data
        except smartsheet.exceptions.ApiError as e:
            err = e.error.result
            code = 404 if err.code == 1006 else err.code
            reason = f"{err.name}: {code} - {err.message} | Check your spreadsheet ID."
            logger.error(reason)
            return False, reason
        except Exception as e:
            reason = str(e)
            logger.error(reason)
            return False, reason
        return True, None
