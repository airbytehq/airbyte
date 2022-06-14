#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import ast
import datetime

from airbyte_cdk.sources.declarative.interpolation.interpolation import Interpolation
from jinja2 import Environment
from jinja2.exceptions import UndefinedError


class JinjaInterpolation(Interpolation):
    def __init__(self):
        self._environment = Environment()
        # Defines some utility methods that can be called from template strings
        # eg "{{ today_utc() }}
        self._environment.globals["now_local"] = datetime.datetime.now
        self._environment.globals["now_utc"] = lambda: datetime.datetime.now(datetime.timezone.utc)
        self._environment.globals["today_utc"] = lambda: datetime.datetime.now(datetime.timezone.utc).date()

    def eval(self, input_str: str, config, default=None, **kwargs):
        context = {"config": config, **kwargs}
        try:
            if isinstance(input_str, str):
                result = self._eval(input_str, context)
                if result:
                    return self._literal_eval(result)
            else:
                # If input is not a string, return it as is
                raise Exception(f"Expected a string. got {input_str}")
        except UndefinedError:
            pass
        # If result is empty or resulted in an undefined error, evaluate and return the default string
        default_value = self._eval(default, context)
        return self._literal_eval(default_value)

    def _literal_eval(self, value):
        try:
            ast_result = ast.literal_eval(value)
            return ast_result
        except (ValueError, SyntaxError):
            return value

    def _eval(self, s: str, context):
        try:
            return self._environment.from_string(s).render(context)
        except TypeError:
            # The string is a static value, not a jinja template
            # It can be returned as is
            return s
