# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http.response_builder import HttpResponseBuilder, NestedPath, find_template


class BoardsResponseBuilder(HttpResponseBuilder):
    @classmethod
    def boards_response(cls) -> "BoardsResponseBuilder":
        return cls(find_template("boards", __file__), NestedPath(["data", "boards"]), None)
