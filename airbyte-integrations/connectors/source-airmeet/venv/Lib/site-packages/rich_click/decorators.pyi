# Some influence take from stubs in Cloup:
# https://github.com/janluke/cloup
# Copyright (c) 2021, Gianluca Gippetto MIT
from __future__ import annotations

import sys
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    MutableMapping,
    Optional,
    Sequence,
    Type,
    TypeVar,
    Union,
    overload,
)

import click
from click.shell_completion import CompletionItem
from click.types import ParamType
from rich.console import Console

from rich_click._internal_types import PanelKwargs, RichContextSettingsDict, RichHelpConfigurationDict, TableKwargs
from rich_click.rich_command import RichCommand, RichGroup
from rich_click.rich_context import RichContext
from rich_click.rich_help_configuration import CommandColumnType, OptionColumnType, RichHelpConfiguration
from rich_click.rich_panel import RichOptionPanel, RichPanel

if sys.version_info < (3, 11):
    pass
else:
    pass

if sys.version_info < (3, 10):
    from typing_extensions import Concatenate, ParamSpec
else:
    from typing import Concatenate, ParamSpec

_AnyCallable = Callable[..., Any]

StyleType = str  # Pyright gets upset at rich.style.Style, so just use str
FC = TypeVar("FC", bound=Union[click.Command, _AnyCallable])
P = TypeVar("P", bound=click.Parameter)
C = TypeVar("C", bound=click.Command)
G = TypeVar("G", bound=click.Group)
RP = TypeVar("RP", bound=RichPanel[Any, Any])

ShellCompleteArg = Callable[
    [click.Context, P, str],
    Union[List[CompletionItem], List[str]],
]
ParamDefault = Union[Any, Callable[[], Any]]
ParamCallback = Callable[[click.Context, P, Any], Any]

# variant: no call, directly as decorator for a function.
@overload
def command(name: _AnyCallable) -> RichCommand: ...
@overload
def command(
    name: Optional[str] = ...,
    *,
    cls: Type[C],
    context_settings: RichContextSettingsDict,
    callback: Callable[..., Any] | None = ...,
    params: list[click.Parameter] | None = ...,
    help: str | None = ...,
    epilog: str | None = ...,
    short_help: str | None = ...,
    options_metavar: str | None = ...,
    add_help_option: bool = ...,
    no_args_is_help: bool = ...,
    hidden: bool = ...,
    deprecated: bool | str = ...,
    aliases: Optional[Iterable[str]] = ...,
    panels: Optional[List[RichPanel[Any, Any]]] = ...,
) -> Callable[[_AnyCallable], C]: ...
@overload
def command(
    name: Optional[str] = ...,
    *,
    cls: None,
    context_settings: RichContextSettingsDict,
    callback: Callable[..., Any] | None = ...,
    params: list[click.Parameter] | None = ...,
    help: str | None = ...,
    epilog: str | None = ...,
    short_help: str | None = ...,
    options_metavar: str | None = ...,
    add_help_option: bool = ...,
    no_args_is_help: bool = ...,
    hidden: bool = ...,
    deprecated: bool | str = ...,
    aliases: Optional[Iterable[str]] = ...,
    panels: Optional[List[RichPanel[Any, Any]]] = ...,
) -> Callable[[_AnyCallable], RichCommand]: ...
@overload
def command(
    name: Optional[str] = ...,
    *,
    cls: Type[C],
    context_settings: MutableMapping[str, Any] | None = ...,
    callback: Callable[..., Any] | None = ...,
    params: list[click.Parameter] | None = ...,
    help: str | None = ...,
    epilog: str | None = ...,
    short_help: str | None = ...,
    options_metavar: str | None = ...,
    add_help_option: bool = ...,
    no_args_is_help: bool = ...,
    hidden: bool = ...,
    deprecated: bool | str = ...,
    aliases: Optional[Iterable[str]] = ...,
    panels: Optional[List[RichPanel[Any, Any]]] = ...,
) -> Callable[[_AnyCallable], C]: ...
@overload
def command(
    name: Optional[str] = None,
    *,
    cls: None,
    context_settings: MutableMapping[str, Any] | None = ...,
    callback: Callable[..., Any] | None = ...,
    params: list[click.Parameter] | None = ...,
    help: str | None = ...,
    epilog: str | None = ...,
    short_help: str | None = ...,
    options_metavar: str | None = ...,
    add_help_option: bool = ...,
    no_args_is_help: bool = ...,
    hidden: bool = ...,
    deprecated: bool | str = ...,
    aliases: Optional[Iterable[str]] = ...,
    panels: Optional[List[RichPanel[Any, Any]]] = ...,
    **attrs: Any,
) -> Callable[[_AnyCallable], RichCommand]: ...

