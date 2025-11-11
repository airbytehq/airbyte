"""The command line interface."""

from __future__ import annotations

# ruff: noqa: D103
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Type, Union

from click import Argument, Command, Group, Option

from rich_click.decorators import command as _rich_command
from rich_click.decorators import group as _rich_group
from rich_click.rich_command import RichCommand, RichCommandCollection, RichGroup, RichMultiCommand
from rich_click.rich_context import RichContext
from rich_click.rich_help_configuration import RichHelpConfiguration
from rich_click.rich_help_formatter import RichHelpFormatter


if TYPE_CHECKING:
    import typer.core


__TyperGroup: Type["typer.core.TyperGroup"]
__TyperCommand: Type["typer.core.TyperCommand"]
__TyperArgument: Type["typer.core.TyperArgument"]
__TyperOption: Type["typer.core.TyperOption"]


class _PatchedTyperContext(RichContext):

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        RichContext.__init__(self, *args, **kwargs)

    def make_formatter(self, error_mode: bool = False) -> RichHelpFormatter:
        """Create the Rich Help Formatter."""
        formatter = super().make_formatter(error_mode=error_mode)
        if hasattr(self.command, "rich_markup_mode") and self.command.rich_markup_mode == "rich":
            formatter.config.text_markup = "rich"
            formatter.config.text_emojis = True
        return formatter

    def get_help(self) -> str:
        """
        Format the help into a string and returns it.

        Calls :meth:`format_help` internally.
        """
        import typer.core
        from typer.models import DefaultPlaceholder

        from rich_click.rich_panel import RichCommandPanel

        if isinstance(self.command, RichGroup):
            command_panels: Dict[str, List[str]] = {}
            for cmd_name in self.command.commands:
                cmd = self.command.commands[cmd_name]
                if (
                    isinstance(cmd, (typer.core.TyperCommand, typer.core.TyperGroup))
                    and cmd.rich_help_panel is not None
                    and not isinstance(cmd.rich_help_panel, DefaultPlaceholder)
                ):
                    command_panels.setdefault(cmd.rich_help_panel, [])
                    command_panels[cmd.rich_help_panel].append(cmd_name)
            for name, commands in command_panels.items():
                self.command.add_panel(RichCommandPanel(name, commands=commands))

        return super().get_help()


def _typer_command_init(
    self: Any, *args: Any, rich_help_panel: Union[str, None] = None, rich_markup_mode: Any = None, **kwargs: Any
) -> None:
    import typer.core

    globals().setdefault("__TyperCommand", typer.core.TyperCommand)
    global __TyperCommand

    super(__TyperCommand, self).__init__(*args, **kwargs)

    super(typer.core.TyperCommand, self).__init__(*args, **kwargs)
    self.rich_markup_mode = rich_markup_mode
    self.rich_help_panel = rich_help_panel
    if not hasattr(self, "_help_option"):
        self._help_option = None


def _typer_group_init(
    self: Any,
    *args: Any,
    rich_help_panel: Union[str, None] = None,
    rich_markup_mode: Any = None,
    suggest_commands: bool = True,
    **kwargs: Any,
) -> None:
    import typer.core

    globals().setdefault("__TyperGroup", typer.core.TyperGroup)
    global __TyperGroup

    super(__TyperGroup, self).__init__(*args, **kwargs)
    self.rich_markup_mode = rich_markup_mode
    self.rich_help_panel = rich_help_panel
    self.suggest_commands = suggest_commands
    self.panels = []
    self._alias_mapping = {}
    if not hasattr(self, "_help_option"):
        self._help_option = None


def _patch_typer_group(cls: Type[Group]) -> Type[Group]:
    cls.format_help = RichGroup.format_help  # type: ignore[assignment]
    cls.__init__ = _typer_group_init  # type: ignore[method-assign]
    cls.context_class = _PatchedTyperContext
    cls.panel = property(  # type: ignore[attr-defined]
        lambda self: self.rich_help_panel, lambda self, value: setattr(self, "rich_help_panel", value)
    )
    return cls


def _patch_typer_command(cls: Type[Command]) -> Type[Command]:
    cls.format_help = RichCommand.format_help  # type: ignore[assignment]
    cls.__init__ = _typer_command_init  # type: ignore[method-assign]
    cls.context_class = _PatchedTyperContext
    cls.panel = property(  # type: ignore[attr-defined]
        lambda self: self.rich_help_panel, lambda self, value: setattr(self, "rich_help_panel", value)
    )
    return cls


def _patch_typer_argument(cls: Type[Argument]) -> Type[Argument]:
    cls.panel = property(  # type: ignore[attr-defined]
        lambda self: self.rich_help_panel, lambda self, value: setattr(self, "rich_help_panel", value)
    )
    return cls


def _patch_typer_option(cls: Type[Option]) -> Type[Option]:
    cls.panel = property(  # type: ignore[attr-defined]
        lambda self: self.rich_help_panel, lambda self, value: setattr(self, "rich_help_panel", value)
    )
    return cls


class PatchMeta(type):
    def __init__(cls, name: str, bases: Tuple[type, ...], namespace: Dict[str, Any]) -> None:
        super().__init__(name, bases, namespace)
        if cls.__module__ in ["typer.core", "typer.main", "rich_click.patch"]:
            if name == "TyperGroup":
                _patch_typer_group(cls)  # type: ignore[arg-type]
            elif name == "TyperCommand":
                _patch_typer_command(cls)  # type: ignore[arg-type]
            elif name == "TyperOption":
                _patch_typer_option(cls)  # type: ignore[arg-type]
            elif name == "TyperArgument":
                _patch_typer_argument(cls)  # type: ignore[arg-type]


