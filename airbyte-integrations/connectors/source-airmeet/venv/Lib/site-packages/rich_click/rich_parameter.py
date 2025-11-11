from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any, List, Optional, Union

import click


if TYPE_CHECKING:
    from rich.columns import Columns
    from rich.style import StyleType

    from rich_click.rich_context import RichContext
    from rich_click.rich_help_formatter import RichHelpFormatter
    from rich_click.rich_help_rendering import RichPanelRow
    from rich_click.rich_panel import RichOptionPanel


class RichParameter(click.Parameter):
    r"""
    A parameter to a command comes in two versions: they are either
    :class:`Option`\s or :class:`Argument`\s.  Other subclasses are currently
    not supported by design as some of the internals for parsing are
    intentionally not finalized.
    """

    def __init__(
        self,
        *args: Any,
        panel: Optional[Union[str, List[str]]] = None,
        help: Optional[str] = None,
        help_style: Optional["StyleType"] = None,
        **kwargs: Any,
    ):
        """Create RichParameter instance."""
        super().__init__(*args, **kwargs)
        self.panel = panel

        if help:
            help = inspect.cleandoc(help)

            deprecated = kwargs.get("deprecated")
            if deprecated:
                deprecated_message = f"(DEPRECATED: {deprecated})" if isinstance(deprecated, str) else "(DEPRECATED)"
                help = help + deprecated_message if help is not None else deprecated_message

        self.help = help

        self.help_style = help_style

    def to_info_dict(self) -> dict[str, Any]:
        """
        Gather information that could be useful for a tool generating
        user-facing documentation.

        Use :meth:`click.Context.to_info_dict` to traverse the entire
        CLI structure.
        """
        info = super().to_info_dict()
        info.setdefault("help", self.help)
        return info

    def get_rich_help(self, ctx: "RichContext", formatter: "RichHelpFormatter") -> "Columns":
        """Get the rich help text for this parameter."""
        from rich_click.rich_help_rendering import get_help_parameter

        return get_help_parameter(self, ctx, formatter)

    def get_rich_table_row(
        self,
        ctx: "RichContext",
        formatter: "RichHelpFormatter",
        panel: Optional["RichOptionPanel"] = None,
    ) -> "RichPanelRow":
        """Create a row for the rich table corresponding with this parameter."""
        from rich_click.rich_help_rendering import get_parameter_rich_table_row

        return get_parameter_rich_table_row(self, ctx, formatter, panel)


class RichArgument(RichParameter, click.Argument):
    """
    Arguments are positional parameters to a command.  They generally
    provide fewer features than options but can have infinite ``nargs``
    and are required by default.

    All parameters are passed onwards to the constructor of :class:`Parameter`.
    """


class RichOption(RichParameter, click.Option):
    """
    Options are usually optional values on the command line and
    have some extra features that arguments don't have.

    All other parameters are passed onwards to the parameter constructor.
    """
