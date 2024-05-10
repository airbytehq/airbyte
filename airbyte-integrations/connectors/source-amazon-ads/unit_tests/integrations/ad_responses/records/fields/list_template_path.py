# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Any, Dict, List

from airbyte_cdk.test.mock_http.response_builder import Path


class ListTemplatePath(Path):
    def update(self, template: List[Dict[str, Any]], value: List[Dict[str, Any]]) -> None:
        template.clear()
        template.extend(value)

    def write(self, template: List[Dict[str, Any]], value: List[Dict[str, Any]]) -> None:
        template.extend(value)
