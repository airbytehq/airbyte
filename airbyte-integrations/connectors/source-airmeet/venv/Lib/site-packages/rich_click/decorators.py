from __future__ import annotations

import sys
from gettext import gettext
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Type, TypeVar, Union, cast, overload

from click import Argument, Command, Context, Group, Option, Parameter
from click import argument as click_argument
from click import command as click_command
from click import confirmation_option as click_confirmation_option
from click import option as click_option
from click import pass_context as click_pass_context
from click import password_option as click_password_option
from click import version_option as click_version_option

from rich_click.rich_command import RichCommand, RichGroup
from rich_click.rich_context import RichContext
from rich_click.rich_help_configuration import RichHelpConfiguration
from rich_click.rich_panel import RichCommandPanel, RichOptionPanel, RichPanel
from rich_click.rich_parameter import RichArgument, RichOption


if sys.version_info < (3, 10):
    from typing_extensions import Concatenate, ParamSpec
else:
    from typing import Concatenate, ParamSpec


if TYPE_CHECKING:  # pragma: no cover
    from rich.console import Console


_AnyCallable = Callable[..., Any]
F = TypeVar("F", bound=Callable[..., Any])
FC = TypeVar("FC", bound=Union[Command, _AnyCallable])
C = TypeVar("C", bound=Command)


G = TypeVar("G", bound=Group)


# variant: no call, directly as decorator for a function.
@overload
def group(name: _AnyCallable) -> RichGroup: ...


# variant: with positional name and with positional or keyword cls argument:
# @group(namearg, GroupCls, ...) or @group(namearg, cls=GroupCls, ...)
@overload
def group(
    name: Optional[str],
    cls: Type[G],
    **attrs: Any,
) -> Callable[[_AnyCallable], G]: ...


# variant: name omitted, cls _must_ be a keyword argument, @group(cmd=GroupCls, ...)
@overload
def group(
    name: None = None,
    *,
    cls: Type[G],
    **attrs: Any,
) -> Callable[[_AnyCallable], G]: ...


# variant: with optional string name, no cls argument provided.
@overload
def group(name: Optional[str] = ..., cls: None = None, **attrs: Any) -> Callable[[_AnyCallable], RichGroup]: ...


def group(
    name: Union[str, _AnyCallable, None] = None,
    cls: Optional[Type[G]] = None,
    **attrs: Any,
) -> Union[Group, Callable[[_AnyCallable], Union[RichGroup, G]]]:
    """
    Group decorator function.

    Defines the group() function so that it uses the RichGroup class by default.
    """
    if cls is None:
        cls = cast(Type[G], RichGroup)

    if callable(name):
        return command(cls=cls, **attrs)(name)

    return command(name, cls, **attrs)


CmdType = TypeVar("CmdType", bound=Command)


# variant: no call, directly as decorator for a function.
@overload
def command(name: _AnyCallable) -> RichCommand: ...


# variant: with positional name and with positional or keyword cls argument:
# @command(namearg, CommandCls, ...) or @command(namearg, cls=CommandCls, ...)
@overload
def command(
    name: Optional[str],
    cls: Type[CmdType],
    **attrs: Any,
) -> Callable[[_AnyCallable], CmdType]: ...


# variant: name omitted, cls _must_ be a keyword argument, @command(cls=CommandCls, ...)
@overload
def command(
    name: None = None,
    *,
    cls: Type[CmdType],
    **attrs: Any,
) -> Callable[[_AnyCallable], CmdType]: ...


# variant: with optional string name, no cls argument provided.
@overload
def command(name: Optional[str] = ..., cls: None = None, **attrs: Any) -> Callable[[_AnyCallable], RichCommand]: ...


def command(
    name: Union[Optional[str], _AnyCallable] = None,
    cls: Optional[Type[CmdType]] = None,
    **attrs: Any,
) -> Union[Command, Callable[[_AnyCallable], Union[RichCommand, CmdType]]]:
    """
    Command decorator function.

    Defines the command() function so that it uses the RichCommand class by default.
    """
    func = None
    if callable(name):
        func = name
        name = None
        if "__rich_click_cli_patch" not in attrs:
            assert cls is None, "Use 'command(cls=cls)(callable)' to specify a class."
        attrs.pop("__rich_click_cli_patch", None)
        assert not attrs, "Use 'command(**kwargs)(callable)' to provide arguments."
    else:
        attrs.pop("__rich_click_cli_patch", None)

    if cls is None:
        cls = cast(Type[CmdType], RichCommand)

    def decorator(f: _AnyCallable) -> CmdType:
        cs = getattr(f, "__rich_context_settings__", None)
        if cs is not None:
            attr_cs = attrs.pop("context_settings", None)
            attr_cs = attr_cs if attr_cs is not None else {}
            attr_cs.update(cs)
            attrs["context_settings"] = attr_cs
            del f.__rich_context_settings__  # type: ignore[attr-defined]

        panels = getattr(f, "__rich_panels__", None)
        if panels is not None:
            attr_panels = attrs.pop("panels", None)
            attr_panels = attr_panels if attr_panels is not None else []
            attr_panels.extend(reversed(panels))
            attrs["panels"] = attr_panels
            del f.__rich_panels__  # type: ignore[attr-defined]

        return click_command(name, cls, **attrs)(f)

    if func is not None:
        return decorator(func)

    return decorator


