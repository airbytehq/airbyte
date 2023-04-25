#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import ast
from typing import Optional

from airbyte_cdk.sources.declarative.interpolation.filters import filters
from airbyte_cdk.sources.declarative.interpolation.interpolation import Interpolation
from airbyte_cdk.sources.declarative.interpolation.macros import macros
from airbyte_cdk.sources.declarative.types import Config
from jinja2 import Environment
from jinja2.exceptions import UndefinedError


class JinjaInterpolation(Interpolation):
    """
    Interpolation strategy using the Jinja2 template engine.

    If the input string is a raw string, the interpolated string will be the same.
    `eval("hello world") -> "hello world"`

    The engine will evaluate the content passed within {{}}, interpolating the keys from the config and context-specific arguments.
    `eval("hello {{ name }}", name="airbyte") -> "hello airbyte")`
    `eval("hello {{ config.name }}", config={"name": "airbyte"}) -> "hello airbyte")`

    In additional to passing additional values through the kwargs argument, macros can be called from within the string interpolation.
    For example,
    "{{ max(2, 3) }}" will return 3

    Additional information on jinja templating can be found at https://jinja.palletsprojects.com/en/3.1.x/templates/#
    """

    # These aliases are used to deprecate existing keywords without breaking all existing connectors.
    ALIASES = {
        "stream_interval": "stream_slice",  # Use stream_interval to access incremental_sync values
        "stream_partition": "stream_slice",  # Use stream_partition to access partition router's values
    }

    def __init__(self):
        self._environment = Environment()
        self._environment.filters.update(**filters)
        self._environment.globals.update(**macros)

    def eval(self, input_str: str, config: Config, default: Optional[str] = None, **additional_parameters):
        context = {"config": config, **additional_parameters}

        for alias, equivalent in self.ALIASES.items():
            if alias in context:
                # This is unexpected. We could ignore or log a warning, but failing loudly should result in fewer surprises
                raise ValueError(
                    f"Found reserved keyword {alias} in interpolation context. This is unexpected and indicative of a bug in the CDK."
                )
            elif equivalent in context:
                context[alias] = context[equivalent]

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
