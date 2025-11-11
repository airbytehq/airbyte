from __future__ import annotations

import inspect
import re
from enum import Enum
from gettext import gettext
from typing import TYPE_CHECKING, Any, Callable, Dict, Iterable, List, Literal, Optional, Tuple, Union, overload

import click
from rich.align import Align
from rich.columns import Columns
from rich.console import RenderableType, group
from rich.highlighter import RegexHighlighter
from rich.jupyter import JupyterMixin
from rich.padding import Padding
from rich.panel import Panel
from rich.text import Text

from rich_click._click_types_cache import Argument, Command, Group, Option
from rich_click._compat_click import (
    CLICK_IS_BEFORE_VERSION_82,
    CLICK_IS_VERSION_80,
)
from rich_click.rich_context import RichContext
from rich_click.rich_help_formatter import RichHelpFormatter
from rich_click.rich_parameter import RichParameter


if TYPE_CHECKING:
    from rich.markdown import Markdown

    from rich_click.rich_help_configuration import CommandColumnType, OptionColumnType, OptionHelpSectionType
    from rich_click.rich_panel import RichCommandPanel, RichOptionPanel


RichPanelRow = List[Optional[RenderableType]]


class RichClickRichPanel(Panel):
    """
    A console renderable that draws a border around its contents.

    This is a patched version of rich.panel.Panel that has additional features useful
    for rendering help text with rich-click.
    """

    def __init__(self, *args: Any, title_padding: int = 1, **kwargs: Any) -> None:
        """
        Create RichClickRichPanel instance.

        Args:
        ----
            *args: Args that get passed to rich.panel.Panel.
            title_padding: Controls padding on panel title.
            **kwargs: Kwargs that get passed to rich.panel.Panel.

        """
        super().__init__(*args, **kwargs)
        self.title_padding = title_padding

    @property
    def _title(self) -> Optional[Text]:
        if self.title:
            title_text = Text.from_markup(self.title) if isinstance(self.title, str) else self.title.copy()
            title_text.end = ""
            title_text.plain = title_text.plain.replace("\n", " ")
            title_text.no_wrap = True
            title_text.expand_tabs()
            # Ensure underlines are handled beautifully;
            # title_text.pad() expands underlines, whereas this method does not.
            if self.title_padding == 0:
                return title_text
            return Text("").join([Text(" " * self.title_padding), title_text, Text(" " * self.title_padding)])
        return None


@group()
def _get_help_text(
    obj: Union[Command, Group], formatter: RichHelpFormatter
) -> Iterable[Union[Padding, "Markdown", Text]]:
    """
    Build primary help text for a click command or group.
    Returns the prose help text for a command or group, rendered either as a
    Rich Text object or as Markdown.
    If the command is marked as depreciated, the depreciated string will be prepended.

    Args:
    ----
        obj (click.Command or click.Group): Command or group to build help text for.
        formatter: formatter object.

    Yields:
    ------
        Text or Markdown: Multiple styled objects (depreciated, usage)

    """
    if TYPE_CHECKING:  # pragma: no cover
        assert isinstance(obj.help, str)
    config = formatter.config
    # Prepend deprecated status
    if obj.deprecated:
        if isinstance(obj.deprecated, str):
            yield Padding(
                Text.from_markup(
                    formatter.config.deprecated_with_reason_string.format(obj.deprecated.replace("[", r"\[")),
                    style=config.style_deprecated,
                ),
                formatter.config.padding_helptext_deprecated,
                style=formatter.config.style_padding_helptext,
            )
        else:
            yield Padding(
                Text.from_markup(config.deprecated_string, style=config.style_deprecated),
                formatter.config.padding_helptext_deprecated,
                style=formatter.config.style_padding_helptext,
            )

    # Fetch and dedent the help text
    help_text = inspect.cleandoc(obj.help or "")

    # Trim off anything that comes after \f on its own line
    help_text = help_text.partition("\f")[0]

    # Get the first paragraph
    first_line = help_text.split("\n\n")[0]
    # Remove single linebreaks
    if not config.text_markup == "markdown":
        if not first_line.startswith("\b"):
            first_line = first_line.replace("\n", " ")
    yield Padding(
        formatter.rich_text(first_line.strip(), formatter.config.style_helptext_first_line),
        formatter.config.padding_helptext_first_line,
        style=formatter.config.style_padding_helptext,
    )
    # Get remaining lines, remove single line breaks and format as dim
    remaining_paragraphs = help_text.split("\n\n")[1:]

    use_markdown = formatter.config.text_markup == "markdown"
    if formatter.config.text_paragraph_linebreaks is None:
        if use_markdown:
            lb = "\n\n"
        else:
            lb = "\n"
    else:
        lb = formatter.config.text_paragraph_linebreaks

    if len(remaining_paragraphs) > 0:
        if not use_markdown:
            # Remove single linebreaks
            help_text_buf = []
            for para in remaining_paragraphs:
                if para.startswith("\b"):
                    help_text_buf.append("{}\n".format(para.strip("\b\n")))
                    help_text_buf.append(lb)
                else:
                    _continuation = False
                    _list = False
                    _first = True
                    for p in para.split("\n"):
                        if any(p.startswith(_) for _ in ["* ", "- "]):
                            _continuation = False
                            if not _first:
                                help_text_buf.append("\n")
                            _list = True
                            help_text_buf.append(p)
                        elif _list and p.startswith("  "):
                            help_text_buf.append(" ")
                            help_text_buf.append(p.lstrip())
                        elif any(p.startswith(_) for _ in ["    ", "> "]):
                            _continuation = False
                            _list = False
                            if not _first:
                                help_text_buf.append("\n")
                            help_text_buf.append(p)
                        elif _continuation:
                            help_text_buf.append(" ")
                            help_text_buf.append(p)
                        else:
                            _list = False
                            help_text_buf.append(p)
                            _continuation = True
                        _first = False
                help_text_buf.append(lb)
            # Join back together
            remaining_lines = "".join(help_text_buf)
        else:
            # Join with double linebreaks if markdown
            remaining_lines = lb.join(remaining_paragraphs)
        yield formatter.rich_text(remaining_lines, formatter.config.style_helptext)
    if getattr(obj, "aliases", None) and formatter.config.helptext_show_aliases:
        yield Text.from_markup(
            formatter.config.helptext_aliases_string.format(", ".join(obj.aliases)),  # type: ignore[attr-defined]
            style=(
                formatter.config.style_helptext_aliases
                if formatter.config.style_helptext_aliases is not None
                else formatter.config.style_helptext
            ),
        )


