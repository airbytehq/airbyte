# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http.response_builder import HttpResponseBuilder, NestedPath, find_template


class UpdatesResponseBuilder(HttpResponseBuilder):
    @classmethod
    def updates_response(cls) -> "UpdatesResponseBuilder":
        return cls(find_template("updates", __file__), NestedPath(["data", "updates"]), None)
