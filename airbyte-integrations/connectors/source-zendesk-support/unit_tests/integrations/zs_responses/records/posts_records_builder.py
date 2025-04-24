# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http.response_builder import FieldPath, NestedPath

from .records_builder import ZendeskSupportRecordBuilder


class PostsRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def posts_record(cls) -> "PostsRecordBuilder":
        record_template = cls.extract_record("posts", __file__, NestedPath(["posts", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))
