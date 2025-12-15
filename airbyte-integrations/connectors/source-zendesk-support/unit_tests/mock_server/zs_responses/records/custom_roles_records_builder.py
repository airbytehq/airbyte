# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http.response_builder import FieldPath, NestedPath

from .records_builder import ZendeskSupportRecordBuilder


class CustomRolesRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def custom_roles_record(cls) -> "CustomRolesRecordBuilder":
        record_template = cls.extract_record("custom_roles", __file__, NestedPath(["custom_roles", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))

    def with_id(self, id: int) -> "CustomRolesRecordBuilder":
        self._record["id"] = id
        return self
