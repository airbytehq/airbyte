#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import functools
import inspect
from functools import wraps
from typing import Any, Callable, Type, TypeVar

import asyncclick as click
from pipelines.models.ci_requirements import CIRequirements

_AnyCallable = Callable[..., Any]
FC = TypeVar("FC", bound="_AnyCallable | click.core.Command")
CI_REQUIREMENTS_OPTION_NAME = "--ci-requirements"


def _contains_var_kwarg(f: Callable) -> bool:
    return any(param.kind is inspect.Parameter.VAR_KEYWORD for param in inspect.signature(f).parameters.values())


def _is_kwarg_of(key: str, f: Callable) -> bool:
    param = inspect.signature(f).parameters.get(key)
    if not param:
        return False

    return bool(param) and (param.kind is inspect.Parameter.KEYWORD_ONLY or param.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD)


def click_ignore_unused_kwargs(f: Callable) -> Callable:
    """Make function ignore unmatched kwargs.

    If the function already has the catch all **kwargs, do nothing.

    Useful in the case that the argument is meant to be passed to a child command
    and is not used by the parent command
    """
    if _contains_var_kwarg(f):
        return f

    @functools.wraps(f)
    def inner(*args: Any, **kwargs: Any) -> Callable:
        filtered_kwargs = {key: value for key, value in kwargs.items() if _is_kwarg_of(key, f)}
        return f(*args, **filtered_kwargs)

    return inner


def click_merge_args_into_context_obj(f: Callable) -> Callable:
    """
    Decorator to pass click context and args to children commands.
    """

    def wrapper(*args: Any, **kwargs: Any) -> Callable:
        ctx = click.get_current_context()
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


def click_append_to_context_object(key: str, value: Callable) -> Callable:
    """
    Decorator to append a value to the click context object.
    """

    def decorator(f: Callable) -> Callable:
        async def wrapper(*args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
            ctx = click.get_current_context()
            ctx.ensure_object(dict)

            # if async, get the value, cannot use await
            if inspect.iscoroutinefunction(value):
                ctx.obj[key] = await value(ctx)
            elif callable(value):
                ctx.obj[key] = value(ctx)
            else:
                ctx.obj[key] = value
            return await f(*args, **kwargs)

        return wrapper

    return decorator


class LazyPassDecorator:
    """
    Used to create a decorator that will pass an instance of the given class to the decorated function.
    """

    def __init__(self, cls: Type[Any], *args: Any, **kwargs: Any) -> None:
        """
        Initialize the decorator with the given source class
        """
        self.cls = cls
        self.args = args
        self.kwargs = kwargs

    def __call__(self, f: Callable[..., Any]) -> Callable[..., Any]:
        """
        Create a decorator that will pass an instance of the given class to the decorated function.
        """

        @wraps(f)
        def decorated_function(*args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
            # Check if the kwargs already contain the arguments being passed by the decorator
            decorator_kwargs = {k: v for k, v in self.kwargs.items() if k not in kwargs}
            # Create an instance of the class
            instance = self.cls(*self.args, **decorator_kwargs)
            # If function has **kwargs, we can put the instance there
            if "kwargs" in kwargs:
                kwargs["kwargs"] = instance
            # Otherwise, add it to positional arguments
            else:
                args = (*args, instance)
            return f(*args, **kwargs)

        return decorated_function


def click_ci_requirements_option() -> Callable[[FC], FC]:
    """Add a --ci-requirements option to the command.

    Returns:
        Callable[[FC], FC]: The decorated command.
    """

    def callback(ctx: click.Context, param: click.Parameter, value: bool) -> None:
        if value:
            ci_requirements = CIRequirements()
            click.echo(ci_requirements.to_json())
            ctx.exit()

    return click.decorators.option(
        CI_REQUIREMENTS_OPTION_NAME,
        is_flag=True,
        expose_value=False,
        is_eager=True,
        flag_value=True,
        help="Show the CI requirements and exit. It used to make airbyte-ci client define the CI runners it will run on.",
        callback=callback,
    )
