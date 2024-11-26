from typing import List, NamedTuple, Optional

from ..error import GraphQLSyntaxError
from .ast import Token
from .block_string import dedent_block_string_lines
from .character_classes import is_digit, is_name_start, is_name_continue
from .source import Source
from .token_kind import TokenKind

__all__ = ["Lexer", "is_punctuator_token_kind"]


class EscapeSequence(NamedTuple):
    """The string value and lexed size of an escape sequence."""

    value: str
    size: int


class Lexer:
    """GraphQL Lexer

    A Lexer is a stateful stream generator in that every time it is advanced, it returns
    the next token in the Source. Assuming the source lexes, the final Token emitted by
    the lexer will be of kind EOF, after which the lexer will repeatedly return the same
    EOF token whenever called.
    """

    def __init__(self, source: Source):
        """Given a Source object, initialize a Lexer for that source."""
        self.source = source
        self.token = self.last_token = Token(TokenKind.SOF, 0, 0, 0, 0)
        self.line, self.line_start = 1, 0

    def advance(self) -> Token:
        """Advance the token stream to the next non-ignored token."""
        self.last_token = self.token
        token = self.token = self.lookahead()
        return token

    def lookahead(self) -> Token:
        """Look ahead and return the next non-ignored token, but do not change state."""
        token = self.token
        if token.kind != TokenKind.EOF:
            while True:
                if token.next:
                    token = token.next
                else:
                    # Read the next token and form a link in the token linked-list.
                    next_token = self.read_next_token(token.end)
                    token.next = next_token
                    next_token.prev = token
                    token = next_token
                if token.kind != TokenKind.COMMENT:
                    break
        return token

    def print_code_point_at(self, location: int) -> str:
        """Print the code point at the given location.

        Prints the code point (or end of file reference) at a given location in a
        source for use in error messages.

        Printable ASCII is printed quoted, while other points are printed in Unicode
        code point form (ie. U+1234).
        """
        body = self.source.body
        if location >= len(body):
            return TokenKind.EOF.value
        char = body[location]
        # Printable ASCII
        if "\x20" <= char <= "\x7E":
            return "'\"'" if char == '"' else f"'{char}'"
        # Unicode code point
        point = ord(
            body[location : location + 2]
            .encode("utf-16", "surrogatepass")
            .decode("utf-16")
            if is_supplementary_code_point(body, location)
            else char
        )
        return f"U+{point:04X}"

    def create_token(
        self, kind: TokenKind, start: int, end: int, value: Optional[str] = None
    ) -> Token:
        """Create a token with line and column location information."""
        line = self.line
        col = 1 + start - self.line_start
        return Token(kind, start, end, line, col, value)

    def read_next_token(self, start: int) -> Token:
        """Get the next token from the source starting at the given position.

        This skips over whitespace until it finds the next lexable token, then lexes
        punctuators immediately or calls the appropriate helper function for more
        complicated tokens.
        """
        body = self.source.body
        body_length = len(body)
        position = start

        while position < body_length:
            char = body[position]  # SourceCharacter

            if char in " \t,\ufeff":
                position += 1
                continue
            elif char == "\n":
                position += 1
                self.line += 1
                self.line_start = position
                continue
            elif char == "\r":
                if body[position + 1 : position + 2] == "\n":
                    position += 2
                else:
                    position += 1
                self.line += 1
                self.line_start = position
                continue

            if char == "#":
                return self.read_comment(position)

            if char == '"':
                if body[position + 1 : position + 3] == '""':
                    return self.read_block_string(position)
                return self.read_string(position)

            kind = _KIND_FOR_PUNCT.get(char)
            if kind:
                return self.create_token(kind, position, position + 1)

            if is_digit(char) or char == "-":
                return self.read_number(position, char)

            if is_name_start(char):
                return self.read_name(position)

            if char == ".":
                if body[position + 1 : position + 3] == "..":
                    return self.create_token(TokenKind.SPREAD, position, position + 3)

            message = (
                "Unexpected single quote character ('),"
                ' did you mean to use a double quote (")?'
                if char == "'"
                else (
                    f"Unexpected character: {self.print_code_point_at(position)}."
                    if is_unicode_scalar_value(char)
                    or is_supplementary_code_point(body, position)
                    else f"Invalid character: {self.print_code_point_at(position)}."
                )
            )

            raise GraphQLSyntaxError(self.source, position, message)

        return self.create_token(TokenKind.EOF, body_length, body_length)

    def read_comment(self, start: int) -> Token:
        """Read a comment token from the source file."""
        body = self.source.body
        body_length = len(body)

        position = start + 1
        while position < body_length:
            char = body[position]
            if char in "\r\n":
                break
            if is_unicode_scalar_value(char):
                position += 1
            elif is_supplementary_code_point(body, position):
                position += 2
            else:
                break  # pragma: no cover

        return self.create_token(
            TokenKind.COMMENT,
            start,
            position,
            body[start + 1 : position],
        )

    def read_number(self, start: int, first_char: str) -> Token:
        """Reads a number token from the source file.

        This can be either a FloatValue or an IntValue,
        depending on whether a FractionalPart or ExponentPart is encountered.
        """
        body = self.source.body
        position = start
        char = first_char
        is_float = False

        if char == "-":
            position += 1
            char = body[position : position + 1]
        if char == "0":
            position += 1
            char = body[position : position + 1]
            if is_digit(char):
                raise GraphQLSyntaxError(
                    self.source,
                    position,
                    "Invalid number, unexpected digit after 0:"
                    f" {self.print_code_point_at(position)}.",
                )
        else:
            position = self.read_digits(position, char)
            char = body[position : position + 1]
        if char == ".":
            is_float = True
            position += 1
            char = body[position : position + 1]
            position = self.read_digits(position, char)
            char = body[position : position + 1]
        if char and char in "Ee":
            is_float = True
            position += 1
            char = body[position : position + 1]
            if char and char in "+-":
                position += 1
                char = body[position : position + 1]
            position = self.read_digits(position, char)
            char = body[position : position + 1]

        # Numbers cannot be followed by . or NameStart
        if char and (char == "." or is_name_start(char)):
            raise GraphQLSyntaxError(
                self.source,
                position,
                "Invalid number, expected digit but got:"
                f" {self.print_code_point_at(position)}.",
            )

        return self.create_token(
            TokenKind.FLOAT if is_float else TokenKind.INT,
            start,
            position,
            body[start:position],
        )

    def read_digits(self, start: int, first_char: str) -> int:
        """Return the new position in the source after reading one or more digits."""
        if not is_digit(first_char):
            raise GraphQLSyntaxError(
                self.source,
                start,
                "Invalid number, expected digit but got:"
                f" {self.print_code_point_at(start)}.",
            )

        body = self.source.body
        body_length = len(body)
        position = start + 1
        while position < body_length and is_digit(body[position]):
            position += 1
        return position

    def read_string(self, start: int) -> Token:
        """Read a single-quote string token from the source file."""
        body = self.source.body
        body_length = len(body)
        position = start + 1
        chunk_start = position
        value: List[str] = []
        append = value.append

        while position < body_length:
            char = body[position]

            if char == '"':
                append(body[chunk_start:position])
                return self.create_token(
                    TokenKind.STRING,
                    start,
                    position + 1,
                    "".join(value),
                )

            if char == "\\":
                append(body[chunk_start:position])
                escape = (
                    (
                        self.read_escaped_unicode_variable_width(position)
                        if body[position + 2 : position + 3] == "{"
                        else self.read_escaped_unicode_fixed_width(position)
                    )
                    if body[position + 1 : position + 2] == "u"
                    else self.read_escaped_character(position)
                )
                append(escape.value)
                position += escape.size
                chunk_start = position
                continue

            if char in "\r\n":
                break

            if is_unicode_scalar_value(char):
                position += 1
            elif is_supplementary_code_point(body, position):
                position += 2
            else:
                raise GraphQLSyntaxError(
                    self.source,
                    position,
                    "Invalid character within String:"
                    f" {self.print_code_point_at(position)}.",
                )

        raise GraphQLSyntaxError(self.source, position, "Unterminated string.")

    def read_escaped_unicode_variable_width(self, position: int) -> EscapeSequence:
        body = self.source.body
        point = 0
        size = 3
        max_size = min(12, len(body) - position)
        # Cannot be larger than 12 chars (\u{00000000}).
        while size < max_size:
            char = body[position + size]
            size += 1
            if char == "}":
                # Must be at least 5 chars (\u{0}) and encode a Unicode scalar value.
                if size < 5 or not (
                    0 <= point <= 0xD7FF or 0xE000 <= point <= 0x10FFFF
                ):
                    break
                return EscapeSequence(chr(point), size)
            # Append this hex digit to the code point.
            point = (point << 4) | read_hex_digit(char)
            if point < 0:
                break

        raise GraphQLSyntaxError(
            self.source,
            position,
            f"Invalid Unicode escape sequence: '{body[position: position + size]}'.",
        )

    def read_escaped_unicode_fixed_width(self, position: int) -> EscapeSequence:
        body = self.source.body
        code = read_16_bit_hex_code(body, position + 2)

        if 0 <= code <= 0xD7FF or 0xE000 <= code <= 0x10FFFF:
            return EscapeSequence(chr(code), 6)

        # GraphQL allows JSON-style surrogate pair escape sequences, but only when
        # a valid pair is formed.
        if 0xD800 <= code <= 0xDBFF:
            if body[position + 6 : position + 8] == "\\u":
                trailing_code = read_16_bit_hex_code(body, position + 8)
                if 0xDC00 <= trailing_code <= 0xDFFF:
                    return EscapeSequence(
                        (chr(code) + chr(trailing_code))
                        .encode("utf-16", "surrogatepass")
                        .decode("utf-16"),
                        12,
                    )

        raise GraphQLSyntaxError(
            self.source,
            position,
            f"Invalid Unicode escape sequence: '{body[position: position + 6]}'.",
        )

    def read_escaped_character(self, position: int) -> EscapeSequence:
        body = self.source.body
        value = _ESCAPED_CHARS.get(body[position + 1])
        if value:
            return EscapeSequence(value, 2)
        raise GraphQLSyntaxError(
            self.source,
            position,
            f"Invalid character escape sequence: '{body[position: position + 2]}'.",
        )

    def read_block_string(self, start: int) -> Token:
        """Read a block string token from the source file."""
        body = self.source.body
        body_length = len(body)
        line_start = self.line_start

        position = start + 3
        chunk_start = position
        current_line = ""

        block_lines = []
        while position < body_length:
            char = body[position]

            if char == '"' and body[position + 1 : position + 3] == '""':
                current_line += body[chunk_start:position]
                block_lines.append(current_line)

                token = self.create_token(
                    TokenKind.BLOCK_STRING,
                    start,
                    position + 3,
                    # return a string of the lines joined with new lines
                    "\n".join(dedent_block_string_lines(block_lines)),
                )

                self.line += len(block_lines) - 1
                self.line_start = line_start
                return token

            if char == "\\" and body[position + 1 : position + 4] == '"""':
                current_line += body[chunk_start:position]
                chunk_start = position + 1  # skip only slash
                position += 4
                continue

            if char in "\r\n":
                current_line += body[chunk_start:position]
                block_lines.append(current_line)

                if char == "\r" and body[position + 1 : position + 2] == "\n":
                    position += 2
                else:
                    position += 1

                current_line = ""
                chunk_start = line_start = position
                continue

            if is_unicode_scalar_value(char):
                position += 1
            elif is_supplementary_code_point(body, position):
                position += 2
            else:
                raise GraphQLSyntaxError(
                    self.source,
                    position,
                    "Invalid character within String:"
                    f" {self.print_code_point_at(position)}.",
                )

        raise GraphQLSyntaxError(self.source, position, "Unterminated string.")

    def read_name(self, start: int) -> Token:
        """Read an alphanumeric + underscore name from the source."""
        body = self.source.body
        body_length = len(body)
        position = start + 1

        while position < body_length:
            char = body[position]
            if not is_name_continue(char):
                break
            position += 1

        return self.create_token(TokenKind.NAME, start, position, body[start:position])


