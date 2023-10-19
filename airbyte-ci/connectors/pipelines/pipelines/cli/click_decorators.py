

import functools
import inspect
import click



def _contains_var_kwarg(f):
    return any(
        param.kind == inspect.Parameter.VAR_KEYWORD
        for param in inspect.signature(f).parameters.values()
    )


def _is_kwarg_of(key, f):
    param = inspect.signature(f).parameters.get(key, False)
    return param and (
        param.kind is inspect.Parameter.KEYWORD_ONLY or
        param.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    )


def click_ignore_unused_kwargs(f):
    """Make function ignore unmatched kwargs.

    If the function already has the catch all **kwargs, do nothing.

    Useful in the case that the argument is meant to be passed to a child command
    and is not used by the parent command
    """
    if _contains_var_kwarg(f):
        return f

    @functools.wraps(f)
    def inner(*args, **kwargs):
        filtered_kwargs = {
            key: value
            for key, value in kwargs.items()
            if _is_kwarg_of(key, f)
        }
        return f(*args, **filtered_kwargs)
    return inner


def click_pass_context_and_args_to_children(f):
    """
    Decorator to pass click context and args to children commands.
    """

    @click.pass_context
    def wrapper(*args, **kwargs):
        ctx = args[0]
        ctx.ensure_object(dict)
        click_obj = ctx.obj
        click_params = ctx.params
        command_name = ctx.command.name

        # Error if click_obj and click_params have the same key
        intersection = set(click_obj.keys()) & set(click_params.keys())
        if intersection:
            raise ValueError(f"Your command '{command_name}' has defined options/arguments with the same key as its parent: {intersection}")

        ctx.obj = {**click_obj, **click_params}

        return f(*args, **kwargs)

    return wrapper
