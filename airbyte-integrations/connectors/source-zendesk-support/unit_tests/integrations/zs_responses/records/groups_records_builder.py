# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http.response_builder import FieldPath, NestedPath

from .records_builder import ZendeskSupportRecordBuilder


class GroupsRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def groups_record(cls) -> "GroupsRecordBuilder":
        record_template = cls.extract_record("groups", __file__, NestedPath(["groups", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))
