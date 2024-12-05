# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from __future__ import annotations

import re
from typing import TYPE_CHECKING

import asyncclick as click

if TYPE_CHECKING:
    from enum import Enum
    from typing import Callable, Dict, Tuple, Type

    from pipelines.models.steps import STEP_PARAMS

# Pattern  for extra param options: --<step_id>.<option_name>=<option_value>
EXTRA_PARAM_PATTERN_FOR_OPTION = re.compile(r"^--([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_-][a-zA-Z0-9_-]*)=([^=]+)$")
# Pattern  for extra param flag: --<step_id>.<option_name>
EXTRA_PARAM_PATTERN_FOR_FLAG = re.compile(r"^--([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_-][a-zA-Z0-9_-]*)$")
EXTRA_PARAM_PATTERN_ERROR_MESSAGE = "The extra flags must be structured as --<step_id>.<flag_name> for flags or --<step_id>.<option_name>=<option_value> for options. You can use - or -- for option/flag names."


def build_extra_params_mapping(SupportedStepIds: Type[Enum]) -> Callable:
    def callback(ctx: click.Context, argument: click.core.Argument, raw_extra_params: Tuple[str]) -> Dict[str, STEP_PARAMS]:
        """Build a mapping of step id to extra params.
        Validate the extra params and raise a ValueError if they are invalid.
        Validation rules:
        - The extra params must be structured as --<step_id>.<param_name>=<param_value> for options or --<step_id>.<param_name> for flags.
        - The step id must be one of the existing step ids.


        Args:
            ctx (click.Context): The click context.
            argument (click.core.Argument): The click argument.
            raw_extra_params (Tuple[str]): The extra params provided by the user.
        Raises:
            ValueError: Raised if the extra params format is invalid.
            ValueError: Raised if the step id in the extra params is not one of the unique steps to run.

        Returns:
            Dict[Literal, STEP_PARAMS]: The mapping of step id to extra params.
        """
        extra_params_mapping: Dict[str, STEP_PARAMS] = {}
        for param in raw_extra_params:
            is_flag = "=" not in param
            pattern = EXTRA_PARAM_PATTERN_FOR_FLAG if is_flag else EXTRA_PARAM_PATTERN_FOR_OPTION
            matches = pattern.match(param)
            if not matches:
                raise ValueError(f"Invalid parameter {param}. {EXTRA_PARAM_PATTERN_ERROR_MESSAGE}")
            if is_flag:
                step_name, param_name = matches.groups()
                param_value = None
            else:
                step_name, param_name, param_value = matches.groups()
            try:
                step_id = SupportedStepIds(step_name).value
            except ValueError:
                raise ValueError(f"Invalid step name {step_name}, it must be one of {[step_id.value for step_id in SupportedStepIds]}")

            extra_params_mapping.setdefault(step_id, {}).setdefault(param_name, [])
            # param_value is None if the param is a flag
            if param_value is not None:
                extra_params_mapping[step_id][param_name].append(param_value)
        return extra_params_mapping

    return callback