_punctuator_token_kinds = frozenset(
    [
        TokenKind.BANG,
        TokenKind.DOLLAR,
        TokenKind.AMP,
        TokenKind.PAREN_L,
        TokenKind.PAREN_R,
        TokenKind.SPREAD,
        TokenKind.COLON,
        TokenKind.EQUALS,
        TokenKind.AT,
        TokenKind.BRACKET_L,
        TokenKind.BRACKET_R,
        TokenKind.BRACE_L,
        TokenKind.PIPE,
        TokenKind.BRACE_R,
    ]
)


def is_punctuator_token_kind(kind: TokenKind) -> bool:
    """Check whether the given token kind corresponds to a punctuator.

    For internal use only.
    """
    return kind in _punctuator_token_kinds


_KIND_FOR_PUNCT = {
    "!": TokenKind.BANG,
    "$": TokenKind.DOLLAR,
    "&": TokenKind.AMP,
    "(": TokenKind.PAREN_L,
    ")": TokenKind.PAREN_R,
    ":": TokenKind.COLON,
    "=": TokenKind.EQUALS,
    "@": TokenKind.AT,
    "[": TokenKind.BRACKET_L,
    "]": TokenKind.BRACKET_R,
    "{": TokenKind.BRACE_L,
    "}": TokenKind.BRACE_R,
    "|": TokenKind.PIPE,
}


