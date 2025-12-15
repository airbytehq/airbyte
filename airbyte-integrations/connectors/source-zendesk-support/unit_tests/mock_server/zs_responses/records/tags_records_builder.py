# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http.response_builder import FieldPath, NestedPath

from .records_builder import ZendeskSupportRecordBuilder


class TagsRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def tags_record(cls) -> "TagsRecordBuilder":
        record_template = cls.extract_record("tags", __file__, NestedPath(["tags", 0]))
        return cls(record_template, FieldPath("name"), None)

    def with_name(self, name: str) -> "TagsRecordBuilder":
        self._record["name"] = name
        return self
