#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from typing import List, Union

from airbyte_cdk.source.config import BaseConfig
from pydantic import BaseModel, Field


class InnerClass(BaseModel):
    field1: str
    field2: int


class Choice1(BaseModel):
    selected_strategy = Field('option1', const=True)

    name: str
    count: int


class Choice2(BaseModel):
    selected_strategy = Field('option2', const=True)

    sequence: List[str]


class SomeConfig(BaseConfig):
    items: List[InnerClass]
    choice: Union[Choice1, Choice2]


class TestBaseConfig:
    def test_schema_postprocessing(self):
        schema = SomeConfig.schema()
        assert schema == ""
