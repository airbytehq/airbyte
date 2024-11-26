import re
from enum import Enum
from typing import Iterable, Optional, Sequence


class ParseError(ValueError):
    def __init__(self, issue: str, offset: int, lines: Iterable[str]):
        self.line_num, self.position = self._get_line_number(offset, lines)
        super().__init__(f"{issue} at line {self.line_num} position {self.position}.")

    def _get_line_number(self, position: int, lines: Iterable[str]):
        line_num = 1
        for line in lines:
            if len(line) > position:
                break
            line_num += 1
            position -= len(line)
        return line_num, position


class ParserState(Enum):
    # Scanning for a new assignment
    SCAN_VAR_NAME = 0
    # In a value with no quoting
    SCAN_VALUE = 1
    # Inside single quotes
    IN_SINGLE_QUOTE = 2
    # Inside double quotes
    IN_DOUBLE_QUOTE = 3


VARNAME_PATTERN = r"^[\s\t;]*(?:export[\s\t]+)?([a-zA-Z_][a-zA-Z_0-9]*)"
ASSIGNMENT_PATTERN = f"{VARNAME_PATTERN}="
COMMENT_SUFFIX_PATTERN = r"^[\s\t;]*\#.*?\n"
WHITESPACE_PATTERN = r"^[\s\t;]*"
UNQUOTED_VALUE_PATTERN = r"^(.*?)(?:(\t|\s|;|'|\"|\\+))"
SINGLE_QUOTE_VALUE_PATTERN = r"^((?:.|\n)*?)'"
DOUBLE_QUOTE_VALUE_PATTERN = r"^((?:.|\n)*?)(\"|\\+)"


def parse_env_file(content_lines: Sequence[str]):
    """
    This function implements envfile parsing similar to bash.

    Line commenting is respected via # outside of quotes and following a non-escaped
    whitespace char.

    Escaping rules:
    - outside of quotes:
      - escaped new lines are omitted
      - other escaped characters are always included
        (including backslashes, whitespace and semicolons)
      - non-escaped backslashes are omitted
    - inside single quotes
      - backslashes are treated like normal character - no escaping
    - inside double quotes
      - escaped new lines are omitted
      - escaped backslashes and double-quotes are kept
      - backslashes not used for escaping are kept
    """

    content = "".join(content_lines) + "\n"
    result = {}
    cursor = 0
    state = ParserState.SCAN_VAR_NAME
    var_name: Optional[str] = ""
    var_content = []

    while cursor < len(content):
        if state == ParserState.SCAN_VAR_NAME:
            # scan for new variable assignment
            match = re.search(ASSIGNMENT_PATTERN, content[cursor:], re.MULTILINE)

            if match is None:
                comment_match = re.match(COMMENT_SUFFIX_PATTERN, content[cursor:])
                if comment_match:
                    cursor += comment_match.end()
                    continue

                if (
                    # ruff: noqa: E501
                    re.match(WHITESPACE_PATTERN, content[cursor:], re.MULTILINE).end()  # type: ignore[union-attr]
                    == len(content) - cursor
                ):
                    # The rest of the input is whitespace or semicolons
                    break

                # skip any immediate whitespace
                cursor += re.match(  # type: ignore[union-attr]
                    r"[\s\t\n]*", content[cursor:]
                ).span()[1]

                var_name_match = re.match(VARNAME_PATTERN, content[cursor:])
                if var_name_match:
                    cursor += var_name_match.span()[1]
                    raise ParseError(
                        "Expected assignment operator", cursor, content_lines
                    )

                raise ParseError("Expected variable assignment", cursor, content_lines)

            var_name = match.group(1)
            cursor += match.end()
            state = ParserState.SCAN_VALUE

        if state == ParserState.SCAN_VALUE:
            # collect up until the first quote, whitespace, or group of backslashes

            match = re.search(UNQUOTED_VALUE_PATTERN, content[cursor:], re.MULTILINE)
            assert match
            new_var_content, match_terminator = match.groups()
            var_content.append(new_var_content)
            cursor += len(new_var_content)

            if match_terminator.isspace() or match_terminator == ";":
                assert var_name
                result[var_name] = "".join(var_content)
                var_name = None
                var_content = []
                state = ParserState.SCAN_VAR_NAME
                continue

            if match_terminator == "'":
                cursor += 1
                state = ParserState.IN_SINGLE_QUOTE

            elif match_terminator == '"':
                cursor += 1
                state = ParserState.IN_DOUBLE_QUOTE
                continue

            else:
                # We found one or more backslashes
                num_backslashes = len(match_terminator)
                # Keep the excess (escaped) backslashes
                var_content.append("\\" * (num_backslashes // 2))
                cursor += num_backslashes

                if num_backslashes % 2 != 0:
                    next_char = content[cursor]
                    cursor += 1

                    if next_char == "\n":
                        # Omit escaped new line
                        continue

                    # Non-escaped backslashes that don't precede a terminator are
                    # dropped
                    var_content.append(next_char)
                    continue

        if state == ParserState.IN_SINGLE_QUOTE:
            # collect characters up until a single quote
            match = re.search(
                SINGLE_QUOTE_VALUE_PATTERN, content[cursor:], re.MULTILINE
            )
            if match is None:
                raise ParseError("Unmatched single quote", cursor, content_lines)
            var_content.append(match.group(1))
            cursor += match.end()
            state = ParserState.SCAN_VALUE
            continue

        if state == ParserState.IN_DOUBLE_QUOTE:
            # collect characters up until a run of backslashes or double quote
            match = re.search(
                DOUBLE_QUOTE_VALUE_PATTERN, content[cursor:], re.MULTILINE
            )
            if match is None:
                raise ParseError("Unmatched double quote", cursor, content_lines)
            new_var_content, backslashes_or_dquote = match.groups()
            var_content.append(new_var_content)
            cursor += match.end()

            if backslashes_or_dquote == '"':
                state = ParserState.SCAN_VALUE
                continue

            # We found one or more backslashes
            num_backslashes = len(backslashes_or_dquote)

            # Keep the excess (escaped) backslashes
            var_content.append("\\" * (num_backslashes // 2))

            if num_backslashes % 2 != 0:
                # Odd number of backslashes maybe an escape sequence
                next_char = content[cursor]
                cursor += 1
                if next_char == "\n":
                    # Omit escaped new line
                    pass
                if next_char == '"':
                    var_content.append(next_char)
                else:
                    # otherwise keep the backslash
                    var_content.append("\\" + next_char)

    return result