_ESCAPED_CHARS = {
    '"': '"',
    "/": "/",
    "\\": "\\",
    "b": "\b",
    "f": "\f",
    "n": "\n",
    "r": "\r",
    "t": "\t",
}


def read_16_bit_hex_code(body: str, position: int) -> int:
    """Read a 16bit hexadecimal string and return its positive integer value (0-65535).

    Reads four hexadecimal characters and returns the positive integer that 16bit
    hexadecimal string represents. For example, "000f" will return 15, and "dead"
    will return 57005.

    Returns a negative number if any char was not a valid hexadecimal digit.
    """
    # read_hex_digit() returns -1 on error. ORing a negative value with any other
    # value always produces a negative value.
    return (
        read_hex_digit(body[position]) << 12
        | read_hex_digit(body[position + 1]) << 8
        | read_hex_digit(body[position + 2]) << 4
        | read_hex_digit(body[position + 3])
    )


def read_hex_digit(char: str) -> int:
    """Read a hexadecimal character and returns its positive integer value (0-15).

    '0' becomes 0, '9' becomes 9
    'A' becomes 10, 'F' becomes 15
    'a' becomes 10, 'f' becomes 15

    Returns -1 if the provided character code was not a valid hexadecimal digit.
    """
    if "0" <= char <= "9":
        return ord(char) - 48
    elif "A" <= char <= "F":
        return ord(char) - 55
    elif "a" <= char <= "f":
        return ord(char) - 87
    return -1


def is_unicode_scalar_value(char: str) -> bool:
    """Check whether this is a Unicode scalar value.

    A Unicode scalar value is any Unicode code point except surrogate code
    points. In other words, the inclusive ranges of values 0x0000 to 0xD7FF and
    0xE000 to 0x10FFFF.
    """
    return "\x00" <= char <= "\ud7ff" or "\ue000" <= char <= "\U0010ffff"


def is_supplementary_code_point(body: str, location: int) -> bool:
    """
    Check whether the current location is a supplementary code point.

    The GraphQL specification defines source text as a sequence of unicode scalar
    values (which Unicode defines to exclude surrogate code points).
    """
    try:
        return (
            "\ud800" <= body[location] <= "\udbff"
            and "\udc00" <= body[location + 1] <= "\udfff"
        )
    except IndexError:
        return False