def _get_deprecated_text(
    deprecated: Union[bool, str],
    formatter: RichHelpFormatter,
) -> Text:
    if isinstance(deprecated, str):
        s = formatter.config.deprecated_with_reason_string.format(deprecated.replace("[", r"\["))
    else:
        s = formatter.config.deprecated_string
    return Text.from_markup(s, style=formatter.config.style_deprecated)


def _get_parameter_env_var(
    param: Union[click.Argument, click.Option, RichParameter],
    ctx: RichContext,
    formatter: RichHelpFormatter,
) -> Optional[Text]:
    if not getattr(param, "show_envvar", None):
        return None

    envvar = getattr(param, "envvar", None)

    # https://github.com/pallets/click/blob/0aec1168ac591e159baf6f61026d6ae322c53aaf/src/click/core.py#L2720-L2726
    if envvar is None:
        if (
            getattr(param, "allow_from_autoenv", None)
            and getattr(ctx, "auto_envvar_prefix", None) is not None
            and param.name is not None
        ):
            envvar = f"{ctx.auto_envvar_prefix}_{param.name.upper()}"
    if envvar is not None:
        envvar = ", ".join(envvar) if isinstance(envvar, list) else envvar

    if envvar is not None:
        return Text.from_markup(
            formatter.config.envvar_string.format(envvar), style=formatter.config.style_option_envvar
        )
    return None


def _get_parameter_deprecated(
    param: Union[click.Argument, click.Option, RichParameter],
    ctx: RichContext,
    formatter: RichHelpFormatter,
) -> Optional[Text]:
    if not getattr(param, "deprecated", None):
        return None
    return _get_deprecated_text(getattr(param, "deprecated"), formatter)


def _get_parameter_help(
    param: Union[click.Argument, click.Option, RichParameter],
    ctx: RichContext,
    formatter: RichHelpFormatter,
) -> Optional[Union["Markdown", Text]]:
    base_help_txt = getattr(param, "help", None)
    if not base_help_txt:
        return None

    if TYPE_CHECKING:  # pragma: no cover
        assert isinstance(param, click.Option)
        assert hasattr(param, "help")
        assert isinstance(param.help, str)

    paragraphs = base_help_txt.split("\n\n")

    # Remove single linebreaks
    if not formatter.config.use_markdown and not formatter.config.text_markup == "markdown":
        paragraphs = [
            x.replace("\n", " ").strip() if not x.startswith("\b") else "{}\n".format(x.strip("\b\n"))
            for x in paragraphs
        ]
    help_text = "\n".join(paragraphs).strip()

    # `Deprecated` is included in base help text; remove it here.
    if getattr(param, "deprecated", None):
        if isinstance(getattr(param, "deprecated"), str):
            help_text = re.sub(r"\(DEPRECATED: .*?\)$", "", help_text)
        else:
            help_text = re.sub(r"\(DEPRECATED\)$", "", help_text)

    if getattr(param, "help_style", None) is None:
        style = formatter.config.style_option_help
    else:
        style = param.help_style  # type: ignore[attr-defined]
    return formatter.rich_text(help_text, style)


