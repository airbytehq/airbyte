#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import List, Union

from airbyte_cdk.sources.config import BaseConfig
from pydantic import BaseModel, Field


class InnerClass(BaseModel):
    field1: str
    field2: int


class Choice1(BaseModel):
    selected_strategy = Field("option1", const=True)

    name: str
    count: int


class Choice2(BaseModel):
    selected_strategy = Field("option2", const=True)

    sequence: List[str]


class SomeSourceConfig(BaseConfig):
    class Config:
        title = "Some Source"

    items: List[InnerClass]
    choice: Union[Choice1, Choice2]


class TestBaseConfig:
    EXPECTED_SCHEMA = {
        "properties": {
            "choice": {
                "oneOf": [
                    {
                        "properties": {
                            "count": {"title": "Count", "type": "integer"},
                            "name": {"title": "Name", "type": "string"},
                            "selected_strategy": {"const": "option1", "title": "Selected " "Strategy", "type": "string"},
                        },
                        "required": ["name", "count"],
                        "title": "Choice1",
                        "type": "object",
                    },
                    {
                        "properties": {
                            "selected_strategy": {"const": "option2", "title": "Selected " "Strategy", "type": "string"},
                            "sequence": {"items": {"type": "string"}, "title": "Sequence", "type": "array"},
                        },
                        "required": ["sequence"],
                        "title": "Choice2",
                        "type": "object",
                    },
                ],
                "title": "Choice",
            },
            "items": {
                "items": {
                    "properties": {"field1": {"title": "Field1", "type": "string"}, "field2": {"title": "Field2", "type": "integer"}},
                    "required": ["field1", "field2"],
                    "title": "InnerClass",
                    "type": "object",
                },
                "title": "Items",
                "type": "array",
            },
        },
        "required": ["items", "choice"],
        "title": "Some Source",
        "type": "object",
    }

    def test_schema_postprocessing(self):
        schema = SomeSourceConfig.schema()
        assert schema == self.EXPECTED_SCHEMA
