# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http.response_builder import HttpResponseBuilder, NestedPath, find_template


class TeamsResponseBuilder(HttpResponseBuilder):
    @classmethod
    def teams_response(cls) -> "TeamsResponseBuilder":
        return cls(find_template("teams", __file__), NestedPath(["data", "teams"]), None)
