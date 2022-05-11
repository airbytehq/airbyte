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
        try:
            context = {"vars": vars, "config": config, **kwargs}
            if isinstance(input_str, str):
                ret = self._environment.from_string(input_str).render(context)
            else:
                ret = None
            return ret
        except UndefinedError:
            # TODO: log warning
            return default
