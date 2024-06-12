# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Any, Dict, Optional, Union

from airbyte_cdk.test.mock_http.response_builder import FieldPath, NestedPath, Path, RecordBuilder, find_template


class ReportCheckStatusRecordBuilder(RecordBuilder):
    @classmethod
    def status_record(cls) -> "ReportCheckStatusRecordBuilder":
        return cls(
            find_template("report_status_response", __file__),
            id_path=None,
            status_path=FieldPath("status"),
            url_path=FieldPath("url")
        )

    def __init__(
        self,
        template: Dict[str, Any],
        id_path: Optional[Path] = None,
        status_path: Optional[Path] = None,
        url_path: Optional[Path] = None,
        cursor_path: Optional[Union[FieldPath, NestedPath]] = None
    ):
        super().__init__(template, id_path, cursor_path)
        self._status_path = status_path
        self._url_path = url_path

    def with_status(self, status: str) -> "ReportCheckStatusRecordBuilder":
        self._set_field("status", self._status_path, status)
        return self

    def with_url(self, url: str) -> "ReportCheckStatusRecordBuilder":
        self._set_field("status", self._url_path, url)
        return self