def _context_settings_memo(f: Callable[..., Any], extra: Dict[str, Any]) -> None:
    if isinstance(f, RichCommand):
        f.context_settings.update(extra)
    else:
        if not hasattr(f, "__rich_context_settings__"):
            f.__rich_context_settings__ = {}  # type: ignore

        f.__rich_context_settings__.update(extra)  # type: ignore


def _rich_panel_memo(f: Callable[..., Any], panel: RichPanel[Any, Any]) -> None:
    if isinstance(f, RichCommand):
        f.add_panel(panel)
    else:
        if not hasattr(f, "__rich_panels__"):
            f.__rich_panels__ = []  # type: ignore

        f.__rich_panels__.append(panel)  # type: ignore


def rich_config(
    help_config: Optional[Union[Dict[str, Any], RichHelpConfiguration]] = None,
    *,
    console: Optional["Console"] = None,
) -> Callable[[FC], FC]:
    """
    Use decorator to configure Rich Click settings.

    Args:
    ----
        help_config: Rich help configuration that is used internally to format help messages and exceptions
            Defaults to None.
        console: A Rich Console that will be accessible from the `RichContext`, `RichCommand`, and `RichGroup` instances
            Defaults to None.

    """
    from rich.console import Console

    if isinstance(help_config, Console) and console is None:
        import warnings

        warnings.warn(
            "`rich_config()`'s args have been swapped."
            " Please set the config first, and use a kwarg to set the console.",
            DeprecationWarning,
            stacklevel=2,
        )
        console = help_config

    def decorator(obj: FC) -> FC:
        extra: Dict[str, Any] = {}
        if console is not None:
            extra["rich_console"] = console
        if help_config is not None:
            extra["rich_help_config"] = help_config

        _context_settings_memo(obj, extra)

        return obj

    return decorator


def _panel(
    name: str,
    cls: Type[RichPanel[Any, Any]],
    **attrs: Any,
) -> Callable[[FC], FC]:
    def decorator(obj: FC) -> FC:
        _rich_panel_memo(
            obj,
            cls(name=name, **attrs),
        )
        return obj

    return decorator


def option_panel(
    name: str,
    cls: Type[RichPanel[Parameter, Any]] = RichOptionPanel,
    **attrs: Any,
) -> Callable[[FC], FC]:
    """
    Use decorator to create a RichOptionPanel.

    Args:
    ----
        name: Name of the RichOptionPanel instance being created.
        cls: The class of the RichPanel; defaults to RichOptionPanel.
        attrs: Additional attributes to pass to the RichOptionPanel.

    """
    return _panel(name, cls, **attrs)


def command_panel(
    name: str,
    cls: Type[RichPanel[Command, Any]] = RichCommandPanel,
    **attrs: Any,
) -> Callable[[FC], FC]:
    """
    Use decorator to create a RichCommandPanel.

    Args:
    ----
        name: Name of the RichCommandPanel instance being created.
        cls: The class of the RichPanel; defaults to RichCommandPanel.
        attrs: Additional attributes to pass to the RichCommandPanel.

    """
    return _panel(name, cls, **attrs)


# Users of rich_click would face issues using mypy with this code,
# if not for wrapping `pass_context` with a new function signature:
#
# @click.command()
# @click.pass_context
# def cli(ctx: click.RichContext) -> None:
#    ...


P = ParamSpec("P")
R = TypeVar("R")


def pass_context(f: Callable[Concatenate[RichContext, P], R]) -> Callable[P, R]:
    # flake8: noqa: D400,D401
    """Marks a callback as wanting to receive the current context object as first argument."""
    return click_pass_context(f)  # type: ignore[arg-type,unused-ignore]


def help_option(*param_decls: str, **kwargs: Any) -> Callable[[FC], FC]:
    """
    Pre-configured ``--help`` option which immediately prints the help page
    and exits the program.

    :param param_decls: One or more option names. Defaults to the single
        value ``"--help"``.
    :param kwargs: Extra arguments are passed to :func:`option`.
    """

    def show_help(ctx: Context, param: Parameter, value: bool) -> None:
        """Callback that print the help page on ``<stdout>`` and exits."""
        if value and not ctx.resilient_parsing:
            # Avoid click.echo() because it ignores console settings like force_terminal.
            # Also, do not print() if empty string; assume console was record=False.
            if getattr(ctx, "help_to_stderr", False):
                print(ctx.get_help(), file=sys.stderr)
            else:
                print(ctx.get_help())
            ctx.exit()

    if not param_decls:
        param_decls = ("--help",)

    kwargs.setdefault("is_flag", True)
    kwargs.setdefault("expose_value", False)
    kwargs.setdefault("is_eager", True)
    kwargs.setdefault("help", gettext("Show this message and exit."))
    kwargs.setdefault("callback", show_help)
    kwargs.setdefault("cls", RichOption)

    return click_option(*param_decls, **kwargs)


