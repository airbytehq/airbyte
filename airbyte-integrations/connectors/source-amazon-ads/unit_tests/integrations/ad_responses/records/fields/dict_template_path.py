# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Any, Dict

from airbyte_cdk.test.mock_http.response_builder import Path


class DictTemplatePath(Path):
    def update(self, template: Dict[str, Any], value: Dict[str, Any]) -> None:
        template.clear()
        template.update(value)

    def write(self, template: Dict[str, Any], value: Dict[str, Any]) -> None:
        template.update(value)
