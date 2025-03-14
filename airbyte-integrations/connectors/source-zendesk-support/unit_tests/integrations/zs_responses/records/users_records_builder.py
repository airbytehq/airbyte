# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http.response_builder import FieldPath, NestedPath

from .records_builder import ZendeskSupportRecordBuilder


class UsersRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def record(cls) -> "UsersRecordBuilder":
        record_template = cls.extract_record("users", __file__, NestedPath(["users", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))
