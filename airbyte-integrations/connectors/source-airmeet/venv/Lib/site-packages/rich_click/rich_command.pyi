from __future__ import annotations

from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Literal,
    MutableMapping,
    NoReturn,
    Optional,
    Sequence,
    Type,
    TypeVar,
    Union,
    overload,
)

import click

# Group, Command, and CommandCollection need to be imported directly,
# or else rich_click.cli.patch() causes a recursion error.
from click import Group
from rich.console import Console

from rich_click._internal_types import RichContextSettingsDict
from rich_click.rich_context import RichContext
from rich_click.rich_help_configuration import RichHelpConfiguration
from rich_click.rich_help_formatter import RichHelpFormatter
from rich_click.rich_help_rendering import RichPanelRow
from rich_click.rich_panel import RichCommandPanel, RichPanel

_AnyCallable = Callable[..., Any]
C = TypeVar("C", bound=click.Command)
G = TypeVar("G", bound=click.Group)

# TLDR: if a subcommand overrides one of the methods called by `RichCommand.format_help`,
# then the text won't render properly. The fix is to not rely on the composability of the API,
# and to instead force everything to use RichCommand's methods.
OVERRIDES_GUARD: bool = False

class RichCommand(click.Command):

    context_class: Type[RichContext] = RichContext
    _formatter: Optional[RichHelpFormatter] = None
    panels: List[RichPanel[Any, Any]]
    panel: Optional[str]
    aliases: Iterable[str]

    def __init__(
        self,
        *args: Any,
        aliases: Optional[Iterable[str]] = None,
        panels: Optional[List[RichPanel[Any, Any]]] = None,
        panel: Optional[str] = None,
        name: str | None,
        context_settings: MutableMapping[str, Any] | None = None,
        callback: Callable[..., Any] | None = None,
        params: list[click.Parameter] | None = None,
        help: str | None = None,
        epilog: str | None = None,
        short_help: str | None = None,
        options_metavar: str | None = "[OPTIONS]",
        add_help_option: bool = True,
        no_args_is_help: bool = False,
        hidden: bool = False,
        deprecated: bool | str = False,
    ) -> None: ...
    @property
    def console(self) -> Optional["Console"]: ...
    @property
    def help_config(self) -> Optional[RichHelpConfiguration]: ...
    def _generate_rich_help_config(self) -> RichHelpConfiguration: ...
    def _error_formatter(self) -> RichHelpFormatter: ...
    @overload
    def main(
        self,
        args: Sequence[str] | None = None,
        prog_name: str | None = None,
        complete_var: str | None = None,
        standalone_mode: Literal[True] = True,
        **extra: Any,
    ) -> NoReturn: ...
    @overload
    def main(
        self,
        args: Sequence[str] | None = None,
        prog_name: str | None = None,
        complete_var: str | None = None,
        standalone_mode: bool = ...,
        **extra: Any,
    ) -> Any: ...
    def main(
        self,
        args: Optional[Sequence[str]] = None,
        prog_name: Optional[str] = None,
        complete_var: Optional[str] = None,
        standalone_mode: bool = True,
        windows_expand_args: bool = True,
        **extra: Any,
    ) -> Any: ...
    def format_help(self, ctx: RichContext, formatter: RichHelpFormatter) -> None: ...
    def format_help_text(self, ctx: RichContext, formatter: RichHelpFormatter) -> None: ...
    def format_options(self, ctx: RichContext, formatter: RichHelpFormatter) -> None: ...
    def format_epilog(self, ctx: RichContext, formatter: RichHelpFormatter) -> None: ...
    def get_help_option(self, ctx: RichContext) -> Union[click.Option, None]: ...
    def get_rich_table_row(
        self,
        ctx: RichContext,
        formatter: RichHelpFormatter,
        panel: Optional[RichCommandPanel] = None,
    ) -> RichPanelRow: ...
    def add_panel(self, panel: "RichPanel[Any, Any]") -> None: ...
    def add_command_to_panel(
        self,
        command_name: str,
        panel_name: Union[str, Iterable[str]],
    ) -> None: ...

