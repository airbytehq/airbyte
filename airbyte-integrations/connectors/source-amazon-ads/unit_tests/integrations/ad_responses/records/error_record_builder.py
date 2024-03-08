# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Any, Dict, Optional, Union

from airbyte_cdk.test.mock_http.response_builder import FieldPath, NestedPath, Path, RecordBuilder, find_template


class ErrorRecordBuilder(RecordBuilder):
    def __init__(
        self,
        template: Dict[str, Any],
        id_path: Optional[Path] = None,
        cursor_path: Optional[Union[FieldPath, NestedPath]] = None,
        error_message_path: Optional[Path] = None
    ):
        super().__init__(template, id_path, cursor_path)
        self._error_message_path = error_message_path

    @classmethod
    def non_breaking_error(cls) -> "ErrorRecordBuilder":
        return cls(find_template("non_breaking_error", __file__), None, None, error_message_path=FieldPath("details"))

    @classmethod
    def breaking_error(cls) -> "ErrorRecordBuilder":
        return cls(find_template("error", __file__), None, None, error_message_path=FieldPath("message"))

    def with_error_message(self, message: str) -> "ErrorRecordBuilder":
        self._set_field(self._error_message_path._path[0], self._error_message_path, message)
        return self