# variant: with positional name and with positional or keyword cls argument:
# @command(namearg, CommandCls, ...) or @command(namearg, cls=CommandCls, ...)
@overload
def command(
    name: Optional[str],
    cls: Type[C],
    **attrs: Any,
) -> Callable[[_AnyCallable], C]: ...

# variant: name omitted, cls _must_ be a keyword argument, @command(cls=CommandCls, ...)
@overload
def command(
    name: None = None,
    *,
    cls: Type[C],
    **attrs: Any,
) -> Callable[[_AnyCallable], C]: ...

# variant: with optional string name, no cls argument provided.
@overload
def command(name: Optional[str] = ..., cls: None = None, **attrs: Any) -> Callable[[_AnyCallable], RichCommand]: ...
def command(
    name: Optional[str] = None, *, cls: Optional[Type[C]] = None, **kwargs: Any
) -> Callable[[_AnyCallable], Union[click.Command, C]]: ...

# variant: no call, directly as decorator for a function.
@overload
def group(name: _AnyCallable) -> RichGroup: ...
@overload
def group(
    name: Optional[str] = None,
    *,
    cls: Type[G],
    commands: MutableMapping[str, click.Command] | Sequence[click.Command] | None = ...,
    invoke_without_command: bool = ...,
    no_args_is_help: bool | None = ...,
    subcommand_metavar: str | None = ...,
    chain: bool = ...,
    result_callback: Callable[..., Any] | None = ...,
    context_settings: RichContextSettingsDict,
    callback: Callable[..., Any] | None = ...,
    params: list[click.Parameter] | None = ...,
    help: str | None = ...,
    epilog: str | None = ...,
    short_help: str | None = ...,
    options_metavar: str | None = ...,
    add_help_option: bool = ...,
    hidden: bool = ...,
    deprecated: bool | str = ...,
    aliases: Optional[Iterable[str]] = ...,
    panels: Optional[List[RichPanel[Any, Any]]] = ...,
) -> Callable[[_AnyCallable], G]: ...
@overload
def group(
    name: Optional[str] = ...,
    *,
    cls: None,
    commands: MutableMapping[str, click.Command] | Sequence[click.Command] | None = ...,
    invoke_without_command: bool = ...,
    no_args_is_help: bool | None = ...,
    subcommand_metavar: str | None = ...,
    chain: bool = ...,
    result_callback: Callable[..., Any] | None = ...,
    context_settings: MutableMapping[str, Any] | None = ...,
    callback: Callable[..., Any] | None = ...,
    params: list[click.Parameter] | None = ...,
    help: str | None = ...,
    epilog: str | None = ...,
    short_help: str | None = ...,
    options_metavar: str | None = ...,
    add_help_option: bool = ...,
    hidden: bool = ...,
    deprecated: bool | str = ...,
    aliases: Optional[Iterable[str]] = ...,
    panels: Optional[List[RichPanel[Any, Any]]] = ...,
) -> Callable[[_AnyCallable], RichGroup]: ...
@overload
def group(
    name: Optional[str] = None,
    *,
    cls: Type[G],
    commands: MutableMapping[str, click.Command] | Sequence[click.Command] | None = ...,
    invoke_without_command: bool = ...,
    no_args_is_help: bool | None = ...,
    subcommand_metavar: str | None = ...,
    chain: bool = ...,
    result_callback: Callable[..., Any] | None = ...,
    context_settings: MutableMapping[str, Any] | None = ...,
    callback: Callable[..., Any] | None = ...,
    params: list[click.Parameter] | None = ...,
    help: str | None = ...,
    epilog: str | None = ...,
    short_help: str | None = ...,
    options_metavar: str | None = ...,
    add_help_option: bool = ...,
    hidden: bool = ...,
    deprecated: bool | str = ...,
    aliases: Optional[Iterable[str]] = ...,
    panels: Optional[List[RichPanel[Any, Any]]] = ...,
) -> Callable[[_AnyCallable], G]: ...
@overload
def group(
    name: Optional[str] = ...,
    *,
    cls: None,
    commands: MutableMapping[str, click.Command] | Sequence[click.Command] | None = ...,
    invoke_without_command: bool = ...,
    no_args_is_help: bool | None = ...,
    subcommand_metavar: str | None = ...,
    chain: bool = ...,
    result_callback: Callable[..., Any] | None = ...,
    context_settings: RichContextSettingsDict,
    callback: Callable[..., Any] | None = ...,
    params: list[click.Parameter] | None = ...,
    help: str | None = ...,
    epilog: str | None = ...,
    short_help: str | None = ...,
    options_metavar: str | None = ...,
    add_help_option: bool = ...,
    hidden: bool = ...,
    deprecated: bool | str = ...,
    aliases: Optional[Iterable[str]] = ...,
    panels: Optional[List[RichPanel[Any, Any]]] = ...,
) -> Callable[[_AnyCallable], RichGroup]: ...

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
) -> Union[click.Group, Callable[[_AnyCallable], Union[RichGroup, G]]]: ...
def argument(
    *param_decls: str,
    cls: Optional[Type[click.Argument]] = None,
    type: ParamType | Any | None = None,
    required: bool = False,
    default: Any | Callable[[], Any] | None = None,
    callback: Callable[[click.Context, click.Parameter, Any], Any] | None = None,
    nargs: int | None = None,
    multiple: bool = False,
    metavar: str | None = None,
    expose_value: bool = True,
    is_eager: bool = False,
    envvar: str | Sequence[str] | None = None,
    shell_complete: Callable[[click.Context, click.Parameter, str], list[CompletionItem] | list[str]] | None = None,
    deprecated: bool | str = False,
    panel: Optional[Union[str, List[str]]] = None,
    help: Optional[str] = None,
    help_style: Optional[StyleType] = None,
    **attrs: Any,
) -> Callable[[FC], FC]: ...
def option(
    *param_decls: str,
    cls: Optional[Type[click.Option]] = None,
    type: Optional[Union["ParamType", Any]] = None,
    required: bool = False,
    default: Optional[Union[Any, Callable[[], Any]]] = None,
    callback: Optional[Callable[[click.Context, click.Parameter, Any], Any]] = None,
    nargs: Optional[int] = None,
    multiple: bool = False,
    metavar: Optional[str] = None,
    expose_value: bool = True,
    is_eager: bool = False,
    envvar: Optional[Union[str, Sequence[str]]] = None,
    shell_complete: Optional[
        Callable[
            [click.Context, click.Parameter, str],
            Union[List[CompletionItem], List[str]],
        ]
    ] = None,
    show_default: Optional[Union[bool, str]] = False,
    prompt: Union[bool, str] = False,
    confirmation_prompt: Union[bool, str] = False,
    prompt_required: bool = True,
    hide_input: bool = False,
    is_flag: Optional[bool] = None,
    flag_value: Optional[Any] = None,
    count: bool = False,
    allow_from_autoenv: bool = True,
    help: Optional[str] = None,
    hidden: bool = False,
    show_choices: bool = True,
    show_envvar: bool = False,
    panel: Optional[Union[str, List[str]]] = None,
    help_style: Optional[StyleType] = None,
    **attrs: Any,
) -> Callable[[FC], FC]: ...
def password_option(
    *param_decls: str,
    cls: Optional[Type[click.Option]] = None,
    type: Optional[Union["ParamType", Any]] = None,
    required: bool = False,
    default: Optional[Union[Any, Callable[[], Any]]] = None,
    callback: Optional[Callable[[click.Context, click.Parameter, Any], Any]] = None,
    nargs: Optional[int] = None,
    multiple: bool = False,
    metavar: Optional[str] = None,
    expose_value: bool = True,
    is_eager: bool = False,
    envvar: Optional[Union[str, Sequence[str]]] = None,
    shell_complete: Optional[
        Callable[
            [click.Context, click.Parameter, str],
            Union[List[CompletionItem], List[str]],
        ]
    ] = None,
    show_default: Optional[Union[bool, str]] = False,
    prompt: Union[bool, str] = False,
    confirmation_prompt: Union[bool, str] = False,
    prompt_required: bool = True,
    hide_input: bool = False,
    is_flag: Optional[bool] = None,
    flag_value: Optional[Any] = None,
    count: bool = False,
    allow_from_autoenv: bool = True,
    help: Optional[str] = None,
    hidden: bool = False,
    show_choices: bool = True,
    show_envvar: bool = False,
    panel: Optional[Union[str, List[str]]] = None,
    help_style: Optional[StyleType] = None,
    **attrs: Any,
) -> Callable[[FC], FC]: ...
def version_option(
    version: Optional[str] = None,
    *param_decls: str,
    package_name: Optional[str] = None,
    prog_name: Optional[str] = None,
    message: Optional[str] = None,
    cls: Optional[Type[click.Option]] = None,
    type: Optional[Union["ParamType", Any]] = None,
    required: bool = False,
    default: Optional[Union[Any, Callable[[], Any]]] = None,
    callback: Optional[Callable[[click.Context, click.Parameter, Any], Any]] = None,
    nargs: Optional[int] = None,
    multiple: bool = False,
    metavar: Optional[str] = None,
    expose_value: bool = True,
    is_eager: bool = False,
    envvar: Optional[Union[str, Sequence[str]]] = None,
    shell_complete: Optional[
        Callable[
            [click.Context, click.Parameter, str],
            Union[List[CompletionItem], List[str]],
        ]
    ] = None,
    show_default: Optional[Union[bool, str]] = False,
    prompt: Union[bool, str] = False,
    confirmation_prompt: Union[bool, str] = False,
    prompt_required: bool = True,
    hide_input: bool = False,
    is_flag: Optional[bool] = None,
    flag_value: Optional[Any] = None,
    count: bool = False,
    allow_from_autoenv: bool = True,
    help: Optional[str] = None,
    hidden: bool = False,
    show_choices: bool = True,
    show_envvar: bool = False,
    panel: Optional[Union[str, List[str]]] = None,
    help_style: Optional[StyleType] = None,
    **attrs: Any,
) -> Callable[[FC], FC]: ...
def help_option(
    *param_decls: str,
    cls: Optional[Type[click.Option]] = None,
    type: Optional[Union["ParamType", Any]] = None,
    required: bool = False,
    default: Optional[Union[Any, Callable[[], Any]]] = None,
    callback: Optional[Callable[[click.Context, click.Parameter, Any], Any]] = None,
    nargs: Optional[int] = None,
    multiple: bool = False,
    metavar: Optional[str] = None,
    expose_value: bool = True,
    is_eager: bool = False,
    envvar: Optional[Union[str, Sequence[str]]] = None,
    shell_complete: Optional[
        Callable[
            [click.Context, click.Parameter, str],
            Union[List[CompletionItem], List[str]],
        ]
    ] = None,
    show_default: Optional[Union[bool, str]] = False,
    prompt: Union[bool, str] = False,
    confirmation_prompt: Union[bool, str] = False,
    prompt_required: bool = True,
    hide_input: bool = False,
    is_flag: Optional[bool] = None,
    flag_value: Optional[Any] = None,
    count: bool = False,
    allow_from_autoenv: bool = True,
    help: Optional[str] = None,
    hidden: bool = False,
    show_choices: bool = True,
    show_envvar: bool = False,
    panel: Optional[Union[str, List[str]]] = None,
    help_style: Optional[StyleType] = None,
    **attrs: Any,
) -> Callable[[FC], FC]: ...
def confirmation_option(
    *param_decls: str,
    cls: Optional[Type[click.Option]] = None,
    type: Optional[Union["ParamType", Any]] = None,
    required: bool = False,
    default: Optional[Union[Any, Callable[[], Any]]] = None,
    callback: Optional[Callable[[click.Context, click.Parameter, Any], Any]] = None,
    nargs: Optional[int] = None,
    multiple: bool = False,
    metavar: Optional[str] = None,
    expose_value: bool = True,
    is_eager: bool = False,
    envvar: Optional[Union[str, Sequence[str]]] = None,
    shell_complete: Optional[
        Callable[
            [click.Context, click.Parameter, str],
            Union[List[CompletionItem], List[str]],
        ]
    ] = None,
    show_default: Optional[Union[bool, str]] = False,
    prompt: Union[bool, str] = False,
    confirmation_prompt: Union[bool, str] = False,
    prompt_required: bool = True,
    hide_input: bool = False,
    is_flag: Optional[bool] = None,
    flag_value: Optional[Any] = None,
    count: bool = False,
    allow_from_autoenv: bool = True,
    help: Optional[str] = None,
    hidden: bool = False,
    show_choices: bool = True,
    show_envvar: bool = False,
    panel: Optional[Union[str, List[str]]] = None,
    help_style: Optional[StyleType] = None,
    **attrs: Any,
) -> Callable[[FC], FC]: ...

