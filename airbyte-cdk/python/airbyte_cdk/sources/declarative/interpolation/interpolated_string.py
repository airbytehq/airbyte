#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass, field
from typing import Optional

from airbyte_cdk.sources.declarative.cdk_jsonschema import JsonSchemaMixin
from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation


@dataclass
class InterpolatedString(JsonSchemaMixin):
    """InterpolatedString"""

    string_template: str
    default: Optional[str] = field(default=None)

    def __post_init__(self):
        self._interpolation = JinjaInterpolation()

    def eval(self, config, **kwargs):
        return self._interpolation.eval(self.string_template, config, self.default, **kwargs)