def argument(*param_decls: str, cls: Optional[Type[Argument]] = None, **attrs: Any) -> Callable[[FC], FC]:
    """
    Attaches an argument to the command.  All positional arguments are
    passed as parameter declarations to :class:`Argument`; all keyword
    arguments are forwarded unchanged (except ``cls``).
    This is equivalent to creating an :class:`Argument` instance manually
    and attaching it to the :attr:`Command.params` list.

    For the default argument class, refer to :class:`Argument` and
    :class:`Parameter` for descriptions of parameters.

    :param cls: the argument class to instantiate.  This defaults to
                :class:`Argument`.
    :param param_decls: Passed as positional arguments to the constructor of
        ``cls``.
    :param attrs: Passed as keyword arguments to the constructor of ``cls``.
    """
    if cls is None:
        cls = RichArgument

    return click_argument(*param_decls, cls=cls, **attrs)


def option(*param_decls: str, cls: Optional[Type[Option]] = None, **attrs: Any) -> Callable[[FC], FC]:
    """
    Attaches an option to the command.  All positional arguments are
    passed as parameter declarations to :class:`Option`; all keyword
    arguments are forwarded unchanged (except ``cls``).
    This is equivalent to creating an :class:`Option` instance manually
    and attaching it to the :attr:`Command.params` list.

    For the default option class, refer to :class:`Option` and
    :class:`Parameter` for descriptions of parameters.

    :param cls: the option class to instantiate.  This defaults to
                :class:`Option`.
    :param param_decls: Passed as positional arguments to the constructor of
        ``cls``.
    :param attrs: Passed as keyword arguments to the constructor of ``cls``.
    """
    if cls is None:
        cls = RichOption

    return click_option(*param_decls, cls=cls, **attrs)


def confirmation_option(*param_decls: str, **kwargs: Any) -> Callable[[FC], FC]:
    """
    Add a ``--yes`` option which shows a prompt before continuing if
    not passed. If the prompt is declined, the program will exit.

    :param param_decls: One or more option names. Defaults to the single
        value ``"--yes"``.
    :param kwargs: Extra arguments are passed to :func:`option`.
    """
    kwargs.setdefault("cls", RichOption)
    return click_confirmation_option(*param_decls, **kwargs)


def password_option(*param_decls: str, **kwargs: Any) -> Callable[[FC], FC]:
    """
    Add a ``--password`` option which prompts for a password, hiding
    input and asking to enter the value again for confirmation.

    :param param_decls: One or more option names. Defaults to the single
        value ``"--password"``.
    :param kwargs: Extra arguments are passed to :func:`option`.
    """
    if not param_decls:
        param_decls = ("--password",)

    kwargs.setdefault("prompt", True)
    kwargs.setdefault("confirmation_prompt", True)
    kwargs.setdefault("hide_input", True)
    kwargs.setdefault("cls", RichOption)
    return click_password_option(*param_decls, **kwargs)


def version_option(
    version: Optional[str] = None,
    *param_decls: str,
    package_name: Optional[str] = None,
    prog_name: Optional[str] = None,
    message: Optional[str] = None,
    **kwargs: Any,
) -> Callable[[FC], FC]:
    """
    Add a ``--version`` option which immediately prints the version
    number and exits the program.

    If ``version`` is not provided, Click will try to detect it using
    :func:`importlib.metadata.version` to get the version for the
    ``package_name``. On Python < 3.8, the ``importlib_metadata``
    backport must be installed.

    If ``package_name`` is not provided, Click will try to detect it by
    inspecting the stack frames. This will be used to detect the
    version, so it must match the name of the installed package.

    :param version: The version number to show. If not provided, Click
        will try to detect it.
    :param param_decls: One or more option names. Defaults to the single
        value ``"--version"``.
    :param package_name: The package name to detect the version from. If
        not provided, Click will try to detect it.
    :param prog_name: The name of the CLI to show in the message. If not
        provided, it will be detected from the command.
    :param message: The message to show. The values ``%(prog)s``,
        ``%(package)s``, and ``%(version)s`` are available. Defaults to
        ``"%(prog)s, version %(version)s"``.
    :param kwargs: Extra arguments are passed to :func:`option`.
    :raise RuntimeError: ``version`` could not be detected.
    """
    kwargs.setdefault("cls", RichOption)
    return click_version_option(
        version, *param_decls, package_name=package_name, prog_name=prog_name, message=message, **kwargs
    )


__all__ = [
    "command",
    "group",
    "argument",
    "option",
    "password_option",
    "confirmation_option",
    "version_option",
    "help_option",
    "rich_config",
    "option_panel",
    "command_panel",
    "pass_context",
]
