"""The command line interface."""

from __future__ import annotations

import os
import sys
import warnings
from contextlib import contextmanager
from functools import wraps
from gettext import gettext
from importlib import (
    import_module,
    metadata,  # type: ignore[import,unused-ignore]
)
from typing import Any, Dict, Generator, List, Literal, Optional, Tuple

import click
from click.core import ParameterSource

from rich_click.decorators import argument as _rich_argument
from rich_click.decorators import command as _rich_command
from rich_click.decorators import option as _rich_option
from rich_click.decorators import option_panel, pass_context
from rich_click.decorators import version_option as _rich_version_option
from rich_click.patch import patch as _patch
from rich_click.rich_click_theme import COLORS, FORMATS, RichClickThemeNotFound, get_theme
from rich_click.rich_context import RichContext
from rich_click.rich_help_configuration import RichHelpConfiguration


DISABLE_WARNINGS_NOTE = (
    "[red]You can pass [b]--suppress-warnings[/b] to the rich-click CLI"
    " or set the [b]RICH_CLICK_CLI_SUPPRESS_WARNINGS[/b] environment variable"
    " to disable this message.[/red]"
)


def entry_points(*, group: str) -> "metadata.EntryPoints":  # type: ignore[name-defined]
    """entry_points function that is compatible with Python 3.7+."""
    if sys.version_info >= (3, 10):
        return metadata.entry_points(group=group)

    epg = metadata.entry_points()

    return epg.get(group, [])