@overload
def _get_parameter_range(
    param: Union[click.Argument, click.Option, RichParameter],
    ctx: RichContext,
    formatter: RichHelpFormatter,
    mode: Literal["metavar_append"],
) -> Optional[str]: ...


@overload
def _get_parameter_range(
    param: Union[click.Argument, click.Option, RichParameter],
    ctx: RichContext,
    formatter: RichHelpFormatter,
    mode: Literal["metavar_column", "help"],
) -> Optional[Text]: ...


def _get_parameter_range(
    param: Union[click.Argument, click.Option, RichParameter],
    ctx: RichContext,
    formatter: RichHelpFormatter,
    mode: Literal["metavar_append", "metavar_column", "help"],
) -> Optional[Union[Text, str]]:
    # Range - from
    # https://github.com/pallets/click/blob/c63c70dabd3f86ca68678b4f00951f78f52d0270/src/click/core.py#L2698-L2706  # noqa: E501
    # skip count with default range type
    if (
        hasattr(param, "count")
        and isinstance(param.type, click.types._NumberRangeBase)
        and not (param.count and param.type.min == 0 and param.type.max is None)
    ):
        range_str = param.type._describe_range()
        if range_str:
            if mode == "metavar_append":
                return range_str
            elif mode == "metavar_column":
                metavar_str = formatter.config.range_string.format(range_str)
                return Text.from_markup(metavar_str, style=formatter.config.style_metavar)
            elif mode == "help":
                metavar_str = formatter.config.append_range_help_string.format(range_str)
                return Text.from_markup(
                    metavar_str,
                    style=(
                        formatter.config.style_range_append
                        if formatter.config.style_range_append is not None
                        else formatter.config.style_metavar_append
                    ),
                )
            else:
                raise ValueError("Bad mode selected")
    return None


def _get_parameter_metavar(
    param: Union[click.Argument, click.Option, RichParameter],
    ctx: RichContext,
    formatter: RichHelpFormatter,
    append: bool = True,
    show_range: bool = False,
) -> Optional[Text]:
    metavar_str = param.make_metavar() if CLICK_IS_BEFORE_VERSION_82 else param.make_metavar(ctx)  # type: ignore
    # Do it ourselves if this is a positional argument
    if isinstance(param, Argument) and param.name is not None and re.match(rf"\[?{param.name.upper()}]?", metavar_str):
        metavar_str = param.type.name.upper()
    # Attach metavar if param is a positional argument, or if it is a non boolean and non flag option
    if isinstance(param, Argument) or (metavar_str != "BOOLEAN" and hasattr(param, "is_flag") and not param.is_flag):
        metavar_str = metavar_str.replace("[", "").replace("]", "")

        if show_range:
            range_txt = _get_parameter_range(param, ctx, formatter, mode="metavar_append")
            if range_txt:
                metavar_str += " " + range_txt

        return Text.from_markup(
            formatter.config.append_metavars_help_string.format(metavar_str),
            style=formatter.config.style_metavar_append if append else formatter.config.style_metavar,
            overflow="fold",
        )
    return None


def _get_parameter_help_metavar_col(
    param: Union[click.Argument, click.Option, RichParameter],
    ctx: RichContext,
    formatter: RichHelpFormatter,
    show_range: bool = True,
) -> Optional[Text]:
    # Column for a metavar, if we have one
    metavar = Text(style=formatter.config.style_metavar, overflow="fold")
    metavar_str = param.make_metavar() if CLICK_IS_BEFORE_VERSION_82 else param.make_metavar(ctx)  # type: ignore

    if TYPE_CHECKING:  # pragma: no cover
        assert isinstance(param.name, str)
        assert isinstance(param, Option)

    # Do it ourselves if this is a positional argument
    if isinstance(param, Argument) and re.match(rf"\[?{param.name.upper()}]?", metavar_str):
        metavar_str = param.type.name.upper()

    # Attach metavar if param is a positional argument, or if it is a non-boolean and non flag option
    if isinstance(param, Argument) or (metavar_str != "BOOLEAN" and not getattr(param, "is_flag", None)):
        metavar.append(metavar_str)

    # Range - from
    # https://github.com/pallets/click/blob/c63c70dabd3f86ca68678b4f00951f78f52d0270/src/click/core.py#L2698-L2706  # noqa: E501
    try:
        # skip count with default range type
        if isinstance(param.type, click.types._NumberRangeBase) and not (
            param.count and param.type.min == 0 and param.type.max is None
        ):
            range_str = param.type._describe_range()
            if show_range and range_str:
                metavar.append(" " + formatter.config.range_string.format(range_str))
    except AttributeError:
        # click.types._NumberRangeBase is only in Click 8x onwards
        pass

    # Highlighter to make [ | ] and <> dim
    class MetavarHighlighter(RegexHighlighter):
        highlights = [
            r"(^|\s)(?P<metavar_sep>(\[|<))",
            r"(?P<metavar_sep>\|)",
            r"(?P<metavar_sep>(\]|>)$)",
        ]

    if "".join(metavar._text) == "":
        return None

    metavar_highlighter = MetavarHighlighter()
    return metavar_highlighter(metavar)


