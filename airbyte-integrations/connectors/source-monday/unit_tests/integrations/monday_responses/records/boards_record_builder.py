# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http.response_builder import FieldPath, NestedPath

from .record_builder import MondayRecordBuilder


class BoardsRecordBuilder(MondayRecordBuilder):
    @classmethod
    def boards_record(cls) -> "BoardsRecordBuilder":
        record_template = cls.extract_record("boards", __file__, NestedPath(["data", "boards", 0]))
        return cls(record_template, FieldPath("id"), None)