# This is a way to trick PyCharm into adding autocompletion for typed dicts
# without jeopardizing anything on Mypy's side.
@overload
def rich_config(
    help_config: RichHelpConfigurationDict,
    *,
    console: Optional[Console] = ...,
) -> Callable[[FC], FC]: ...
@overload
def rich_config(
    help_config: Optional[Union[Dict[str, Any], RichHelpConfigurationDict, RichHelpConfiguration]] = ...,
    *,
    console: Optional[Console] = ...,
) -> Callable[[FC], FC]: ...
def rich_config(
    help_config: Optional[Union[Dict[str, Any], RichHelpConfigurationDict, RichHelpConfiguration]] = None,
    *,
    console: Optional[Console] = None,
) -> Callable[[FC], FC]: ...
@overload
def option_panel(
    name: str,
    cls: Type[RichPanel[click.Parameter]] = ...,
    *,
    options: Optional[List[str]] = ...,
    help: Optional[str] = ...,
    help_style: Optional[StyleType] = ...,
    table_styles: TableKwargs,
    panel_styles: PanelKwargs,
    column_types: Optional[List[OptionColumnType]] = ...,
    inline_help_in_title: Optional[bool] = ...,
    title_style: Optional[StyleType] = ...,
) -> Callable[[FC], FC]: ...
@overload
def option_panel(
    name: str,
    cls: Type[RichPanel[click.Parameter]] = ...,
    *,
    options: Optional[List[str]] = ...,
    help: Optional[str] = ...,
    help_style: Optional[StyleType] = ...,
    table_styles: Union[Dict[str, Any], None] = ...,
    panel_styles: Union[Dict[str, Any], None] = ...,
    column_types: Optional[List[OptionColumnType]] = ...,
    inline_help_in_title: Optional[bool] = ...,
    title_style: Optional[StyleType] = ...,
) -> Callable[[FC], FC]: ...
def option_panel(
    name: str,
    cls: Type[RichPanel[click.Parameter]] = RichOptionPanel,
    *,
    options: Optional[List[str]] = None,
    help: Optional[str] = None,
    help_style: Optional[StyleType] = None,
    table_styles: Union[TableKwargs, Dict[str, Any], None] = None,
    panel_styles: Union[PanelKwargs, Dict[str, Any], None] = None,
    column_types: Optional[List[OptionColumnType]] = None,
    inline_help_in_title: Optional[bool] = None,
    title_style: Optional[StyleType] = None,
) -> Callable[[FC], FC]: ...
@overload
def command_panel(
    name: str,
    cls: Type[RichPanel[click.Parameter]] = RichOptionPanel,
    *,
    commands: Optional[List[str]] = ...,
    help: Optional[str] = ...,
    help_style: Optional[StyleType] = ...,
    table_styles: TableKwargs,
    panel_styles: PanelKwargs,
    column_types: Optional[List[CommandColumnType]] = ...,
    inline_help_in_title: Optional[bool] = ...,
    title_style: Optional[StyleType] = ...,
) -> Callable[[FC], FC]: ...
@overload
def command_panel(
    name: str,
    cls: Type[RichPanel[click.Parameter]] = RichOptionPanel,
    *,
    commands: Optional[List[str]] = ...,
    help: Optional[str] = ...,
    help_style: Optional[StyleType] = ...,
    table_styles: Optional[Dict[str, Any]] = ...,
    panel_styles: Optional[Dict[str, Any]] = ...,
    column_types: Optional[List[CommandColumnType]] = ...,
    inline_help_in_title: Optional[bool] = ...,
    title_style: Optional[StyleType] = ...,
) -> Callable[[FC], FC]: ...
@overload
def command_panel(
    name: str,
    cls: Type[RichPanel[click.Parameter]] = RichOptionPanel,
    *,
    commands: Optional[List[str]] = ...,
    help: Optional[str] = ...,
    help_style: Optional[StyleType] = ...,
    table_styles: None,
    panel_styles: None,
    column_types: Optional[List[CommandColumnType]] = ...,
    inline_help_in_title: Optional[bool] = ...,
    title_style: Optional[StyleType] = ...,
) -> Callable[[FC], FC]: ...
def command_panel(
    name: str,
    cls: Type[RichPanel[click.Parameter]] = RichOptionPanel,
    *,
    commands: Optional[List[str]] = None,
    help: Optional[str] = None,
    help_style: Optional[StyleType] = None,
    table_styles: Optional[Dict[str, Any]] = None,
    panel_styles: Optional[Dict[str, Any]] = None,
    column_types: Optional[List[CommandColumnType]] = None,
    inline_help_in_title: Optional[bool] = None,
    title_style: Optional[StyleType] = None,
) -> Callable[[FC], FC]: ...

PSpec = ParamSpec("PSpec")
R = TypeVar("R")

def pass_context(f: Callable[Concatenate[RichContext, PSpec], R]) -> Callable[PSpec, R]: ...

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