def _get_parameter_help_opt(
    param: Union[click.Argument, click.Option, RichParameter],
    ctx: RichContext,
    formatter: RichHelpFormatter,
) -> Tuple[
    Optional[Text],
    Optional[Text],
    Optional[Text],
    Optional[Text],
    Optional[Text],
]:
    # This may seem convoluted to return tuples with widths instead of just renderables,
    # but there are two things we want to do that are impossible otherwise:
    # 1. Prevent splitting of options. If we just use Text() and allow wrapping,
    #    then something like --foo/--bar may split in the middle of an option
    #    instead of at the "/".
    # 2. Make it so the table doesn't expand. We solve the first problem by using
    #    Columns(), but the issue is there is no way to prevent the expansion of
    #    the outer table column other than to explicitly set the width.
    # Attempting to solve both of those problems simultaneously leads to this mess.

    opt_long_primary = []
    opt_short_primary = []
    opt_long_secondary = []
    opt_short_secondary = []

    for opt in param.opts:
        if isinstance(param, Argument):
            opt_long_primary.append(opt.upper())
        elif "--" in opt:
            opt_long_primary.append(opt)
        else:
            opt_short_primary.append(opt)
    for opt in param.secondary_opts:
        if isinstance(param, Argument):
            opt_long_secondary.append(opt.upper())
        elif "--" in opt:
            opt_long_secondary.append(opt)
        else:
            opt_short_secondary.append(opt)

    from rich.text import Text

    # opt_long_primary_len = len("".join(opt_long_primary)) + len(opt_long_primary) - 1
    # opt_short_primary_len = len("".join(opt_short_primary)) + len(opt_short_primary) - 1
    # opt_long_secondary_len = len("".join(opt_long_secondary)) + len(opt_long_secondary) - 1
    # opt_short_secondary_len = len("".join(opt_short_secondary)) + len(opt_short_secondary) - 1

    primary_cols = []
    secondary_cols = []
    long_cols = []
    short_cols = []

    comma = Text(formatter.config.delimiter_comma, style=formatter.config.style_option_help)
    slash = Text(formatter.config.delimiter_slash, style=formatter.config.style_option_help)

    for o in opt_short_primary:
        oh = Text(o.strip(), style=formatter.config.style_switch)
        primary_cols.append(oh)
        primary_cols.append(comma)
        short_cols.append(oh)
        short_cols.append(comma)

    for o in opt_long_primary:
        oh = Text(o.strip(), style=formatter.config.style_option)
        primary_cols.append(oh)
        primary_cols.append(comma)
        long_cols.append(oh)
        long_cols.append(comma)

    if opt_short_secondary:
        short_cols = short_cols[:-1]
        short_cols.append(slash)
        for o in opt_short_secondary:
            oh = Text(
                o.strip(),
                style=(
                    formatter.config.style_switch_negative
                    if formatter.config.style_switch_negative is not None
                    else formatter.config.style_switch
                ),
            )
            secondary_cols.append(oh)
            secondary_cols.append(comma)
            short_cols.append(oh)
            short_cols.append(comma)

    if opt_long_secondary:
        long_cols = long_cols[:-1]
        long_cols.append(slash)
        for o in opt_long_secondary:
            oh = Text(
                o.strip(),
                style=(
                    formatter.config.style_option_negative
                    if formatter.config.style_option_negative is not None
                    else formatter.config.style_option
                ),
            )
            secondary_cols.append(oh)
            secondary_cols.append(comma)
            long_cols.append(oh)
            long_cols.append(comma)

    all_cols = primary_cols
    if secondary_cols:
        all_cols = [*primary_cols[:-1], slash, *secondary_cols]

    def _renderable(cols: List[Text]) -> Optional[Text]:
        if not cols:
            return None
        if len(cols) == 1:
            return cols[0]
        # Todo - make the text fold at the slashes without adding whitespace.
        #   this is very tricky.
        t = Text("", overflow="fold").join(cols)
        return t

    primary_final = _renderable(primary_cols[:-1])
    secondary_final = _renderable(secondary_cols[:-1])
    long_final = _renderable(long_cols[:-1])
    short_final = _renderable(short_cols[:-1])
    all_final = _renderable(all_cols[:-1])

    return primary_final, secondary_final, long_final, short_final, all_final