class RichGroup(RichCommand, click.Group):
    """
    Richly formatted click Group.

    Inherits click.Group and overrides help and error methods
    to print richly formatted output.
    """

    command_class: Optional[Type[RichCommand]] = RichCommand
    group_class: Optional[Union[Type[Group], Type[type]]] = type
    _alias_mapping: Dict[str, str]
    _panel_command_mapping: Dict[str, List[str]]

    def __init__(
        self,
        panels: Optional[List["RichPanel[Any, Any]"]] = None,
        aliases: Optional[Iterable[str]] = None,
        name: str | None = None,
        commands: MutableMapping[str, click.Command] | Sequence[click.Command] | None = None,
        invoke_without_command: bool = False,
        no_args_is_help: bool | None = None,
        subcommand_metavar: str | None = None,
        chain: bool = False,
        result_callback: Callable[..., Any] | None = None,
        context_settings: MutableMapping[str, Any] | None = None,
        callback: Callable[..., Any] | None = None,
        params: list[click.Parameter] | None = None,
        help: str | None = None,
        epilog: str | None = None,
        short_help: str | None = None,
        options_metavar: str | None = "[OPTIONS]",
        add_help_option: bool = True,
        hidden: bool = False,
        deprecated: bool | str = False,
    ) -> None: ...
    def format_commands(self, ctx: RichContext, formatter: RichHelpFormatter) -> None: ...
    def format_help(self, ctx: RichContext, formatter: RichHelpFormatter) -> None: ...
    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...

    # variant: no call, directly as decorator for a function.
    @overload
    def command(self, name: _AnyCallable) -> RichCommand: ...
    @overload
    def command(
        self,
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
        panel: Optional[str] = ...,
    ) -> Callable[[_AnyCallable], C]: ...
    @overload
    def command(
        self,
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
        panel: Optional[str] = ...,
    ) -> Callable[[_AnyCallable], RichCommand]: ...
    @overload
    def command(
        self,
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
        panel: Optional[str] = ...,
    ) -> Callable[[_AnyCallable], C]: ...
    @overload
    def command(
        self,
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
        panel: Optional[str] = ...,
        **attrs: Any,
    ) -> Callable[[_AnyCallable], RichCommand]: ...

    # variant: with positional name and with positional or keyword cls argument:
    # @command(namearg, CommandCls, ...) or @command(namearg, cls=CommandCls, ...)
    @overload
    def command(
        self,
        name: Optional[str],
        cls: Type[C],
        **attrs: Any,
    ) -> Callable[[_AnyCallable], C]: ...

    # variant: name omitted, cls _must_ be a keyword argument, @command(cls=CommandCls, ...)
    @overload
    def command(
        self,
        name: None = None,
        *,
        cls: Type[C],
        **attrs: Any,
    ) -> Callable[[_AnyCallable], C]: ...

    # variant: with optional string name, no cls argument provided.
    @overload
    def command(
        self, name: Optional[str] = ..., cls: None = None, **attrs: Any
    ) -> Callable[[_AnyCallable], RichCommand]: ...
    def command(
        self, name: Optional[str] = None, *, cls: Optional[Type[C]] = None, **kwargs: Any
    ) -> Callable[[_AnyCallable], Union[click.Command, C]]: ...
    @overload
    def group(self, name: _AnyCallable) -> RichGroup: ...
    @overload
    def group(
        self,
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
        panel: Optional[str] = ...,
    ) -> Callable[[_AnyCallable], G]: ...
    @overload
    def group(
        self,
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
        panel: Optional[str] = ...,
    ) -> Callable[[_AnyCallable], RichGroup]: ...
    @overload
    def group(
        self,
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
        panel: Optional[str] = ...,
    ) -> Callable[[_AnyCallable], G]: ...
    @overload
    def group(
        self,
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
        panel: Optional[str] = ...,
    ) -> Callable[[_AnyCallable], RichGroup]: ...

    # variant: with positional name and with positional or keyword cls argument:
    # @group(namearg, GroupCls, ...) or @group(namearg, cls=GroupCls, ...)
    @overload
    def group(
        self,
        name: Optional[str],
        cls: Type[G],
        **attrs: Any,
    ) -> Callable[[_AnyCallable], G]: ...

    # variant: name omitted, cls _must_ be a keyword argument, @group(cmd=GroupCls, ...)
    @overload
    def group(
        self,
        name: None = None,
        *,
        cls: Type[G],
        **attrs: Any,
    ) -> Callable[[_AnyCallable], G]: ...

    # variant: with optional string name, no cls argument provided.
    @overload
    def group(
        self, name: Optional[str] = ..., cls: None = None, **attrs: Any
    ) -> Callable[[_AnyCallable], RichGroup]: ...
    def group(
        self,
        name: Union[str, _AnyCallable, None] = None,
        cls: Optional[Type[G]] = None,
        **attrs: Any,
    ) -> Union[click.Group, Callable[[_AnyCallable], Union[RichGroup, G]]]: ...
    def get_command(self, ctx: RichContext, cmd_name: str) -> Optional[click.Command]: ...
    def add_command(
        self,
        cmd: click.Command,
        name: str | None = None,
        aliases: Optional[Iterable[str]] = None,
        panel: Optional[str] = None,
    ) -> None: ...
    def _handle_extras_add_command(
        self,
        cmd: click.Command,
        name: Optional[str] = None,
        aliases: Optional[Iterable[str]] = None,
        panel: Optional[Union[str, List[str]]] = None,
    ) -> None: ...

class RichMultiCommand(RichGroup, click.CommandCollection):
    pass

class RichCommandCollection(RichGroup, click.CommandCollection):
    pass
