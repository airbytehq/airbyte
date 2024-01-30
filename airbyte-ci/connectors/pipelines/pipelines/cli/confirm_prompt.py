#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

from typing import TYPE_CHECKING

import asyncclick as click

if TYPE_CHECKING:
    from typing import Any, Callable

PRE_CONFIRM_ALL_KEY = "yes"


def pre_confirm_all_flag(f: Callable) -> Callable:
    """Decorator to add a --yes flag to a command."""
    return click.option("-y", "--yes", PRE_CONFIRM_ALL_KEY, is_flag=True, default=False, help="Skip prompts and use default values")(f)


def confirm(*args: Any, **kwargs: Any) -> bool:
    """Confirm a prompt with the user, with support for a --yes flag."""
    additional_pre_confirm_key = kwargs.pop("additional_pre_confirm_key", None)
    ctx = click.get_current_context()
    if ctx.obj.get(PRE_CONFIRM_ALL_KEY, False):
        return True

    if additional_pre_confirm_key:
        if ctx.obj.get(additional_pre_confirm_key, False):
            return True

    return click.confirm(*args, **kwargs)
