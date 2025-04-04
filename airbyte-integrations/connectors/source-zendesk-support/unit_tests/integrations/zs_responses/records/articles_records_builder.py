# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http.response_builder import FieldPath, NestedPath

from .records_builder import ZendeskSupportRecordBuilder


class ArticlesRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def record(cls) -> "ArticlesRecordBuilder":
        record_template = cls.extract_record("articles", __file__, NestedPath(["articles", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))
