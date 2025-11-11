from __future__ import annotations

import io
import sys
from contextlib import contextmanager
from functools import cached_property
from typing import (
    IO,
    TYPE_CHECKING,
    Any,
    Dict,
    Iterator,
    Literal,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
)

import click

from rich_click.rich_help_configuration import RichHelpConfiguration
from rich_click.rich_panel import RichCommandPanel, RichOptionPanel, RichPanel


if TYPE_CHECKING:  # pragma: no cover
    from rich.console import Console
    from rich.highlighter import Highlighter
    from rich.markdown import Markdown
    from rich.style import StyleType
    from rich.text import Text


RP = TypeVar("RP", bound=RichPanel[Any, Any])


def create_console(
    config: RichHelpConfiguration,
    file: Optional[IO[str]] = None,
    width: Optional[int] = None,
    max_width: Optional[int] = None,
) -> "Console":
    """
    Create a Rich Console configured from Rich Help Configuration.

    Args:
    ----
        config: Rich Help Configuration instance
        file: Optional IO stream to write Rich Console output
            Defaults to None.
        width: Width of the Console; overrides config.width if set.
        max_width: Max width of the Console; overrides config.max_width if set.

    """
    from rich.console import Console
    from rich.theme import Theme

    console = Console(
        theme=Theme(
            {
                "option": config.style_option,
                "command": config.style_command,
                "argument": config.style_argument,
                "switch": config.style_switch,
                "metavar": config.style_metavar,
                "metavar_sep": config.style_metavar_separator,
                "usage": config.style_usage,
                "deprecated": config.style_deprecated,
            }
        ),
        color_system=config.color_system,
        force_terminal=config.force_terminal,
        width=width if width is not None else config.width,
        record=True if file is None else False,
        legacy_windows=config.legacy_windows,
    )
    # Defaults for console.color_system change when file is in __init__.
    # Workaround: set file after __init__.
    console.file = file or io.StringIO()
    max_width = max_width if max_width is not None else config.max_width
    if isinstance(max_width, int):
        console.width = min(max_width, console.size.width)
    return console


