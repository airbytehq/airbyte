from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from types import ModuleType
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Tuple, TypeVar, Union

from rich_click.rich_click_theme import RichClickTheme, get_theme
from rich_click.utils import CommandGroupDict, OptionGroupDict, notset, truthy


if TYPE_CHECKING:  # pragma: no cover
    from rich.align import AlignMethod
    from rich.box import Box
    from rich.highlighter import Highlighter
    from rich.padding import PaddingDimensions
    from rich.style import StyleType
    from rich.text import Text

T = TypeVar("T", bound="RichHelpConfiguration")

OptionColumnType = Literal[
    "required",
    "opt_primary",
    "opt_secondary",
    "opt_long",
    "opt_short",
    "opt_all",
    "opt_all_metavar",
    "opt_long_metavar",
    "metavar",
    "metavar_short",
    "help",
    # "default",
    # "envvar",
]

CommandColumnType = Literal["name", "aliases", "name_with_aliases", "help"]

OptionHelpSectionType = Literal[
    "help", "required", "envvar", "default", "range", "metavar", "metavar_short", "deprecated"
]

CommandHelpSectionType = Literal["aliases", "help", "deprecated"]

ColumnType = Union[OptionColumnType, CommandColumnType, str]


class FromTheme(object):
    """Sentinel value for unset config options."""

    def __init__(self, default: str) -> None:
        """Initialize a default."""
        self.default = default

    def __repr__(self) -> str:
        return "FromTheme"

    def get_default(self, key: str) -> Any:
        """Get the default value from the default theme."""
        from rich_click.rich_click_theme import get_theme

        theme = get_theme(self.default)
        return theme.styles[key]


FROM_THEME: Any = FromTheme(default="default-box")


def force_terminal_default() -> Optional[bool]:
    """Use as the default factory for `force_terminal`."""
    env_vars = ["FORCE_COLOR", "PY_COLORS", "GITHUB_ACTIONS"]
    for env_var in env_vars:
        if env_var in os.environ:
            return truthy(os.getenv(env_var))
    else:
        return None


def terminal_width_default() -> Optional[int]:
    """Use as the default factory for `width` and `max_width`."""
    width = os.getenv("TERMINAL_WIDTH")
    if width:
        try:
            return int(width)
        except ValueError:
            import warnings

            warnings.warn(
                "Environment variable `TERMINAL_WIDTH` cannot be cast to an integer.", UserWarning, stacklevel=2
            )
            return None
    return None


