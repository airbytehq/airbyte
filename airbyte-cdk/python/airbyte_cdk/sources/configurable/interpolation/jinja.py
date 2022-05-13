#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import datetime

from airbyte_cdk.sources.configurable.interpolation.interpolation import \
    Interpolation
from jinja2 import Environment
from jinja2.exceptions import UndefinedError


class JinjaInterpolation(Interpolation):
    def __init__(self):
        self._environment = Environment()
        self._environment.globals["now_local"] = datetime.datetime.now
        self._environment.globals["now_utc"] = lambda: datetime.datetime.now(datetime.timezone.utc)
        self._environment.globals["today_utc"] = lambda: datetime.datetime.now(datetime.timezone.utc).date()

    def eval(self, input_str: str, config, default=None, **kwargs):
        context = {"config": config, **kwargs}
        try:
            if isinstance(input_str, str):
                result = self._eval(input_str, context)
                if result:
                    return result
            else:
                return input_str
        except UndefinedError:
            pass
        return self._eval(default, context)

    def _eval(self, s: str, context):
        try:
            return self._environment.from_string(s).render(context)
        except TypeError:
            # Not a template node!
            return s