class _PatchedRichCommand(RichCommand, metaclass=PatchMeta):
    pass


class _PatchedRichMultiCommand(RichMultiCommand, _PatchedRichCommand):
    pass


class _PatchedRichCommandCollection(RichCommandCollection, _PatchedRichCommand):
    pass


class _PatchedRichGroup(RichGroup, _PatchedRichCommand):
    pass


# Options and Arguments don't need to be patched for base click CLIs.
# However, we need to intercept type.__init__ calls for Typer CLIs.


class _PatchedOption(Option, metaclass=PatchMeta):
    pass


class _PatchedArgument(Argument, metaclass=PatchMeta):
    pass


def rich_command(*args, **kwargs):  # type: ignore[no-untyped-def]
    kwargs.setdefault("cls", _PatchedRichCommand)
    kwargs["__rich_click_cli_patch"] = True
    return _rich_command(*args, **kwargs)


def rich_group(*args, **kwargs):  # type: ignore[no-untyped-def]
    kwargs.setdefault("cls", _PatchedRichGroup)
    kwargs["__rich_click_cli_patch"] = True
    return _rich_group(*args, **kwargs)


def patch(
    rich_config: Optional[RichHelpConfiguration] = None,
    *,
    patch_rich_click: bool = False,
    patch_typer: bool = False,
) -> None:
    """Patch Click internals to use rich-click types."""
    import warnings

    import rich_click._click_types_cache  # noqa: F401

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=DeprecationWarning)

        import click
        import click.core

        rich_click.rich_command.OVERRIDES_GUARD = True
        click.group = rich_group
        click.command = rich_command
        click.Group = _PatchedRichGroup  # type: ignore[misc]
        click.Command = _PatchedRichCommand  # type: ignore[misc]
        click.CommandCollection = _PatchedRichCommandCollection  # type: ignore[misc]
        click.Argument = _PatchedArgument  # type: ignore[misc]
        click.Option = _PatchedOption  # type: ignore[misc]

        click.core.Group = _PatchedRichGroup  # type: ignore[misc]
        click.core.Command = _PatchedRichCommand  # type: ignore[misc]
        click.core.CommandCollection = _PatchedRichCommandCollection  # type: ignore[misc]
        click.core.Argument = _PatchedArgument  # type: ignore[misc]
        click.core.Option = _PatchedOption  # type: ignore[misc]

        if hasattr(click, "MultiCommand"):
            click.MultiCommand = _PatchedRichMultiCommand  # type: ignore[assignment,misc,unused-ignore]
        if patch_rich_click:
            rich_click.group = rich_group
            rich_click.command = rich_command
            rich_click.Group = _PatchedRichGroup  # type: ignore[misc]
            rich_click.Command = _PatchedRichCommand  # type: ignore[misc]
            rich_click.CommandCollection = _PatchedRichCommandCollection  # type: ignore[misc]
            if hasattr(click, "MultiCommand"):
                rich_click.MultiCommand = _PatchedRichMultiCommand  # type: ignore[assignment,misc,unused-ignore]

    if patch_typer:
        globals()["patch_typer"]()

    if rich_config is not None:
        rich_config.dump_to_globals()


def patch_typer(rich_config: Optional[RichHelpConfiguration] = None) -> None:
    import typer.core
    import typer.main

    if not issubclass(typer.core.TyperCommand, _PatchedRichCommand):
        globals().setdefault("__TyperCommand", typer.core.TyperCommand)

        class _PatchedTyperCommand(_PatchedRichCommand, typer.core.TyperCommand):  # type: ignore[misc]
            pass

        typer.core.TyperCommand = typer.main.TyperCommand = _patch_typer_command(_PatchedTyperCommand)  # type: ignore[assignment,attr-defined,misc]

    if not issubclass(typer.core.TyperGroup, _PatchedRichGroup):
        globals().setdefault("__TyperGroup", typer.core.TyperGroup)

        class _PatchedTyperGroup(_PatchedRichGroup, typer.core.TyperGroup):  # type: ignore[misc]
            pass

        typer.core.TyperGroup = typer.main.TyperGroup = _patch_typer_group(_PatchedTyperGroup)  # type: ignore[assignment,attr-defined,misc]

    if not issubclass(typer.core.TyperOption, _PatchedOption):
        globals().setdefault("__TyperOption", typer.core.TyperOption)

        class _PatchedTyperOption(_PatchedOption, typer.core.TyperOption):
            pass

        typer.core.TyperOption = typer.main.TyperOption = _patch_typer_option(_PatchedTyperOption)  # type: ignore[assignment,attr-defined,misc]

    if not issubclass(typer.core.TyperArgument, _PatchedArgument):
        globals().setdefault("__TyperArgument", typer.core.TyperArgument)

        class _PatchedTyperArgument(_PatchedArgument, typer.core.TyperArgument):
            pass

        typer.core.TyperArgument = typer.main.TyperArgument = _patch_typer_argument(_PatchedTyperArgument)  # type: ignore[assignment,attr-defined,misc]

    if rich_config is not None:
        rich_config.dump_to_globals()


__all__ = ["patch", "patch_typer"]
