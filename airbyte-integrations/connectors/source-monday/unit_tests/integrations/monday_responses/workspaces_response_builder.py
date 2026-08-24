# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http.response_builder import HttpResponseBuilder, NestedPath, find_template


class WorkspacesResponseBuilder(HttpResponseBuilder):
    @classmethod
    def workspaces_response(cls) -> "WorkspacesResponseBuilder":
        return cls(find_template("workspaces", __file__), NestedPath(["data", "workspaces"]), None)