def _get_parameter_default(
    param: Union[click.Argument, click.Option, RichParameter], ctx: RichContext, formatter: RichHelpFormatter
) -> Optional[Text]:

    if not hasattr(param, "show_default"):
        return None

    show_default = False
    show_default_is_str = False

    resilient = ctx.resilient_parsing
    ctx.resilient_parsing = True
    try:
        default_value = param.get_default(ctx, call=False)
    finally:
        ctx.resilient_parsing = resilient

    notset: Tuple[Any, ...]
    try:
        # try/except because it's unclear whether later versions of click will change this.
        if not CLICK_IS_BEFORE_VERSION_82:
            from click.core import UNSET  # type: ignore[attr-defined,unused-ignore]

            notset = (UNSET, None)
        else:
            notset = (None,)
    except ImportError:
        notset = (None,)

    if (not CLICK_IS_VERSION_80 and param.show_default is not None) or param.show_default:
        if isinstance(param.show_default, str):
            show_default_is_str = show_default = True
        else:
            show_default = param.show_default
    elif ctx.show_default is not None:
        show_default = ctx.show_default

    default_string: Optional[str] = None

    if show_default_is_str or (show_default and (default_value not in notset)):
        if show_default_is_str:
            default_string = f"({param.show_default})"
        elif isinstance(default_value, (list, tuple)):
            default_string = ", ".join(str(d) for d in default_value)
        elif isinstance(default_value, Enum):
            default_string = str(default_value.value)
        elif inspect.isfunction(default_value):
            default_string = gettext("(dynamic)")
        elif hasattr(param, "is_bool_flag") and param.is_bool_flag and param.secondary_opts:
            # For boolean flags that have distinct True/False opts,
            # use the opt without prefix instead of the value.
            opt = (param.opts if default_value else param.secondary_opts)[0]
            first = opt[:1]
            if first.isalnum():
                default_string = opt
            if opt[1:2] == first:
                default_string = opt[2:]
            else:
                default_string = opt[1:]
        elif hasattr(param, "is_bool_flag") and param.is_bool_flag and not param.secondary_opts and not default_value:
            if CLICK_IS_VERSION_80:
                default_string = str(param.default)
            else:
                default_string = ""
        elif default_value == "":
            default_string = '""'
        else:
            default_string = str(default_value)

    if default_string:
        return Text.from_markup(
            formatter.config.default_string.format(default_string.replace("[", r"\[")),
            style=formatter.config.style_option_default,
        )
    return None


def _get_parameter_required(
    param: Union[click.Argument, click.Option, RichParameter], ctx: RichContext, formatter: RichHelpFormatter
) -> Optional[Text]:
    if param.required:
        return Text.from_markup(formatter.config.required_long_string, style=formatter.config.style_required_long)
    return None


def _get_parameter_help_required_short(
    param: Union[click.Argument, click.Option, RichParameter], ctx: RichContext, formatter: RichHelpFormatter
) -> Optional[Text]:
    if param.required:
        return Text(formatter.config.required_short_string, style=formatter.config.style_required_short)
    return None


def get_help_parameter(
    param: Union[click.Argument, click.Option, RichParameter], ctx: RichContext, formatter: RichHelpFormatter
) -> Columns:
    """
    Build primary help text for a click option or argument.
    Returns the prose help text for an option or argument, rendered either
    as a Rich Text object or as Markdown.
    Additional elements are appended to show the default and required status if applicable.

    Args:
    ----
        param (click.Argument or click.Option): Parameter to build help text for.
        ctx (click.Context): Click Context object.
        formatter (RichHelpFormatter): formatter object.

    Returns:
    -------
        Columns: A columns element with multiple styled objects (help, default, required)

    """
    if TYPE_CHECKING:  # pragma: no cover
        assert isinstance(param.name, str)

    section_callbacks: Dict["OptionHelpSectionType", Callable[..., Any]] = {
        "help": _get_parameter_help,
        "required": _get_parameter_required,
        "envvar": _get_parameter_env_var,
        "default": _get_parameter_default,
        "metavar": lambda param, ctx, formatter: _get_parameter_metavar(param, ctx, formatter, show_range=True),
        "metavar_short": lambda param, ctx, formatter: _get_parameter_metavar(param, ctx, formatter, show_range=False),
        "range": lambda param, ctx, formatter: _get_parameter_range(param, ctx, formatter, mode="help"),
        "deprecated": _get_parameter_deprecated,
    }

    sections: List[Optional[RenderableType]] = []
    for sec in formatter.config.options_table_help_sections:
        sections.append(section_callbacks[sec](param, ctx, formatter))

    # Use Columns - this allows us to group different renderable types
    # (Text, Markdown) onto a single line.
    if formatter.config.text_markup == "markdown" or not all([isinstance(i, Text) or i is None for i in sections]):
        return Columns([i for i in sections if i])
    else:
        # Weird but necessary--
        # in order to keep things flush, the last column of the table must be of type Columns().
        # (We are assuming here 'help' is always last, which is not necessarily the case of course.)
        # In a 2.0 of rich-click we will try to do something nicer than this.
        # But in 1.x all other solutions would be too breaking.
        return Columns(
            [
                Text(" ", overflow="fold", style=formatter.config.style_option_help).join(
                    [i for i in sections if i]  # type: ignore[misc]
                )
            ]
        )


