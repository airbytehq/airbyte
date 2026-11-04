# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http.response_builder import FieldPath, NestedPath

from .record_builder import MondayRecordBuilder


class UpdatesRecordBuilder(MondayRecordBuilder):
    @classmethod
    def updates_record(cls) -> "UpdatesRecordBuilder":
        record_template = cls.extract_record("updates", __file__, NestedPath(["data", "updates", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("created_at"))
