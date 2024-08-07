# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http.response_builder import FieldPath, NestedPath

from .record_builder import MondayRecordBuilder


class TeamsRecordBuilder(MondayRecordBuilder):
    @classmethod
    def teams_record(cls) -> "TeamsRecordBuilder":
        record_template = cls.extract_record("teams", __file__, NestedPath(["data", "teams", 0]))
        return cls(record_template, FieldPath("id"), None)