@dataclass
class RichHelpConfiguration:
    """
    Rich Help Configuration class.

    When merging multiple RichHelpConfigurations together, user-defined values always
    take precedence over the class's defaults. When there are multiple user-defined values
    for a given field, the right-most field is used.
    """

    theme: Optional[Union[str, RichClickTheme]] = field(default=None)
    enable_theme_env_var: bool = field(default=True)

    # Default styles
    style_option: "StyleType" = field(default=FROM_THEME)
    style_option_negative: Optional["StyleType"] = field(default=FROM_THEME)
    style_argument: "StyleType" = field(default=FROM_THEME)
    style_command: "StyleType" = field(default=FROM_THEME)
    style_command_aliases: "StyleType" = field(default=FROM_THEME)
    style_switch: "StyleType" = field(default=FROM_THEME)
    style_switch_negative: Optional["StyleType"] = field(default=FROM_THEME)
    style_metavar: "StyleType" = field(default=FROM_THEME)
    style_metavar_append: "StyleType" = field(default=FROM_THEME)
    style_metavar_separator: "StyleType" = field(default=FROM_THEME)
    style_range_append: "StyleType" = field(default=FROM_THEME)
    style_header_text: "StyleType" = field(default=FROM_THEME)
    style_epilog_text: "StyleType" = field(default=FROM_THEME)
    style_footer_text: "StyleType" = field(default=FROM_THEME)
    style_usage: "StyleType" = field(default=FROM_THEME)
    style_usage_command: "StyleType" = field(default=FROM_THEME)
    style_usage_separator: "StyleType" = field(default=FROM_THEME)
    style_deprecated: "StyleType" = field(default=FROM_THEME)
    style_helptext_first_line: "StyleType" = field(default=FROM_THEME)
    style_helptext: "StyleType" = field(default=FROM_THEME)
    style_helptext_aliases: Optional["StyleType"] = field(default=None)
    style_option_help: "StyleType" = field(default=FROM_THEME)
    style_command_help: "StyleType" = field(default=FROM_THEME)
    style_option_default: "StyleType" = field(default=FROM_THEME)
    style_option_envvar: "StyleType" = field(default=FROM_THEME)
    style_required_short: "StyleType" = field(default=FROM_THEME)
    style_required_long: "StyleType" = field(default=FROM_THEME)
    style_options_panel_border: "StyleType" = field(default=FROM_THEME)
    style_options_panel_box: Optional[Union[str, "Box"]] = field(default=FROM_THEME)
    style_options_panel_help_style: "StyleType" = field(default=FROM_THEME)
    style_options_panel_title_style: "StyleType" = field(default=FROM_THEME)
    style_options_panel_padding: "PaddingDimensions" = field(default=FROM_THEME)
    style_options_panel_style: "StyleType" = field(default=FROM_THEME)
    align_options_panel: "AlignMethod" = field(default="left")
    style_options_table_show_lines: bool = field(default=False)
    style_options_table_leading: int = field(default=0)
    style_options_table_pad_edge: bool = field(default=False)
    style_options_table_padding: "PaddingDimensions" = field(default_factory=lambda: (0, 1))
    style_options_table_expand: bool = field(default=FROM_THEME)
    style_options_table_box: Optional[Union[str, "Box"]] = field(default=FROM_THEME)
    style_options_table_row_styles: Optional[List["StyleType"]] = field(default=None)
    style_options_table_border_style: Optional["StyleType"] = field(default=FROM_THEME)
    style_commands_panel_border: "StyleType" = field(default=FROM_THEME)
    panel_inline_help_in_title: bool = field(default=FROM_THEME)
    panel_inline_help_delimiter: str = field(default=FROM_THEME)
    style_commands_panel_box: Optional[Union[str, "Box"]] = field(default=FROM_THEME)
    style_commands_panel_help_style: "StyleType" = field(default=FROM_THEME)
    style_commands_panel_title_style: "StyleType" = field(default=FROM_THEME)
    style_commands_panel_padding: "PaddingDimensions" = field(default=FROM_THEME)
    style_commands_panel_style: "StyleType" = field(default=FROM_THEME)
    align_commands_panel: "AlignMethod" = field(default="left")
    style_commands_table_show_lines: bool = field(default=False)
    style_commands_table_leading: int = field(default=0)
    style_commands_table_pad_edge: bool = field(default=False)
    style_commands_table_padding: "PaddingDimensions" = field(default_factory=lambda: (0, 1))
    style_commands_table_expand: bool = field(default=FROM_THEME)
    style_commands_table_box: Optional[Union[str, "Box"]] = field(default=FROM_THEME)
    style_commands_table_row_styles: Optional[List["StyleType"]] = field(default=None)
    style_commands_table_border_style: Optional["StyleType"] = field(default=FROM_THEME)
    style_commands_table_column_width_ratio: Optional[Union[Tuple[None, None], Tuple[int, int]]] = field(
        default_factory=lambda: (None, None)
    )
    style_errors_panel_border: "StyleType" = field(default=FROM_THEME)
    style_errors_panel_box: Optional[Union[str, "Box"]] = field(default=FROM_THEME)
    align_errors_panel: "AlignMethod" = field(default="left")
    style_errors_suggestion: Optional["StyleType"] = field(default=None)
    style_errors_suggestion_command: Optional["StyleType"] = field(default=None)
    style_padding_errors: "StyleType" = field(default=FROM_THEME)
    style_aborted: "StyleType" = field(default="red")
    style_padding_usage: "StyleType" = field(default=FROM_THEME)
    style_padding_helptext: "StyleType" = field(default=FROM_THEME)
    style_padding_epilog: "StyleType" = field(default=FROM_THEME)

    panel_title_padding: int = field(default=FROM_THEME)
    width: Optional[int] = field(default_factory=terminal_width_default)
    max_width: Optional[int] = field(default_factory=terminal_width_default)
    color_system: Optional[Literal["auto", "standard", "256", "truecolor", "windows"]] = field(default="auto")
    force_terminal: Optional[bool] = field(default_factory=force_terminal_default)

    options_table_column_types: List[OptionColumnType] = field(default=FROM_THEME)
    commands_table_column_types: List[CommandColumnType] = field(default=FROM_THEME)
    options_table_help_sections: List[OptionHelpSectionType] = field(default=FROM_THEME)
    commands_table_help_sections: List[CommandHelpSectionType] = field(default=FROM_THEME)

    # Fixed strings
    header_text: Optional[Union[str, "Text"]] = field(default=None)
    footer_text: Optional[Union[str, "Text"]] = field(default=None)
    panel_title_string: str = field(default=FROM_THEME)
    deprecated_string: str = field(default=FROM_THEME)
    deprecated_with_reason_string: str = field(default=FROM_THEME)
    default_string: str = field(default=FROM_THEME)
    envvar_string: str = field(default=FROM_THEME)
    required_short_string: str = field(default=FROM_THEME)
    required_long_string: str = field(default=FROM_THEME)
    range_string: str = field(default=FROM_THEME)
    append_metavars_help_string: str = field(default=FROM_THEME)
    append_range_help_string: str = field(default=FROM_THEME)
    helptext_aliases_string: str = field(default="Aliases: {}")
    arguments_panel_title: str = field(default="Arguments")
    options_panel_title: str = field(default="Options")
    commands_panel_title: str = field(default="Commands")
    errors_panel_title: str = field(default="Error")
    delimiter_comma: str = field(default=FROM_THEME)
    delimiter_slash: str = field(default=FROM_THEME)
    errors_suggestion: Optional[Union[str, "Text"]] = field(default=None)
    """Defaults to Try 'cmd -h' for help. Set to False to disable."""
    errors_epilogue: Optional[Union[str, "Text"]] = field(default=None)
    aborted_text: str = field(default="Aborted.")

    padding_header_text: "PaddingDimensions" = field(default=FROM_THEME)
    padding_usage: "PaddingDimensions" = field(default=FROM_THEME)
    padding_helptext: "PaddingDimensions" = field(default=FROM_THEME)
    padding_helptext_deprecated: "PaddingDimensions" = field(default=0)
    padding_helptext_first_line: "PaddingDimensions" = field(default=0)
    padding_epilog: "PaddingDimensions" = field(default=FROM_THEME)
    padding_footer_text: "PaddingDimensions" = field(default=FROM_THEME)
    padding_errors_panel: "PaddingDimensions" = field(default=(0, 0, 1, 0))
    padding_errors_suggestion: "PaddingDimensions" = field(default=(0, 1, 0, 1))
    padding_errors_epilogue: "PaddingDimensions" = field(default=(0, 1, 1, 1))

    # Behaviours
    show_arguments: Optional[bool] = field(default=None)
    """Show positional arguments"""
    show_metavars_column: Optional[bool] = field(default=None)
    """Show a column with the option metavar (eg. INTEGER)"""
    commands_before_options: bool = field(default=False)
    """If set, the commands panel show above the options panel."""
    append_metavars_help: Optional[bool] = field(default=None)
    """Append metavar (eg. [TEXT]) after the help text"""
    group_arguments_options: bool = field(default=False)
    """Show arguments with options instead of in own panel"""
    option_envvar_first: Optional[bool] = field(default=None)
    """Show env vars before option help text instead of after"""
    text_markup: Literal["ansi", "rich", "markdown", None] = field(default=notset)
    """What engine to use to render the text. Default is 'ansi'."""
    text_kwargs: Optional[Dict[str, Any]] = field(default=None)
    """Additional kwargs to pass to Rich text rendering. Kwargs differ by text_markup chosen."""
    text_paragraph_linebreaks: Optional[Literal["\n", "\n\n"]] = field(default=None)
    text_emojis: bool = field(default=notset)
    """If set, parse emoji codes and replace with actual emojis, e.g. :smiley_cat: -> 😺"""
    use_markdown: Optional[bool] = field(default=None)
    """Silently deprecated; use `text_markup` field instead."""
    use_markdown_emoji: Optional[bool] = field(default=None)
    """Silently deprecated; use `text_emojis` instead."""
    use_rich_markup: Optional[bool] = field(default=None)
    """Silently deprecated; use `text_markup` field instead."""
    command_groups: Dict[str, List[CommandGroupDict]] = field(default_factory=lambda: {})
    """Define sorted groups of panels to display subcommands"""
    option_groups: Dict[str, List[OptionGroupDict]] = field(default_factory=lambda: {})
    """Define sorted groups of panels to display options and arguments"""
    use_click_short_help: bool = field(default=False)
    """Use click's default function to truncate help text"""
    helptext_show_aliases: bool = field(default=True)
    highlighter: Optional["Highlighter"] = field(default=None, repr=False, compare=False)
    """(Deprecated) Rich regex highlighter for help highlighting"""

    highlighter_patterns: List[str] = field(
        default_factory=lambda: [
            r"(^|[^\w\-])(?P<switch>-([^\W0-9][\w\-]*\w|[^\W0-9]))",
            r"(^|[^\w\-])(?P<option>--([^\W0-9][\w\-]*\w|[^\W0-9]))",
            r"(?P<metavar><[^>]+>)",
            r"(?P<deprecated>\(DEPRECATED(?:\: .*?)?\))$",
        ]
    )
    """Patterns to use with the option highlighter."""

    legacy_windows: Optional[bool] = field(default=None)

    def __post_init__(self) -> None:  # noqa: D105

        if self.highlighter is not None:
            import warnings

            warnings.warn(
                "`highlighter` kwarg is deprecated in RichHelpConfiguration."
                " Please do one of the following instead: either set highlighter_patterns=[...] if you want"
                " to use regex; or for more advanced use cases where you'd like to use a different type"
                " of rich.highlighter.Highlighter, subclass the `RichHelpFormatter` and update its `highlighter`.",
                DeprecationWarning,
                stacklevel=2,
            )

        if self.use_markdown is not None:
            import warnings

            warnings.warn(
                "`use_markdown=` will be deprecated in a future version of rich-click."
                " Please use `text_markup=` instead.",
                PendingDeprecationWarning,
                stacklevel=2,
            )

        if self.use_rich_markup is not None:
            import warnings

            warnings.warn(
                "`use_rich_markup=` will be deprecated in a future version of rich-click."
                " Please use `text_markup=` instead.",
                PendingDeprecationWarning,
                stacklevel=2,
            )

        if self.show_metavars_column is not None:
            import warnings

            warnings.warn(
                "`show_metavars_column=` will be deprecated in a future version of rich-click."
                " Please use `options_table_column_types=` instead for rich-click>=1.9.0."
                " The `options_table_column_types` config option lets you specify an ordered list"
                " of which columns are rendered and in what order. The default is:"
                " ['required', 'opt_short', 'opt_long', 'metavar', 'help']."
                " You can remove the metavar column by passing in a new list without 'metavar'.",
                PendingDeprecationWarning,
                stacklevel=2,
            )

        if self.append_metavars_help is not None:
            import warnings

            warnings.warn(
                "`append_metavars_help=` will be deprecated in a future version of rich-click."
                " Please use `options_table_help_sections=` instead for rich-click>=1.9.0."
                " The `options_table_help_sections=` config option lets you specify an ordered list"
                " of which sections are rendered and in what order. The default is:"
                " ['help', 'deprecated', 'envvar', 'default', 'required']."
                " You can append the metavar by passing in a new list with 'metavar'.",
                PendingDeprecationWarning,
                stacklevel=2,
            )

        if self.option_envvar_first is not None:
            import warnings

            warnings.warn(
                "`option_envvar_first=` will be deprecated in a future version of rich-click."
                " Please use `options_table_help_sections=` instead for rich-click>=1.9.0."
                " The `options_table_help_sections=` config option lets you specify an ordered list"
                " of which sections are rendered and in what order. The default is:"
                " ['help', 'deprecated', 'envvar', 'default', 'required']."
                " You can set the envvar first by passing in a new list with 'envvar' first.",
                PendingDeprecationWarning,
                stacklevel=2,
            )

        if self.use_markdown_emoji is not None:
            import warnings

            warnings.warn(
                "`use_markdown_emoji=` will be deprecated in a future version of rich-click."
                " Please use `text_emojis=` instead.",
                PendingDeprecationWarning,
                stacklevel=2,
            )

        self.__dataclass_fields__.pop("highlighter", None)

        self.apply_theme()

    @classmethod
    def load_from_globals(cls, module: Optional[ModuleType] = None, **extra: Any) -> "RichHelpConfiguration":
        """
        Build a RichHelpConfiguration from globals in rich_click.rich_click.

        When building from globals, all fields are treated as having been set by the user,
        meaning they will overwrite other fields when "merged".
        """
        if module is None:
            import rich_click.rich_click as rc

            module = rc
        kw = {}
        for k, v in cls.__dataclass_fields__.items():
            if v.init:
                if k != "highlighter" and hasattr(module, k.upper()):
                    kw[k] = getattr(module, k.upper())

        kw.update(extra)
        inst = cls(**kw)
        return inst

    def apply_theme(self, force_default: bool = False) -> None:
        theme: Optional[Union[str, RichClickTheme]] = None
        raise_key_error = True

        import rich_click.rich_click as rc

        if rc._THEME_FROM_CLI is not None:
            theme = rc._THEME_FROM_CLI
        if self.enable_theme_env_var and "RICH_CLICK_THEME" in os.environ:
            _theme = os.environ["RICH_CLICK_THEME"]
            _theme_cfg = _theme.strip()
            if _theme_cfg.startswith("{"):
                try:
                    data = json.loads(_theme_cfg)
                    # Extract theme before parsing everything else.
                    if isinstance(data, dict) and "theme" in data and theme is None:
                        theme = data["theme"]
                        raise_key_error = False
                        data.pop("theme")
                    for k, v in data.items():
                        if hasattr(self, k):
                            setattr(self, k, v)
                        else:
                            raise TypeError(f"'{type(self)}' has no attribute '{k}'")
                except Exception as e:
                    if force_default:  # only warn once
                        import warnings

                        warnings.warn(
                            f"RICH_CLICK_THEME= failed to parse: {e.__class__.__name__}{e.args}",
                            UserWarning,
                            stacklevel=2,
                        )
            elif theme is None:
                theme = _theme
                raise_key_error = False

        if theme is None:
            theme = self.theme

        theme_styles: Optional[Dict[str, Any]] = None

        if isinstance(theme, RichClickTheme):
            theme_styles = theme.styles
        elif theme is not None:
            theme_styles = get_theme(theme, raise_key_error=raise_key_error).styles

        if theme_styles is not None:
            for k, v in theme_styles.items():
                current = getattr(self, k)
                if isinstance(current, FromTheme):
                    setattr(self, k, v)

        if force_default:
            for k in self.__dataclass_fields__:
                v = getattr(self, k)
                if isinstance(v, FromTheme):
                    setattr(self, k, v.get_default(k))

        if force_default:
            # Handle deprecated fields here
            # must create new copy of these lists; don't modify in-place
            if self.text_markup is notset:
                if self.use_markdown:
                    self.text_markup = "markdown"
                elif self.use_rich_markup:
                    self.text_markup = "rich"
                else:
                    self.text_markup = "ansi"

            if self.text_emojis is notset:
                if self.use_markdown_emoji is not None:
                    self.text_emojis = self.use_markdown_emoji
                elif self.text_emojis is notset:
                    self.text_emojis = self.text_markup in {"markdown", "rich"}

            if self.show_metavars_column is False and "metavar" in self.options_table_column_types:
                self.options_table_column_types = [i for i in self.options_table_column_types if i != "metavar"]

            if self.append_metavars_help is True and "metavar" not in self.options_table_help_sections:
                self.options_table_help_sections = self.options_table_help_sections.copy() + ["metavar"]

            if self.option_envvar_first is True and "envvar" in self.options_table_help_sections:
                self.options_table_help_sections = ["envvar"] + [  # type: ignore[assignment]
                    i for i in self.options_table_help_sections if i != "envvar"
                ]

    def to_theme(self, **kwargs: Any) -> RichClickTheme:
        styles = kwargs.get("styles", {})
        for k, v in self.__dataclass_fields__.items():
            if k == "theme":
                continue
            styles.setdefault(k, getattr(self, k))
        kwargs.setdefault("name", "_from_config")
        kwargs["styles"] = styles
        return RichClickTheme(**kwargs)

    def dump_to_globals(self, module: Optional[ModuleType] = None) -> None:
        if module is None:
            import rich_click.rich_click as rc

            module = rc
        for k, v in self.__dataclass_fields__.items():
            if v.init:
                if hasattr(module, k.upper()):
                    setattr(module, k.upper(), getattr(self, k))


def __getattr__(name: str) -> Any:
    if name == "OptionHighlighter":
        from rich.highlighter import RegexHighlighter

        class OptionHighlighter(RegexHighlighter):
            """Highlights our special options."""

            highlights = [
                r"(^|[^\w\-])(?P<switch>-([^\W0-9][\w\-]*\w|[^\W0-9]))",
                r"(^|[^\w\-])(?P<option>--([^\W0-9][\w\-]*\w|[^\W0-9]))",
                r"(?P<metavar><[^>]+>)",
            ]

        import warnings

        warnings.warn(
            "OptionHighlighter is deprecated and will be removed in a future version.",
            DeprecationWarning,
            stacklevel=2,
        )

        globals()["OptionHighlighter"] = OptionHighlighter

        return OptionHighlighter

    else:
        raise AttributeError
