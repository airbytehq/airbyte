# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http.response_builder import FieldPath, NestedPath

from .record_builder import MondayRecordBuilder


class WorkspacesRecordBuilder(MondayRecordBuilder):
    @classmethod
    def workspaces_record(cls) -> "WorkspacesRecordBuilder":
        record_template = cls.extract_record("workspaces", __file__, NestedPath(["data", "workspaces", 0]))
        return cls(record_template, FieldPath("id"), None)