def get_parameter_rich_table_row(
    param: Union[click.Argument, click.Option, RichParameter],
    ctx: RichContext,
    formatter: RichHelpFormatter,
    panel: Optional["RichOptionPanel"],
) -> RichPanelRow:
    """Create a row for the rich table corresponding with this parameter."""
    # Short and long form
    column_types: List["OptionColumnType"]
    if panel is None:
        column_types = formatter.config.options_table_column_types
    else:
        column_types = panel.column_types or formatter.config.options_table_column_types

    opt_long_strs = []
    opt_short_strs = []
    for idx, opt in enumerate(param.opts):
        opt_str = opt
        secondary = None
        try:
            secondary = param.secondary_opts[idx]
        except IndexError:
            pass

        if isinstance(param, Argument):
            opt_long_strs.append(Text.from_markup(opt_str.upper(), style=formatter.config.style_option))
        elif "--" in opt:
            if secondary:
                opt_long_strs.append(
                    Text("/", style=formatter.config.style_option_help).join(
                        [
                            Text(opt_str, style=formatter.config.style_option),
                            Text(
                                secondary,
                                style=(
                                    formatter.config.style_option_negative
                                    if formatter.config.style_option_negative is not None
                                    else formatter.config.style_option
                                ),
                            ),
                        ]
                    )
                )
            else:
                opt_long_strs.append(Text.from_markup(opt_str, style=formatter.config.style_option))
        else:
            if secondary:
                opt_short_strs.append(
                    Text("/", style=formatter.config.style_option_help).join(
                        [
                            Text(opt_str, style=formatter.config.style_option),
                            Text(
                                secondary,
                                style=(
                                    formatter.config.style_option_negative
                                    if formatter.config.style_option_negative is not None
                                    else formatter.config.style_option
                                ),
                            ),
                        ]
                    )
                )
            else:
                opt_short_strs.append(Text.from_markup(opt_str, style=formatter.config.style_option))

    if TYPE_CHECKING:  # pragma: no cover
        assert isinstance(param.name, str)
        assert isinstance(param, Option)

    _primary, _secondary, _long, _short, _all = _get_parameter_help_opt(param, ctx, formatter)

    _metavar_padded = None
    if any(i in column_types for i in ["opt_all_metavar", "opt_long_metavar"]):
        _metavar_padded = _get_parameter_metavar(param, ctx, formatter, append=False, show_range=False)

    def _opt_all_metavar() -> Optional[RenderableType]:
        if _metavar_padded is None:
            return _all
        if _all is None:
            return _metavar_padded
        return Text(" ", style=formatter.config.style_option_help).join([_all, _metavar_padded])

    def _opt_long_metavar() -> Optional[RenderableType]:
        if _metavar_padded is None:
            return _long
        if _long is None:
            return _metavar_padded
        return Text(" ", style=formatter.config.style_option_help).join([_long, _metavar_padded])

    column_callbacks: Dict["OptionColumnType", Callable[..., Any]] = {
        "required": _get_parameter_help_required_short,
        "opt_long": lambda *args, **kwargs: _long,
        "opt_short": lambda *args, **kwargs: _short,
        "opt_primary": lambda *args, **kwargs: _primary,
        "opt_secondary": lambda *args, **kwargs: _secondary,
        "opt_all": lambda *args, **kwargs: _all,
        "metavar": _get_parameter_help_metavar_col,
        "metavar_short": lambda *args, **kwargs: _get_parameter_help_metavar_col(*args, **kwargs, show_range=False),  # type: ignore[misc]
        "opt_all_metavar": lambda *args, **kwargs: _opt_all_metavar(),
        "opt_long_metavar": lambda *args, **kwargs: _opt_long_metavar(),
        "help": lambda *args, **kwargs: (
            param.get_rich_help(ctx, formatter)
            if isinstance(param, RichParameter)
            else get_help_parameter(param, ctx, formatter)
        ),
        # "default": lambda *args, **kwargs: None,
        # "envvar": lambda *args, **kwargs: None,
    }

    cols: RichPanelRow = []
    for col in column_types:
        cols.append(column_callbacks[col](param, ctx, formatter))

    return cols


