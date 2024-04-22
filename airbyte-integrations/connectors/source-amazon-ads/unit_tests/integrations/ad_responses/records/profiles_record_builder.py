# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http.response_builder import FieldPath, RecordBuilder, find_template


class ProfilesRecordBuilder(RecordBuilder):
    @classmethod
    def profiles_record(cls) -> "ProfilesRecordBuilder":
        return cls(find_template("profiles", __file__)[0], FieldPath("profileId"), None)
