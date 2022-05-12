#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import datetime

from airbyte_cdk.sources.cac.interpolation.interpolation import Interpolation
from jinja2 import Environment
from jinja2.exceptions import UndefinedError


class JinjaInterpolation(Interpolation):
    def __init__(self):
        self._environment = Environment()
        self._environment.globals["now_local"] = datetime.datetime.now
        self._environment.globals["now_utc"] = lambda: datetime.datetime.now(datetime.timezone.utc)
        self._environment.globals["today_utc"] = lambda: datetime.datetime.now(datetime.timezone.utc).date()
        self._environment.globals["to_timestamp"] = lambda s: datetime.datetime.strptime(s, "%Y-%m-%d")  # FIXME hardcoded format
        self._environment.globals["from_timestamp"] = lambda i: datetime.datetime.fromtimestamp(i).strftime(
            "%Y-%m-%d"
        )  # FIXME hardcoded format

    def eval(self, input_str: str, vars, config, default=None, **kwargs):
        context = {"vars": vars, "config": config, **kwargs}
        try:
            if isinstance(input_str, str):
                result = self._eval(input_str, context)
                if result:
                    return result
            else:
                return input_str
        except UndefinedError:
            # TODO: log warning
            pass
        return self._eval(default, context)

    def _eval(self, s: str, context):
        try:
            return self._environment.from_string(s).render(context)
        except TypeError:
            # TODO log warning!
            # Type error if not a template node!
            return s