def _get_command_name_help(
    command: click.Command,
    ctx: RichContext,
    formatter: RichHelpFormatter,
) -> Text:
    # We want to use the command name as it is registered in the group.
    # This resolves the situation where they do not match.
    # e.g. group.add_command(subcmd, name="foo")
    #
    # Note there may be extremely weird edge cases not covered here,
    # most notably, when a user registers the same command twice.
    # We do not care to solve this edge case.
    command_name = None
    if isinstance(ctx.command, Group):
        if command.name not in ctx.command.commands:
            for k, v in ctx.command.commands.items():
                if command is v:
                    command_name = k
                    break
    if command_name is None:
        command_name = command.name or ""
    return Text(command_name, style=formatter.config.style_command)


def _get_command_aliases_help(
    command: click.Command,
    ctx: RichContext,
    formatter: RichHelpFormatter,
    include_name: bool = False,
) -> Optional[Text]:
    aliases = getattr(command, "aliases", None)
    if aliases:
        txt_list = []
        comma = Text(formatter.config.delimiter_comma, style=formatter.config.style_command_help)
        _last = len(aliases) - 1
        for idx, alias in enumerate(aliases):
            txt_list.append(Text(alias, style=formatter.config.style_command_aliases))
            if idx != _last:
                txt_list.append(comma)
        if include_name:
            cmd_name_txt = _get_command_name_help(command, ctx, formatter)
            return Text("", overflow="ellipsis").join([cmd_name_txt, comma, *txt_list])
        else:
            return Text("").join(txt_list)
    elif include_name:
        return _get_command_name_help(command, ctx, formatter)
    return None


def get_command_rich_table_row(
    command: click.Command,
    ctx: RichContext,
    formatter: RichHelpFormatter,
    panel: Optional["RichCommandPanel"],
) -> RichPanelRow:
    """Create a row for the rich table corresponding with this command."""
    # todo
    column_types: List["CommandColumnType"]
    if panel is None:
        column_types = formatter.config.commands_table_column_types
    else:
        column_types = panel.column_types or formatter.config.commands_table_column_types

    column_callbacks: Dict["CommandColumnType", Callable[..., Any]] = {
        "name": _get_command_name_help,
        "aliases": _get_command_aliases_help,
        "name_with_aliases": lambda *args, **kwargs: _get_command_aliases_help(*args, **kwargs, include_name=True),  # type: ignore[misc]
        "help": _get_command_help,
        # "short_help": ...,
    }

    cols: RichPanelRow = []
    for col in column_types:
        cols.append(column_callbacks[col](command, ctx, formatter))

    return cols


def _get_command_help(
    command: click.Command,
    ctx: RichContext,
    formatter: RichHelpFormatter,
) -> Union[Text, "Markdown", Columns]:
    """
    Build cli help text for a click group command.
    That is, when calling help on groups with multiple subcommands
    (not the main help text when calling the subcommand help).
    Returns the first paragraph of help text for a command, rendered either as a
    Rich Text object or as Markdown.
    Ignores single newlines as paragraph markers, looks for double only.

    Returns
    -------
        Text or Markdown: Styled object

    """
    if formatter.config.use_click_short_help:
        help_text = command.get_short_help_str()
    else:
        help_text = command.short_help or command.help or ""

    deprecated = command.deprecated

    paragraphs = inspect.cleandoc(help_text).split("\n\n")
    # Remove single linebreaks
    if not formatter.config.text_markup == "markdown" and not paragraphs[0].startswith("\b"):
        paragraphs[0] = paragraphs[0].replace("\n", " ")
    elif paragraphs[0].startswith("\b"):
        paragraphs[0] = paragraphs[0].replace("\b\n", "")
    help_text = paragraphs[0].strip()
    renderable: Union[Text, "Markdown", Columns]
    renderable = formatter.rich_text(help_text, formatter.config.style_command_help)
    if deprecated:
        dep_txt = _get_deprecated_text(
            deprecated=deprecated,
            formatter=formatter,
        )
        if isinstance(renderable, Text):
            renderable.append(" ")
            renderable.append(dep_txt)
        else:
            renderable = Columns([renderable, dep_txt])
    return renderable


