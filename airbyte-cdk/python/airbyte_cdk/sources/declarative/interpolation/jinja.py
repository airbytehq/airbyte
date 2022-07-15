#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import ast

from airbyte_cdk.sources.declarative.interpolation.interpolation import Interpolation
from airbyte_cdk.sources.declarative.interpolation.macros import macros
from jinja2 import Environment
from jinja2.exceptions import UndefinedError


class JinjaInterpolation(Interpolation):
    def __init__(self):
        self._environment = Environment()
        self._environment.globals.update(**macros)

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
        return self._literal_eval(self._eval(default, context))

    def _literal_eval(self, result):
        try:
            return ast.literal_eval(result)
        except (ValueError, SyntaxError):
            return result

    def _eval(self, s: str, context):
        try:
            return self._environment.from_string(s).render(context)
        except TypeError:
            # The string is a static value, not a jinja template
            # It can be returned as is
            return s
