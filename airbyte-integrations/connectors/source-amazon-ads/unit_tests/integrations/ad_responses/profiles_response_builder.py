# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http.response_builder import HttpResponseBuilder, RootPath, find_template


class ProfilesResponseBuilder(HttpResponseBuilder):
    @classmethod
    def profiles_response(cls) -> "ProfilesResponseBuilder":
        return cls(find_template("profiles", __file__), RootPath(), None)
