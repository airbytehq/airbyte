# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http.response_builder import FieldPath, NestedPath

from .record_builder import MondayRecordBuilder


class UpdatesRecordBuilder(MondayRecordBuilder):
    @classmethod
    def updates_record(cls) -> "UpdatesRecordBuilder":
        record_template = cls.extract_record("updates", __file__, NestedPath(["data", "updates", 0]))
        return cls(record_template, FieldPath("id"), None)
