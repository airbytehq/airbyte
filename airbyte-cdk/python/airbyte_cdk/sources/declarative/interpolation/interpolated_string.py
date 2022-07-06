#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Optional

from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation
from pydantic import BaseModel, Field


class InterpolatedString(BaseModel):
    string: str = Field()
    default: Optional[str]
    interpolation = JinjaInterpolation()

    class Config:
        arbitrary_types_allowed = True

    def eval(self, config, **kwargs):
        return self.interpolation.eval(self.string, config, self.default, **kwargs)