class RichHelpFormatter(click.HelpFormatter):
    """
    Rich Help Formatter.

    This class is a container for the help configuration and Rich Console that
    are used internally by the help and error printing methods.
    """

    console: "Console"
    """Rich Console created from the help configuration.

    This console is meant only for use with the formatter and should
    not be created directly
    """
    export_console_as: Literal[None, "html", "svg", "text"] = None

    option_panel_class: Type[RichOptionPanel] = RichOptionPanel
    command_panel_class: Type[RichCommandPanel] = RichCommandPanel

    def __init__(
        self,
        indent_increment: int = 2,
        width: Optional[int] = None,
        max_width: Optional[int] = None,
        *args: Any,
        console: Optional["Console"] = None,
        config: Optional[RichHelpConfiguration] = None,
        export_console_as: Literal[None, "html", "svg", "text"] = None,
        export_kwargs: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Create Rich Help Formatter.

        Args:
        ----
            indent_increment: Passed to click.HelpFormatter.
            width: Passed to click.HelpFormatter. Overrides config.width if not None.
            max_width: Passed to click.HelpFormatter. Overrides config.max_width if not None.
            *args: Args passed to click.HelpFormatter.
            console: Use an external console.
            config: RichHelpConfiguration. If None, then build config from globals.
            file: Stream to output to in the Rich Console. If None, use stdout.
            export_console_as: How output is rendered by getvalue(). Default of None renders output normally.
            export_kwargs: Any kwargs passed to the export method of the Console in getvalue().
            **kwargs: Kwargs passed to click.HelpFormatter.

        """
        if config is not None:
            self.config = config
            # Rich config overrides width and max width if set.
        else:
            self.config = RichHelpConfiguration.load_from_globals()

        self.config.apply_theme(force_default=True)

        file = kwargs.pop("file", None)
        if file is not None:
            import warnings

            warnings.warn(
                "The file kwarg to `RichHelpFormatter()` is deprecated" " and will be removed in a future release.",
                DeprecationWarning,
                stacklevel=2,
            )

        if console:
            self.console = console
        else:
            self.console = create_console(self.config, file=file, width=width, max_width=max_width)

        width = self.console.width

        self.export_console_as = export_console_as
        self.export_kwargs = export_kwargs or {}

        super().__init__(indent_increment, width, max_width, *args, **kwargs)

    @property
    def width(self) -> int:
        return self.console.width

    @width.setter
    def width(self, v: int) -> None:
        self.console.width = v

    @cached_property
    def highlighter(self) -> "Highlighter":
        if self.config.highlighter is not None:
            return self.config.highlighter
        else:
            from rich.highlighter import RegexHighlighter

            class HighlighterClass(RegexHighlighter):
                highlights = self.config.highlighter_patterns

            return HighlighterClass()

    def write(self, *objects: Any, **kwargs: Any) -> None:
        self.console.print(*objects, **kwargs)

    def write_usage(self, prog: str, args: str = "", prefix: Optional[str] = None) -> None:
        from rich_click.rich_help_rendering import get_rich_usage

        get_rich_usage(formatter=self, prog=prog, args=args, prefix=prefix)

    def write_error(self, e: click.ClickException) -> None:
        from rich_click.rich_help_rendering import rich_format_error

        rich_format_error(self=e, formatter=self)

    def write_abort(self) -> None:
        """Print richly formatted abort error."""
        self.console.print(self.config.aborted_text, style=self.config.style_aborted)

    def rich_text(
        self,
        text: Union[str, "Text", "Markdown"],
        style: "StyleType" = "",
    ) -> Union["Text", "Markdown"]:
        """
        Take a string, remove indentations, and return styled text.
        By default, return the text as a Rich Text with the request style.

        This method uses the config options prefixed `text_` to influence how
        rendering works.

        Args:
        ----
            text (str): Text to style.
            style (StyleType): Rich style to apply.

        Returns:
        -------
            MarkdownElement or Text: Styled text object

        """
        import inspect

        from rich.jupyter import JupyterMixin
        from rich.text import Text

        if isinstance(text, JupyterMixin):
            return text

        # Remove indentations from input text
        text = inspect.cleandoc(text)

        kw: Dict[str, Any]
        if self.config.text_markup != "rich":
            kw = {"style": style}
            if self.config.text_emojis:
                from rich.emoji import Emoji

                text = Emoji.replace(text)
        else:
            kw = {"style": style, "emoji": self.config.text_emojis}

        kw.update(self.config.text_kwargs or {})

        if self.config.text_markup == "markdown":
            # Lazy load Markdown because it slows down rendering
            from rich.markdown import Markdown

            return Markdown(text, **kw)
        elif self.config.text_markup == "rich":
            return self.highlighter(Text.from_markup(text, **kw))
        elif self.config.text_markup == "ansi":
            return self.highlighter(Text.from_ansi(text, **kw))
        else:
            return self.highlighter(Text(text, **kw))

    def getvalue(self) -> str:
        if not self.export_console_as:
            from rich.console import COLOR_SYSTEMS
            from rich.segment import Segment

            if self.console.legacy_windows:
                # Handle legacy windows
                import colorama  # type: ignore[import-untyped]

                colorama.init()

            if self.console.no_color:
                res = "".join(
                    (
                        style.render(
                            text,
                            color_system=(
                                COLOR_SYSTEMS.get(self.console.color_system) if self.console.color_system else None
                            ),
                        )
                        if style
                        else text
                    )
                    for text, style, _ in Segment.remove_color(self.console._record_buffer)
                )
            else:
                res = "".join(
                    (
                        style.render(
                            text,
                            color_system=(
                                COLOR_SYSTEMS.get(self.console.color_system) if self.console.color_system else None
                            ),
                        )
                        if style
                        else text
                    )
                    for text, style, _ in self.console._record_buffer
                )
            return res
        elif self.console.record:
            kw = self.export_kwargs.copy()
            kw.setdefault("clear", False)
            if self.export_console_as == "text" or self.export_console_as is None:
                res = self.console.export_text(**kw)
            elif self.export_console_as == "html":
                kw.setdefault("inline_styles", True)
                res = self.console.export_html(**kw)
            elif self.export_console_as == "svg":
                kw.setdefault("title", " ".join(sys.argv))
                res = self.console.export_svg(**kw)
            else:
                raise ValueError(
                    "Invalid value for `export_console_as`." " Must be one of 'text', 'html', 'svg', or None."
                )
            return res
        else:
            return super().getvalue()

    def indent(self) -> None:
        import warnings

        warnings.warn("Not implemented.", RuntimeWarning, stacklevel=2)

    def dedent(self) -> None:
        import warnings

        warnings.warn("Not implemented.", RuntimeWarning, stacklevel=2)

    def write_heading(self, heading: str) -> None:
        import warnings

        warnings.warn("Not implemented.", RuntimeWarning, stacklevel=2)

    def write_paragraph(self) -> None:
        import warnings

        warnings.warn("Not implemented.", RuntimeWarning, stacklevel=2)

    def write_text(self, text: str) -> None:
        import warnings

        warnings.warn("Not implemented.", RuntimeWarning, stacklevel=2)

    def write_dl(
        self,
        rows: Sequence[Tuple[str, str]],
        col_max: int = 30,
        col_spacing: int = 2,
    ) -> None:
        import warnings

        warnings.warn("Not implemented.", RuntimeWarning, stacklevel=2)

    @contextmanager
    def section(self, name: str) -> Iterator[None]:
        import warnings

        warnings.warn("Not implemented.", RuntimeWarning, stacklevel=2)
        yield

    @contextmanager
    def indentation(self) -> Iterator[None]:
        import warnings

        warnings.warn("Not implemented.", RuntimeWarning, stacklevel=2)
        yield