def get_rich_usage(formatter: RichHelpFormatter, prog: str, args: str = "", prefix: Optional[str] = None) -> None:
    """Richly render usage text."""
    if prefix is None:
        prefix = "Usage:"

    config = formatter.config

    # Header text if we have it
    if config.header_text:
        formatter.write(
            Padding(
                formatter.rich_text(config.header_text, config.style_header_text),
                config.padding_header_text,
                style=formatter.config.style_padding_usage,
            ),
        )

    # Highlighter for options and arguments
    class UsageHighlighter(RegexHighlighter):
        highlights = [
            r"(?P<argument>\w+)",
        ]

    usage_highlighter = UsageHighlighter()

    # Print usage
    formatter.write(
        Padding(
            Columns(
                (
                    Text(prefix, style=config.style_usage),
                    Text(prog, style=config.style_usage_command),
                    usage_highlighter(Text(args, style=config.style_usage_separator)),
                )
            ),
            formatter.config.padding_usage,
            style=formatter.config.style_padding_usage,
        ),
    )


def get_rich_help_text(self: Command, ctx: RichContext, formatter: RichHelpFormatter) -> None:
    """Write rich help text to the formatter if it exists."""
    # Print command / group help if we have some
    if self.help or self.deprecated or getattr(self, "aliases", None):
        # Print with some padding
        formatter.write(
            Padding(
                Align(_get_help_text(self, formatter), pad=False),
                formatter.config.padding_helptext,
                style=formatter.config.style_padding_helptext,
            )
        )


def get_rich_epilog(
    self: Command,
    ctx: RichContext,
    formatter: RichHelpFormatter,
) -> None:
    """Richly render a click Command's epilog if it exists."""
    if self.epilog:
        # Remove single linebreaks, replace double with single
        lines = self.epilog.split("\n\n")
        if isinstance(self.epilog, JupyterMixin):  # Handles Text and Markdown
            epilog = self.epilog
        else:
            epilog = "\n".join([x.replace("\n", " ").strip() for x in lines])  # type: ignore[assignment]
            epilog = formatter.rich_text(epilog, formatter.config.style_epilog_text)  # type: ignore[assignment]
        formatter.write(
            Padding(
                Align(epilog, pad=False), formatter.config.padding_epilog, style=formatter.config.style_padding_epilog
            )
        )

    # Footer text if we have it
    if formatter.config.footer_text:
        formatter.write(
            Padding(
                formatter.rich_text(formatter.config.footer_text, formatter.config.style_footer_text),
                formatter.config.padding_footer_text,
                style=formatter.config.style_padding_epilog,
            )
        )


def rich_format_error(
    self: click.ClickException, formatter: RichHelpFormatter, export_console_as: Literal[None, "html", "svg"] = None
) -> None:
    """
    Print richly formatted click errors.

    Called by custom exception handler to print richly formatted click errors.
    Mimics original click.ClickException.echo() function but with rich formatting.

    Args:
    ----
        self (click.ClickException): Click exception to format.
        formatter: formatter object.
        export_console_as: If set, outputs error message as HTML or SVG.

    """
    config = formatter.config
    # Print usage
    if getattr(self, "ctx", None) is not None:
        if TYPE_CHECKING:  # pragma: no cover
            assert hasattr(self, "ctx")
        self.ctx.command.format_usage(self.ctx, formatter)
    if config.errors_suggestion:
        formatter.write(
            Padding(
                config.errors_suggestion,
                config.padding_errors_suggestion,
            ),
            style=config.style_errors_suggestion,
        )
    elif (
        config.errors_suggestion is None
        and getattr(self, "ctx", None) is not None
        and self.ctx.command.get_help_option(self.ctx) is not None  # type: ignore[attr-defined]
    ):
        cmd_path = self.ctx.command_path  # type: ignore[attr-defined]
        help_option = self.ctx.help_option_names[0]  # type: ignore[attr-defined]
        formatter.write(
            Padding(
                Text(" ").join(
                    (
                        Text("Try"),
                        Text(
                            f"'{cmd_path} {help_option}'",
                            style=(
                                config.style_errors_suggestion_command
                                if config.style_errors_suggestion_command is not None
                                else config.style_option
                            ),
                        ),
                        Text("for help"),
                    ),
                ),
                config.padding_errors_suggestion,
                style=config.style_padding_errors,
            ),
            style=(
                config.style_errors_suggestion if config.style_errors_suggestion is not None else config.style_helptext
            ),
        )

    # A major Python library using click (dbt-core) has its own exception
    # logic that subclasses ClickException, but does not use the message
    # attribute. Checking for the 'message' attribute works to make the
    # rich-click CLI compatible.
    if hasattr(self, "message"):

        from rich_click.rich_box import get_box

        formatter.write(
            Padding(
                Panel(
                    formatter.highlighter(self.format_message()),
                    border_style=config.style_errors_panel_border,
                    title=config.errors_panel_title,
                    title_align=config.align_errors_panel,
                    box=get_box(formatter.config.style_errors_panel_box or "ROUNDED"),
                ),
                config.padding_errors_panel,
                style=config.style_padding_errors,
            )
        )
    if config.errors_epilogue:
        formatter.write(Padding(config.errors_epilogue, config.padding_errors_epilogue))
