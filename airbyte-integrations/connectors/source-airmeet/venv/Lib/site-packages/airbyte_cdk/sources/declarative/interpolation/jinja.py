#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import ast
from functools import cache
from typing import Any, Mapping, Optional, Set, Tuple, Type

from jinja2 import meta
from jinja2.environment import Template
from jinja2.exceptions import UndefinedError
from jinja2.sandbox import SandboxedEnvironment

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.interpolation.filters import filters
from airbyte_cdk.sources.declarative.interpolation.interpolation import Interpolation
from airbyte_cdk.sources.declarative.interpolation.macros import macros
from airbyte_cdk.sources.types import Config
from airbyte_cdk.utils import AirbyteTracedException


class StreamPartitionAccessEnvironment(SandboxedEnvironment):
    """
    Currently, source-jira is setting an attribute to StreamSlice specific to its use case which because of the PerPartitionCursor is set to
    StreamSlice._partition but not exposed through StreamSlice.partition. This is a patch to still allow source-jira to have access to this
    parameter
    """

    def is_safe_attribute(self, obj: Any, attr: str, value: Any) -> bool:
        if attr in ["_partition"]:
            return True
        return super().is_safe_attribute(obj, attr, value)  # type: ignore  # for some reason, mypy says 'Returning Any from function declared to return "bool"'


# These aliases are used to deprecate existing keywords without breaking all existing connectors.
_ALIASES = {
    "stream_interval": "stream_slice",  # Use stream_interval to access incremental_sync values
    "stream_partition": "stream_slice",  # Use stream_partition to access partition router's values
}

_UNSUPPORTED_INTERPOLATION_VARIABLES: Mapping[str, str] = {
    "stream_state": "`stream_state` is no longer supported for interpolation. We recommend using `stream_interval` instead. Please reference the CDK Migration Guide for more information.",
}

# These extensions are not installed so they're not currently a problem,
# but we're still explicitly removing them from the jinja context.
# At worst, this is documentation that we do NOT want to include these extensions because of the potential security risks
_RESTRICTED_EXTENSIONS = ["jinja2.ext.loopcontrols"]  # Adds support for break continue in loops

# By default, these Python builtin functions are available in the Jinja context.
# We explicitly remove them because of the potential security risk.
# Please add a unit test to test_jinja.py when adding a restriction.
_RESTRICTED_BUILTIN_FUNCTIONS = [
    "range"
]  # The range function can cause very expensive computations

_ENVIRONMENT = StreamPartitionAccessEnvironment()
_ENVIRONMENT.filters.update(**filters)
_ENVIRONMENT.globals.update(**macros)

for extension in _RESTRICTED_EXTENSIONS:
    _ENVIRONMENT.extensions.pop(extension, None)
for builtin in _RESTRICTED_BUILTIN_FUNCTIONS:
    _ENVIRONMENT.globals.pop(builtin, None)


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

    def eval(
        self,
        input_str: str,
        config: Config,
        default: Optional[str] = None,
        valid_types: Optional[Tuple[Type[Any]]] = None,
        **additional_parameters: Any,
    ) -> Any:
        context = {"config": config, **additional_parameters}

        for alias, equivalent in _ALIASES.items():
            if alias in context:
                # This is unexpected. We could ignore or log a warning, but failing loudly should result in fewer surprises
                raise ValueError(
                    f"Found reserved keyword {alias} in interpolation context. This is unexpected and indicative of a bug in the CDK."
                )
            elif equivalent in context:
                context[alias] = context[equivalent]

        for variable_name in _UNSUPPORTED_INTERPOLATION_VARIABLES:
            if variable_name in input_str:
                raise AirbyteTracedException(
                    message=_UNSUPPORTED_INTERPOLATION_VARIABLES[variable_name],
                    internal_message=_UNSUPPORTED_INTERPOLATION_VARIABLES[variable_name],
                    failure_type=FailureType.config_error,
                )
        try:
            if isinstance(input_str, str):
                result = self._eval(input_str, context)
                if result:
                    return self._literal_eval(result, valid_types)
            else:
                # If input is not a string, return it as is
                raise Exception(f"Expected a string, got {input_str}")
        except UndefinedError:
            pass

        # If result is empty or resulted in an undefined error, evaluate and return the default string
        return self._literal_eval(self._eval(default, context), valid_types)

    def _literal_eval(self, result: Optional[str], valid_types: Optional[Tuple[Type[Any]]]) -> Any:
        try:
            evaluated = ast.literal_eval(result)  # type: ignore # literal_eval is able to handle None
        except (ValueError, SyntaxError):
            return result
        if (not valid_types and not isinstance(evaluated, complex)) or (
            valid_types and isinstance(evaluated, valid_types)
        ):
            return evaluated
        return result

    def _eval(self, s: Optional[str], context: Mapping[str, Any]) -> Optional[str]:
        try:
            undeclared = self._find_undeclared_variables(s)
            undeclared_not_in_context = {var for var in undeclared if var not in context}
            if undeclared_not_in_context:
                raise ValueError(
                    f"Jinja macro has undeclared variables: {undeclared_not_in_context}. Context: {context}"
                )
            return self._compile(s).render(context)  # type: ignore # from_string is able to handle None
        except TypeError:
            # The string is a static value, not a jinja template
            # It can be returned as is
            return s

    @staticmethod
    @cache
    def _find_undeclared_variables(s: Optional[str]) -> Set[str]:
        """
        Find undeclared variables and cache them
        """
        ast = _ENVIRONMENT.parse(s)  # type: ignore # parse is able to handle None
        return meta.find_undeclared_variables(ast)

    @staticmethod
    @cache
    def _compile(s: str) -> Template:
        """
        We must cache the Jinja Template ourselves because we're using `from_string` instead of a template loader
        """
        return _ENVIRONMENT.from_string(s)
