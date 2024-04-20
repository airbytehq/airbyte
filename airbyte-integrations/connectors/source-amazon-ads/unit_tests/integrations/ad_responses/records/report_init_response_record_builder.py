# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Any, Dict, Optional, Union

from airbyte_cdk.test.mock_http.response_builder import FieldPath, NestedPath, Path, RecordBuilder, find_template


class ReportInitResponseRecordBuilder(RecordBuilder):
    @classmethod
    def init_response_record(cls) -> "ReportInitResponseRecordBuilder":
        return cls(
            find_template("report_init_response", __file__),
            id_path=FieldPath("reportId"),
            status_path=FieldPath("status"),
            cursor_path=None
        )

    def __init__(
        self,
        template: Dict[str, Any],
        id_path: Optional[Path] = None,
        status_path: Optional[Path] = None,
        cursor_path: Optional[Union[FieldPath, NestedPath]] = None
    ):
        super().__init__(template, id_path, cursor_path)
        self._status_path = status_path

    def with_status(self, status: str) -> "ReportInitResponseRecordBuilder":
        self._set_field("status", self._status_path, status)
        return self
