#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime
from base64 import b64encode

from airbyte_cdk.sources.declarative.interpolation.interpolation import Interpolation
from jinja2 import Environment
from jinja2.exceptions import UndefinedError


def coolfunc(s):
    return s + " is cool"


class JinjaInterpolation(Interpolation):
    def __init__(self):
        self._environment = Environment()
        # Defines some utility methods that can be called from template strings
        # eg "{{ today_utc() }}
        self._environment.globals["now_local"] = datetime.datetime.now
        self._environment.globals["now_utc"] = lambda: datetime.datetime.now(datetime.timezone.utc)
        self._environment.globals["today_utc"] = lambda: datetime.datetime.now(datetime.timezone.utc).date()
        self._environment.globals["base64"] = lambda s: b64encode(s.encode("utf8")).decode("utf8")
        self._environment.globals["encode"] = lambda s, encoding: s.encode(encoding)

    def eval(self, input_str: str, config, default=None, **kwargs):
        context = {"config": config, **kwargs}
        print(self._environment.globals)
        try:
            if isinstance(input_str, str):
                result = self._eval(input_str, context)
                if result:
                    return result
            else:
                # If input is not a string, return it as is
                raise Exception(f"Expected a string. got {input_str}")
        except UndefinedError:
            pass
        # If result is empty or resulted in an undefined error, evaluate and return the default string
        return self._eval(default, context)

    def _eval(self, s: str, context):
        try:
            return self._environment.from_string(s).render(context)
        except TypeError:
            # The string is a static value, not a jinja template
            # It can be returned as is
            return s
