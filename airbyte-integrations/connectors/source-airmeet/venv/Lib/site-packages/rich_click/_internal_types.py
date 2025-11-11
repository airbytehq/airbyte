"""
Contains types for .pyi files.
Import from this at your own risk.
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Literal,
    Mapping,
    MutableMapping,
    Optional,
    Tuple,
    TypedDict,
    Union,
)

from rich_click.utils import CommandGroupDict, OptionGroupDict


if TYPE_CHECKING:
    import sys

    from rich.align import AlignMethod
    from rich.box import Box
    from rich.console import Console, JustifyMethod
    from rich.padding import PaddingDimensions
    from rich.style import StyleType
    from rich.text import Text, TextType

    from rich_click.rich_click_theme import RichClickTheme
    from rich_click.rich_help_configuration import (
        CommandColumnType,
        CommandHelpSectionType,
        OptionColumnType,
        OptionHelpSectionType,
        RichHelpConfiguration,
    )

    if sys.version_info < (3, 11):
        from typing_extensions import NotRequired
    else:
        from typing import NotRequired


class RichContextSettingsDict(TypedDict):
    obj: NotRequired["Any | None"]
    auto_envvar_prefix: NotRequired[Optional[str]]
    default_map: NotRequired[MutableMapping[str, Any] | None]
    terminal_width: NotRequired[Optional[int]]
    max_content_width: NotRequired[Optional[int]]
    resilient_parsing: NotRequired[bool]
    allow_extra_args: NotRequired[Optional[bool]]
    allow_interspersed_args: NotRequired[Optional[bool]]
    ignore_unknown_options: NotRequired[Optional[bool]]
    help_option_names: NotRequired[Optional[List[str]]]
    token_normalize_func: NotRequired[Callable[[str], str] | None]
    color: NotRequired[Optional[bool]]
    show_default: NotRequired[Optional[bool]]
    rich_console: NotRequired[Optional["Console"]]
    rich_help_config: NotRequired[Optional[Union[Mapping[str, Any], RichHelpConfiguration]]]
    export_console_as: NotRequired[Optional[Literal["html", "svg", "text"]]]
    errors_in_output_format: NotRequired[Optional[bool]]
    help_to_stderr: NotRequired[Optional[bool]]


class TableKwargs(TypedDict):
    title: NotRequired[Optional["TextType"]]
    caption: NotRequired[Optional["TextType"]]
    width: NotRequired[Optional[int]]
    min_width: NotRequired[Optional[int]]
    box: NotRequired[Optional[Union[str, "Box"]]]
    safe_box: NotRequired[Optional[bool]]
    padding: NotRequired["PaddingDimensions"]
    collapse_padding: NotRequired[bool]
    pad_edge: NotRequired[bool]
    expand: NotRequired[bool]
    show_header: NotRequired[bool]
    show_footer: NotRequired[bool]
    show_edge: NotRequired[bool]
    show_lines: NotRequired[bool]
    leading: NotRequired[int]
    style: NotRequired["StyleType"]
    row_styles: NotRequired[Optional[Iterable["StyleType"]]]
    header_style: NotRequired[Optional["StyleType"]]
    footer_style: NotRequired[Optional["StyleType"]]
    border_style: NotRequired[Optional["StyleType"]]
    title_style: NotRequired[Optional["StyleType"]]
    caption_style: NotRequired[Optional["StyleType"]]
    title_justify: NotRequired["JustifyMethod"]
    caption_justify: NotRequired["JustifyMethod"]
    highlight: NotRequired[bool]


class PanelKwargs(TypedDict):
    box: NotRequired[Union[str, "Box"]]
    title: NotRequired[Optional["TextType"]]
    title_align: NotRequired["AlignMethod"]
    subtitle: NotRequired[Optional["TextType"]]
    subtitle_align: NotRequired["AlignMethod"]
    safe_box: NotRequired[Optional[bool]]
    expand: NotRequired[bool]
    style: NotRequired["StyleType"]
    border_style: NotRequired["StyleType"]
    width: NotRequired[Optional[int]]
    height: NotRequired[Optional[int]]
    padding: NotRequired["PaddingDimensions"]
    highlight: NotRequired[bool]


class RichHelpConfigurationDict(TypedDict):
    """Typed dict for rich_config() kwargs."""

    theme: NotRequired[Optional[Union[str, "RichClickTheme"]]]
    enable_theme_env_var: NotRequired[bool]
    style_option: NotRequired["StyleType"]
    style_option_negative: NotRequired[Optional["StyleType"]]
    style_argument: NotRequired["StyleType"]
    style_command: NotRequired["StyleType"]
    style_command_aliases: NotRequired["StyleType"]
    style_switch: NotRequired["StyleType"]
    style_switch_negative: NotRequired[Optional["StyleType"]]
    style_metavar: NotRequired["StyleType"]
    style_metavar_append: NotRequired["StyleType"]
    style_metavar_separator: NotRequired["StyleType"]
    style_range_append: NotRequired["StyleType"]
    style_header_text: NotRequired["StyleType"]
    style_epilog_text: NotRequired["StyleType"]
    style_footer_text: NotRequired["StyleType"]
    style_usage: NotRequired["StyleType"]
    style_usage_command: NotRequired["StyleType"]
    style_usage_separator: NotRequired["StyleType"]
    style_deprecated: NotRequired["StyleType"]
    style_helptext_first_line: NotRequired["StyleType"]
    style_helptext: NotRequired["StyleType"]
    style_helptext_aliases: NotRequired[Optional["StyleType"]]
    style_option_help: NotRequired["StyleType"]
    style_command_help: NotRequired["StyleType"]
    style_option_default: NotRequired["StyleType"]
    style_option_envvar: NotRequired["StyleType"]
    style_required_short: NotRequired["StyleType"]
    style_required_long: NotRequired["StyleType"]
    style_options_panel_border: NotRequired["StyleType"]
    style_options_panel_box: NotRequired[Optional[Union[str, "Box"]]]
    style_options_panel_help_style: NotRequired["StyleType"]
    style_options_panel_title_style: NotRequired["StyleType"]
    style_options_panel_padding: NotRequired["PaddingDimensions"]
    style_options_panel_style: NotRequired["StyleType"]
    align_options_panel: NotRequired["AlignMethod"]
    style_options_table_show_lines: NotRequired[bool]
    style_options_table_leading: NotRequired[int]
    style_options_table_pad_edge: NotRequired[bool]
    style_options_table_padding: NotRequired["PaddingDimensions"]
    style_options_table_expand: NotRequired[bool]
    style_options_table_box: NotRequired[Optional[Union[str, "Box"]]]
    style_options_table_row_styles: NotRequired[Optional[List["StyleType"]]]
    style_options_table_border_style: NotRequired[Optional["StyleType"]]
    style_commands_panel_border: NotRequired["StyleType"]
    panel_inline_help_in_title: NotRequired[bool]
    panel_inline_help_delimiter: NotRequired[str]
    style_commands_panel_box: NotRequired[Optional[Union[str, "Box"]]]
    style_commands_panel_help_style: NotRequired["StyleType"]
    style_commands_panel_title_style: NotRequired["StyleType"]
    style_commands_panel_padding: NotRequired["PaddingDimensions"]
    style_commands_panel_style: NotRequired["StyleType"]
    align_commands_panel: NotRequired[AlignMethod]
    style_commands_table_show_lines: NotRequired[bool]
    style_commands_table_leading: NotRequired[int]
    style_commands_table_pad_edge: NotRequired[bool]
    style_commands_table_padding: NotRequired["PaddingDimensions"]
    style_commands_table_expand: NotRequired[bool]
    style_commands_table_box: NotRequired[Optional[Union[str, "Box"]]]
    style_commands_table_row_styles: NotRequired[Optional[List["StyleType"]]]
    style_commands_table_border_style: NotRequired[Optional["StyleType"]]
    style_commands_table_column_width_ratio: NotRequired[Optional[Union[Tuple[None, None], Tuple[int, int]]]]
    style_errors_panel_border: NotRequired["StyleType"]
    style_errors_panel_box: NotRequired[Optional[Union[str, "Box"]]]
    align_errors_panel: NotRequired[AlignMethod]
    style_errors_suggestion: NotRequired[Optional["StyleType"]]
    style_errors_suggestion_command: NotRequired[Optional["StyleType"]]
    style_padding_errors: NotRequired["StyleType"]
    style_aborted: NotRequired["StyleType"]
    style_padding_usage: NotRequired["StyleType"]
    style_padding_helptext: NotRequired["StyleType"]
    style_padding_epilog: NotRequired["StyleType"]

    panel_title_padding: NotRequired[int]
    width: NotRequired[Optional[int]]
    max_width: NotRequired[Optional[int]]
    color_system: NotRequired[Optional[Literal["auto", "standard", "256", "truecolor", "windows"]]]
    force_terminal: NotRequired[Optional[bool]]
    options_table_column_types: NotRequired[List["OptionColumnType"]]
    commands_table_column_types: NotRequired[List["CommandColumnType"]]
    options_table_help_sections: NotRequired[List["OptionHelpSectionType"]]
    commands_table_help_sections: NotRequired[List["CommandHelpSectionType"]]

    header_text: NotRequired[Optional[Union[str, "Text"]]]
    footer_text: NotRequired[Optional[Union[str, "Text"]]]
    panel_title_string: NotRequired[str]
    deprecated_string: NotRequired[str]
    deprecated_with_reason_string: NotRequired[str]
    default_string: NotRequired[str]
    envvar_string: NotRequired[str]
    required_short_string: NotRequired[str]
    required_long_string: NotRequired[str]
    range_string: NotRequired[str]
    append_metavars_help_string: NotRequired[str]
    append_range_help_string: NotRequired[str]
    helptext_aliases_string: NotRequired[str]
    arguments_panel_title: NotRequired[str]
    options_panel_title: NotRequired[str]
    commands_panel_title: NotRequired[str]
    errors_panel_title: NotRequired[str]
    delimiter_comma: NotRequired[str]
    delimiter_slash: NotRequired[str]
    errors_suggestion: NotRequired[Optional[Union[str, Text]]]
    errors_epilogue: NotRequired[Optional[Union[str, Text]]]
    aborted_text: NotRequired[str]
    padding_header_text: NotRequired["PaddingDimensions"]
    padding_helptext: NotRequired["PaddingDimensions"]
    padding_helptext_deprecated: NotRequired["PaddingDimensions"]
    padding_helptext_first_line: NotRequired["PaddingDimensions"]
    padding_usage: NotRequired["PaddingDimensions"]
    padding_epilog: NotRequired["PaddingDimensions"]
    padding_footer_text: NotRequired["PaddingDimensions"]
    padding_errors_panel: NotRequired["PaddingDimensions"]
    padding_errors_suggestion: NotRequired["PaddingDimensions"]
    padding_errors_epilogue: NotRequired["PaddingDimensions"]

    # Behaviours
    show_arguments: NotRequired[Optional[bool]]
    show_metavars_column: NotRequired[Optional[bool]]
    commands_before_options: NotRequired[bool]
    append_metavars_help: NotRequired[Optional[bool]]
    group_arguments_options: NotRequired[bool]
    option_envvar_first: NotRequired[Optional[bool]]
    text_markup: NotRequired[Literal["ansi", "rich", "markdown", None]]
    text_kwargs: NotRequired[Optional[Dict[str, Any]]]
    text_emojis: NotRequired[bool]
    text_paragraph_linebreaks: NotRequired[Optional[Literal["\n", "\n\n"]]]
    use_markdown: NotRequired[Optional[bool]]
    use_markdown_emoji: NotRequired[Optional[bool]]
    use_rich_markup: NotRequired[Optional[bool]]
    command_groups: NotRequired[Dict[str, List[CommandGroupDict]]]
    option_groups: NotRequired[Dict[str, List[OptionGroupDict]]]
    use_click_short_help: NotRequired[bool]
    helptext_show_aliases: NotRequired[bool]
    highlighter_patterns: NotRequired[List[str]]
    legacy_windows: NotRequired[Optional[bool]]