@wraps(_patch)
def patch(*args: Any, **kwargs: Any) -> None:  # noqa: D103
    import warnings

    warnings.warn(
        "`rich_click.cli.patch()` has moved to `rich_click.patch.patch()`."
        " Importing `patch()` from `rich_click.cli` is deprecated; please import from `rich_click.patch` instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    return _patch(*args, **kwargs)


class _RichHelpConfigurationParamType(click.ParamType):
    name = "JSON"

    def __repr__(self) -> str:
        return "JSON"

    def convert(
        self,
        value: Optional[str],
        param: Optional[click.Parameter],
        ctx: Optional[click.Context],
    ) -> Optional[Dict[str, Any]]:
        if value is None:
            return value
        else:
            try:
                import json

                if value.startswith("@"):
                    with open(value[1:], "r") as f:
                        data = json.load(f)
                else:
                    data = json.loads(value)
                if not isinstance(data, dict):
                    raise ValueError("--rich-config needs to be a JSON.")
                return data
            except Exception as e:
                # In normal circumstances, a bad arg to a CLI doesn't
                # prevent the help text from rendering.
                if ctx is not None and ctx.params.get("show_help", False):
                    print(ctx.get_help())
                    ctx.exit()
                else:
                    raise e


def _get_module_path_and_function_name(script: str, suppress_warnings: bool) -> Tuple[str, str]:
    _selected: List[str] = []
    module_path = ""
    function_name = ""

    for s in entry_points(group="console_scripts"):
        if script == s.name:
            if not _selected:
                module_path, function_name = s.value.split(":", 1)
                if " [" in function_name and function_name.endswith("]"):
                    function_name = function_name.split(" [")[0]
            if suppress_warnings:
                break
            if s.value not in _selected:
                _selected.append(s.value)

    if len(_selected) > 1 and not suppress_warnings:
        # This is an extremely rare edge case that comes up when the user sets the PYTHONPATH themselves.
        if script in sys.argv:
            _args = sys.argv.copy()
            _args[_args.index(script)] = f"{module_path}:{function_name}"
        else:
            _args = ["rich-click", f"{module_path}:{function_name}"]

        import rich

        rich.print(
            f"[red]WARNING: Multiple entry_points correspond with script '{script}': {_selected!r}."
            "\nThis can happen when an 'egg-info' directory exists, you're using a virtualenv,"
            " and you have set a custom PYTHONPATH."
            f"\n\nThe selected script is '{module_path}:{function_name}', which is being executed now."
            "\n\nIt is safer and recommended that you specify the MODULE:CLICK_COMMAND"
            f" ('{module_path}:{function_name}') instead of the script ('{script}'), like this:[/]"
            f"\n\n>>> {' '.join(_args)}"
            f"\n\n{DISABLE_WARNINGS_NOTE}",
        )

    if ":" in script and not module_path:
        # the path to a function was passed
        module_path, function_name = script.split(":", 1)

    if not module_path:
        module_path = script

    return module_path, function_name


def list_themes(ctx: RichContext, param: click.Parameter, value: bool) -> None:
    """Print all themes."""
    if value:
        from rich import box
        from rich.console import Console
        from rich.containers import Renderables
        from rich.padding import Padding
        from rich.panel import Panel
        from rich.table import Table
        from rich.text import Text

        formatter = ctx.make_formatter()

        console = Console(
            color_system=formatter.config.color_system,
            force_terminal=formatter.config.force_terminal,
            width=formatter.config.width,
            legacy_windows=formatter.config.legacy_windows,
        )

        found = False
        c, f = None, None

        selected = os.getenv("RICH_CLICK_THEME")
        if selected is not None:
            if selected.startswith("{"):
                import json

                try:
                    data = json.loads(selected)
                    _theme = data.get("theme")
                except Exception:
                    _theme = None
            else:
                _theme = selected
            if _theme:
                try:
                    get_theme(_theme)
                except RichClickThemeNotFound:
                    found = False
                else:
                    found = True
                    if "-" in _theme:
                        c, f, *_ = _theme.split("-")
                    elif _theme in FORMATS:
                        f = _theme
                        found = True
                    elif _theme in COLORS:
                        c = _theme
                        found = True

        if selected is None:
            selected_text = "[red bold]RICH_CLICK_THEME[/] is not set"
        elif not found:
            selected_text = f"[red bold]RICH_CLICK_THEME[/]=[red]{selected!r}[/] is not a valid theme."
        else:
            selected_text = (
                f"[blue bold]RICH_CLICK_THEME[/blue bold]=[blue]{selected!r}[/blue]"
                f"\n\n[b]Colors:[/b] {c or '[dim](null)[/]'}"
                f"\n[b]Format:[/b] {f or '[dim](null)[/]'}"
            )

        colors = Table(
            "",
            "Name",
            "Colors",
            "Description",
            padding=(0, 1),
            border_style="dim",
            box=box.SIMPLE_HEAD,
            show_lines=True,
            expand=True,
        )
        colors.columns[0].max_width = 1
        colors.columns[1].style = "bold"
        for r in COLORS.values():
            if r.hidden:
                continue
            selected_row = c == r.name or (c is None and r.name == "default")
            colors.add_row(
                "*" if selected_row else "",
                r.name,
                " ".join([f"[{_}]▓▓[/]" for _ in r.primary_colors[:3]]),
                r.description,
            )

        formats = Table(
            "",
            "Name",
            "Description",
            padding=(0, 1),
            border_style="dim",
            box=box.SIMPLE_HEAD,
            show_lines=True,
            expand=True,
        )
        formats.columns[1].style = "bold"
        for r in FORMATS.values():
            selected_row = f == r.name or (f is None and r.name == "box")
            formats.add_row("*" if selected_row else "", r.name, r.description)

        how_to_use = Padding(
            Text("\n\n", overflow="fold").join(
                [
                    Text.from_markup("[b]Themes[/b] are an easy way to style a rich-click CLI."),
                    Text.from_markup(
                        "As an end-user of CLIs, you can set the [blue b]RICH_CLICK_THEME=[/blue b] env var"
                        " to style all rich-click CLIs you use."
                    ),
                    Text.from_markup(
                        "As a developer, you can add a theme to your CLI with one line of code:"
                        " [green b]@click.rich_config({'theme': 'name'})[/green b]."
                    ),
                    Text.from_markup(
                        "Themes consist of [b]Color Palettes[/b] and [b]Formats[/b], which can be mixed and matched:"
                        " The name of a full theme has the following schema: [red]{color_palette}-{format}[/red]."
                    ),
                    Text.from_markup(
                        "For example, the [b]forest-slim[/b] theme uses the [b]forest[/b]"
                        " color palette and the [b]slim[/b] format."
                    ),
                ]
            ),
            pad=1,
            expand=False,
        )

        console.print(
            Panel(
                Renderables(
                    [
                        Panel(how_to_use, title="How to use", width=100),
                        Panel(Padding(selected_text, pad=1), title="Local user setting", width=100),
                        Panel(colors, title="Color Palettes"),
                        Panel(formats, title="Formats"),
                    ]
                ),
                expand=False,
                box=box.SIMPLE,
            )
        )
        ctx.exit(0)


@_rich_command(
    "rich-click",
    context_settings={"allow_interspersed_args": False},
    add_help_option=False,
)
@_rich_argument(
    "script_and_args",
    nargs=-1,
    metavar="SCRIPT | MODULE[:CLICK_COMMAND] ...",
    help="The script you want to run. If it's a Click CLI and you are rendering help text;"
    " then the help text will render"
    " [#FF6B6B bold]r[/][#FF8E53 bold]i[/][#FFB347 bold]c[/][#4ECDC4 bold]h[/]"
    "[#45B7D1 bold]l[/][#74B9FF bold]y[/]. Otherwise, the script will run normally.",
)
@_rich_option(
    "--theme",
    "-t",
    help="Set the theme to render the CLI with.",
    metavar="THEME",
)
@_rich_option(
    "--rich-config",
    "-c",
    type=_RichHelpConfigurationParamType(),
    help="Keyword arguments to pass into the [de]RichHelpConfiguration()[/] used"
    " to render the help text of the command. You can pass either a JSON directly, or a file"
    " prefixed with `@` (for example: '@rich_config.json'). Note that the --rich-config"
    " option is also used to render this help text you're reading right now!",
)
@_rich_option(
    "--output",
    "-o",
    type=click.Choice(["html", "svg", "text"], case_sensitive=False),
    help="Optionally render help text as HTML or SVG or plain text. By default, help text is rendered normally.",
)
@_rich_option(
    "--errors-in-output-format",
    is_flag=True,
    panel="Advanced Options",
    help="If set, forces the CLI to render CLI error messages"
    " in the format specified by the --output option."
    " By default, error messages render normally, i.e. they are not converted to html or svg.",
)
@_rich_option(
    "--suppress-warnings/--do-not-suppress-warnings",
    is_flag=True,
    default=False,
    envvar="RICH_CLICK_CLI_SUPPRESS_WARNINGS",
    show_envvar=True,
    panel="Advanced Options",
    help="Suppress warnings when there are conflicting entry_points. This situation is extremely rare.",
)
@_rich_option(
    "--patch-rich-click/--no-patch-rich-click",
    is_flag=True,
    default=True,
    panel="Advanced Options",
    help="If set, patch [reverse][option][b]rich_click.Command[/][/][/],"
    " not just [reverse][option][b]click.Command[/][/][/].",
)
@_rich_option(
    "--themes",
    help="List all available themes and exit.",
    panel="Extra",
    callback=list_themes,  # type: ignore[arg-type,unused-ignore]
    expose_value=False,
    is_flag=True,
)
@_rich_version_option(panel="Extra")
@_rich_option(
    # The rich-click CLI uses a special implementation of --help,
    # which is aware of the --rich-config object.
    "--help",
    "-h",
    "show_help",
    is_eager=True,
    is_flag=True,
    help=gettext("Show this message and exit."),
    panel="Extra",
    # callback=help_callback
)
@option_panel("Options")
@option_panel("Advanced Options")
@option_panel("Extra")
@pass_context
def main(
    ctx: RichContext,
    script_and_args: Tuple[str, ...],
    theme: str,
    output: Literal[None, "html", "svg"],
    errors_in_output_format: bool,
    suppress_warnings: bool,
    patch_rich_click: bool,
    rich_config: Optional[Dict[str, Any]],
    show_help: bool,
) -> None:
    """
    The [link=https://github.com/ewels/rich-click]rich-click[/] CLI provides
    [#FF6B6B bold]r[/][#FF8E53 bold]i[/][#FFB347 bold]c[/][#4ECDC4 bold]h[/][#45B7D1 bold]l[/][#74B9FF bold]y[/]
    formatted help output from any
    tool using [link=https://click.palletsprojects.com/]click[/], formatted with
    [link=https://github.com/Textualize/rich]rich[/].

    Full docs here: [link=https://ewels.github.io/rich-click/latest/documentation/rich_click_cli/]\
https://ewels.github.io/rich-click/latest/documentation/rich_click_cli/[/]

    The rich-click command line tool can be prepended before any Python package
    using native click to provide attractive richified click help output.

    For example, if you have a package called [argument]my_package[/] that uses click,
    you can run:

    >>> [command]rich-click[/] [argument]my_package[/] [option]--help[/]

    When not rendering help text, the provided command will run normally,
    so it is safe to replace calls to the tool with [command]rich-click[/] in front, e.g.:

    >>> [command]rich-click[/] [argument]my_package[/] [argument]cmd[/] [option]--foo[/] 3
    """  # noqa: D401
    try:
        if rich_config:
            if theme:
                rich_config.setdefault("theme", theme)
                import rich_click.rich_click as rc

                rc._THEME_FROM_CLI = theme
            cfg = RichHelpConfiguration.load_from_globals(**rich_config)
        elif theme:
            import rich_click.rich_click as rc

            rc._THEME_FROM_CLI = theme
            cfg = RichHelpConfiguration.load_from_globals(theme=theme)
        else:
            cfg = RichHelpConfiguration.load_from_globals()
    except RichClickThemeNotFound as e:
        raise click.ClickException(e.args[0] if e.args else "Theme not found")

    if (show_help or not script_and_args) and not ctx.resilient_parsing:
        cfg.use_markdown = False
        cfg.use_rich_markup = True
        cfg.text_markup = "rich"
        if cfg.show_arguments is None:
            cfg.show_arguments = False
        ctx.help_config = cfg
        print(ctx.get_help())
        if not show_help and not script_and_args:
            ctx.exit(2)
        ctx.exit(0)

    @contextmanager
    def patch_ctx() -> Generator[None, None, None]:
        if ctx.get_parameter_source("typer") != ParameterSource.ENVIRONMENT:
            try:
                with warnings.catch_warnings():
                    warnings.filterwarnings("error", category=ImportWarning)
                    yield
            except ImportWarning as e:
                if not suppress_warnings and any("Typer" in a for a in e.args):
                    import rich

                    rich.print(
                        f"[red]WARNING: Attempted to patch Typer, but Typer is not installed.[/red]"
                        f"\n\n{DISABLE_WARNINGS_NOTE}"
                    )
        else:
            yield

    # patch click before importing the program function
    with patch_ctx():
        _patch(rich_config=cfg, patch_rich_click=patch_rich_click)

    script, *args = script_and_args

    # PYTHONPATH can change output of entry_points(group="console_scripts") in rare cases,
    # so we want to run the whole search with this.
    _sys_path = sys.path.copy()
    sys.path.append(os.path.abspath("."))
    try:
        module_path, function_name = _get_module_path_and_function_name(script, suppress_warnings)
    finally:
        sys.path = _sys_path

    if function_name:

        def function() -> None:
            try:
                module = import_module(module_path)
            except ModuleNotFoundError:
                try:
                    # Import can fail if module is relative to root dir
                    # and PYTHONPATH does not include ".".
                    sys.path.append(os.path.abspath("."))
                    module = import_module(module_path)
                except ModuleNotFoundError as e:
                    raise click.ClickException(e.args[0] if e.args else "Unknown error")
            try:
                f = getattr(module, function_name)
            except AttributeError:
                raise click.ClickException(f"Module '{module_path}' has no attribute '{function_name}'.")
            f()

    elif module_path.endswith(".py"):

        def function() -> None:
            import runpy

            try:
                runpy.run_path(module_path, run_name="__main__")
            except ImportError as e:
                raise click.ClickException(e.args[0] if e.args else "Unknown error")

    else:

        def function() -> None:
            import runpy

            try:
                runpy.run_module(module_path, run_name="__main__")
            except ImportError:
                # Import can fail if module is relative to root dir
                # and PYTHONPATH does not include ".".
                sys.path.append(os.path.abspath("."))
                try:
                    runpy.run_module(module_path, run_name="__main__")
                except ImportError as e:
                    raise click.ClickException(e.args[0] if e.args else "Unknown error")

    prog = module_path.split(".", 1)[0]
    sys.argv = [prog, *args]

    RichContext.export_console_as = ctx.export_console_as = output
    RichContext.errors_in_output_format = ctx.errors_in_output_format = errors_in_output_format
    function()
