# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http.response_builder import HttpResponseBuilder, NestedPath, find_template


class ItemsResponseBuilder(HttpResponseBuilder):
    @classmethod
    def items_response(cls) -> "ItemsResponseBuilder":
        return cls(find_template("items", __file__), NestedPath(["data", "boards", 0, "items_page", "items"]), None)
