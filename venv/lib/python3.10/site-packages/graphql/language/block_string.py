from typing import Collection, List
from sys import maxsize

__all__ = [
    "dedent_block_string_lines",
    "is_printable_as_block_string",
    "print_block_string",
]


def dedent_block_string_lines(lines: Collection[str]) -> List[str]:
    """Produce the value of a block string from its parsed raw value.

    This function works similar to CoffeeScript's block string,
    Python's docstring trim or Ruby's strip_heredoc.

    It implements the GraphQL spec's BlockStringValue() static algorithm.

    Note that this is very similar to Python's inspect.cleandoc() function.
    The difference is that the latter also expands tabs to spaces and
    removes whitespace at the beginning of the first line. Python also has
    textwrap.dedent() which uses a completely different algorithm.

    For internal use only.
    """
    common_indent = maxsize
    first_non_empty_line = None
    last_non_empty_line = -1

    for i, line in enumerate(lines):
        indent = leading_white_space(line)

        if indent == len(line):
            continue  # skip empty lines

        if first_non_empty_line is None:
            first_non_empty_line = i
        last_non_empty_line = i

        if i and indent < common_indent:
            common_indent = indent

    if first_non_empty_line is None:
        first_non_empty_line = 0

    return [  # Remove common indentation from all lines but first.
        line[common_indent:] if i else line for i, line in enumerate(lines)
    ][  # Remove leading and trailing blank lines.
        first_non_empty_line : last_non_empty_line + 1
    ]


def leading_white_space(s: str) -> int:
    i = 0
    for c in s:
        if c not in " \t":
            return i
        i += 1
    return i


def is_printable_as_block_string(value: str) -> bool:
    """Check whether the given string is printable as a block string.

    For internal use only.
    """
    if not isinstance(value, str):
        value = str(value)  # resolve lazy string proxy object

    if not value:
        return True  # emtpy string is printable

    is_empty_line = True
    has_indent = False
    has_common_indent = True
    seen_non_empty_line = False

    for c in value:
        if c == "\n":
            if is_empty_line and not seen_non_empty_line:
                return False  # has leading new line
            seen_non_empty_line = True
            is_empty_line = True
            has_indent = False
        elif c in " \t":
            has_indent = has_indent or is_empty_line
        elif c <= "\x0f":
            return False
        else:
            has_common_indent = has_common_indent and has_indent
            is_empty_line = False

    if is_empty_line:
        return False  # has trailing empty lines

    if has_common_indent and seen_non_empty_line:
        return False  # has internal indent

    return True


def print_block_string(value: str, minimize: bool = False) -> str:
    """Print a block string in the indented block form.

    Prints a block string in the indented block form by adding a leading and
    trailing blank line. However, if a block string starts with whitespace and
    is a single-line, adding a leading blank line would strip that whitespace.

    For internal use only.
    """
    if not isinstance(value, str):
        value = str(value)  # resolve lazy string proxy object

    escaped_value = value.replace('"""', '\\"""')

    # Expand a block string's raw value into independent lines.
    lines = escaped_value.splitlines() or [""]
    num_lines = len(lines)
    is_single_line = num_lines == 1

    # If common indentation is found,
    # we can fix some of those cases by adding a leading new line.
    force_leading_new_line = num_lines > 1 and all(
        not line or line[0] in " \t" for line in lines[1:]
    )

    # Trailing triple quotes just looks confusing but doesn't force trailing new line.
    has_trailing_triple_quotes = escaped_value.endswith('\\"""')

    # Trailing quote (single or double) or slash forces trailing new line
    has_trailing_quote = value.endswith('"') and not has_trailing_triple_quotes
    has_trailing_slash = value.endswith("\\")
    force_trailing_new_line = has_trailing_quote or has_trailing_slash

    print_as_multiple_lines = not minimize and (
        # add leading and trailing new lines only if it improves readability
        not is_single_line
        or len(value) > 70
        or force_trailing_new_line
        or force_leading_new_line
        or has_trailing_triple_quotes
    )

    # Format a multi-line block quote to account for leading space.
    skip_leading_new_line = is_single_line and value and value[0] in " \t"
    before = (
        "\n"
        if print_as_multiple_lines
        and not skip_leading_new_line
        or force_leading_new_line
        else ""
    )
    after = "\n" if print_as_multiple_lines or force_trailing_new_line else ""

    return f'"""{before}{escaped_value}{after}"""'
