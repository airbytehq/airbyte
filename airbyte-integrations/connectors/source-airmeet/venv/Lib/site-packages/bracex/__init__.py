"""
A Bash like brace expander.

Licensed under MIT
Copyright (c) 2018 - 2020 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.
"""
from __future__ import annotations
import itertools
import math
import re
from typing import Iterator, Pattern, Match, Iterable, AnyStr
from . import __meta__


__all__ = ('expand', 'iexpand')

__version__ = __meta__.__version__
__version_info__ = __meta__.__version_info__

_alpha = [chr(x) if x != 0x5c else '' for x in range(ord('A'), ord('z') + 1)]
_nalpha = list(reversed(_alpha))

RE_INT_ITER = re.compile(r'(-?\d+)\.{2}(-?\d+)(?:\.{2}(-?\d+))?(?=\})')
RE_CHR_ITER = re.compile(r'([A-Za-z])\.{2}([A-Za-z])(?:\.{2}(-?\d+))?(?=\})')

DEFAULT_LIMIT = 1000


class ExpansionLimitException(Exception):
    """Brace expansion limit exception."""


def expand(string: AnyStr, keep_escapes: bool = False, limit: int = DEFAULT_LIMIT) -> list[AnyStr]:
    """Expand braces."""

    return list(iexpand(string, keep_escapes, limit))


def iexpand(string: AnyStr, keep_escapes: bool = False, limit: int = DEFAULT_LIMIT) -> Iterator[AnyStr]:
    """Expand braces and return an iterator."""

    if isinstance(string, bytes):
        for entry in ExpandBrace(keep_escapes, limit).expand(string.decode('latin-1')):
            yield entry.encode('latin-1')
    else:
        for entry in ExpandBrace(keep_escapes, limit).expand(string):
            yield entry


class StringIter:
    """Preprocess replace tokens."""

    def __init__(self, string: str) -> None:
        """Initialize."""

        self._string = string
        self._index = 0

    def __iter__(self) -> "StringIter":  # pragma: no cover
        """Iterate."""

        return self

    def __next__(self) -> str:
        """Python 3 iterator compatible next."""

        return self.iternext()

    def match(self, pattern: Pattern[str]) -> Match[str] | None:
        """Perform regex match at index."""

        m = pattern.match(self._string, self._index)
        if m:
            self._index = m.end()
        return m

    @property
    def index(self) -> int:
        """Get current index."""

        return self._index

    def previous(self) -> str:  # pragma: no cover
        """Get previous char."""

        return self._string[self._index - 1]

    def advance(self, count: int) -> None:
        """Advanced the index."""

        self._index += count

    def rewind(self, count: int) -> None:
        """Rewind index."""

        if count > self._index:  # pragma: no cover
            raise ValueError("Can't rewind past beginning!")

        self._index -= count

    def iternext(self) -> str:
        """Iterate through characters of the string."""

        try:
            char = self._string[self._index]
            self._index += 1
        except IndexError as e:  # pragma: no cover
            raise StopIteration from e

        return char


class ExpandBrace:
    """Expand braces like in Bash."""

    def __init__(self, keep_escapes: bool = False, limit: int = DEFAULT_LIMIT) -> None:
        """Initialize."""

        self.max_limit = limit
        self.count = 0
        self.expanding = False
        self.keep_escapes = keep_escapes

    def update_count_seq(self, count: list[int]) -> None:
        """Update the count from a list after evaluating a brace sequence and assert if count exceeds the max limit."""

        self.count -= sum(count)
        prod = 1
        for c in count:
            prod *= c
        self.update_count(prod)

    def update_count(self, count: int) -> None:
        """Update the count and assert if count exceeds the max limit."""

        self.count += count

        if self.max_limit > 0 and self.count > self.max_limit:
            raise ExpansionLimitException(
                f'Brace expansion has exceeded the limit of {self.max_limit:d}'
            )

    def set_expanding(self) -> bool:
        """Set that we are expanding a sequence, and return whether a release is required by the caller."""

        status = not self.expanding
        if status:
            self.expanding = True
        return status

    def is_expanding(self) -> bool:
        """Get status of whether we are expanding."""

        return self.expanding

    def release_expanding(self, release: bool) -> None:
        """Release the expand status."""

        if release:
            self.expanding = False

    def get_escape(self, c: str, i: StringIter) -> str:
        """Get an escape."""

        try:
            escaped = next(i)
        except StopIteration:
            escaped = ''
        return c + escaped if self.keep_escapes else escaped

    def squash(self, a: Iterable[str], b: Iterable[str]) -> Iterator[str]:
        """
        Returns a generator that squashes two iterables into one.

        ```
        ['this', 'that'], [[' and', ' or']] => ['this and', 'this or', 'that and', 'that or']
        ```
        """

        for x in itertools.product(a, b):
            yield ''.join(x) if isinstance(x, tuple) else x

    def get_literals(self, c: str, i: StringIter, depth: int) -> Iterator[str] | None:
        """
        Get a string literal.

        Gather all the literal chars up to opening curly or closing brace.
        Also gather chars between braces and commas within a group (is_expanding).
        """

        result = iter([''])
        is_dollar = False

        count = True
        seq_count = []

        try:
            while c:
                value = [c]  # type: Iterable[str]
                ignore_brace = is_dollar
                is_dollar = False

                if c == '$':
                    is_dollar = True

                elif c == '\\':
                    value = [self.get_escape(c, i)]

                elif not ignore_brace and c == '{':
                    # Try and get the group
                    index = i.index
                    try:
                        current_count = self.count
                        seq = self.get_sequence(next(i), i, depth + 1)
                        if seq:
                            if self.max_limit > 0:
                                diff = self.count - current_count
                                seq_count.append(diff)
                            count = False
                            value = seq
                    except StopIteration:
                        # Searched to end of string
                        # and still didn't find it.
                        i.rewind(i.index - index)

                elif self.is_expanding() and c in (',', '}'):
                    # We are Expanding within a group and found a group delimiter
                    # Return what we gathered before the group delimiters.
                    i.rewind(1)
                    if count:
                        self.update_count(1)
                    else:
                        self.update_count_seq(seq_count)
                    return result

                # Squash the current set of literals.
                result = self.squash(result, value)

                c = next(i)
        except StopIteration:
            if self.is_expanding():
                return None

        if count:
            self.update_count(1)
        else:
            self.update_count_seq(seq_count)
        return result

    def get_sequence(self, c: str, i: StringIter, depth: int) -> Iterator[str] | None:
        """
        Get the sequence.

        Get sequence between `{}`, such as: `{a,b}`, `{1..2[..inc]}`, etc.
        It will basically crawl to the end or find a valid series.
        """

        result = iter([])  # type: Iterator[str]
        release = self.set_expanding()
        has_comma = False  # Used to indicate validity of group (`{1..2}` are an exception).
        is_empty = True  # Tracks whether the current slot is empty `{slot,slot,slot}`.

        # Detect numerical and alphabetic series: `{1..2}` etc.
        i.rewind(1)
        item = self.get_range(i)
        i.advance(1)
        if item is not None:
            self.release_expanding(release)
            return item

        try:
            while True:
                # Bash has some special top level logic. if `}` follows `{` but hasn't matched
                # a group yet, keep going except when the first 2 bytes are `{}` which gets
                # completely ignored.
                keep_looking = depth == 1 and not has_comma  # and i.index not in self.skip_index
                if (c == '}' and (not keep_looking or i.index == 2)):
                    # If there is no comma, we know the sequence is bogus.
                    if is_empty:
                        result = itertools.chain(result, [''])
                    if not has_comma:
                        result = (''.join(['{', literal, '}']) for literal in result)
                    self.release_expanding(release)
                    return result

                elif c == ',':
                    # Must be the first element in the list.
                    has_comma = True
                    if is_empty:
                        result = itertools.chain(result, [''])
                    else:
                        is_empty = True

                else:
                    if c == '}':
                        # Top level: If we didn't find a comma, we haven't
                        # completed the top level group. Request more and
                        # append to what we already have for the first slot.
                        if is_empty and not has_comma:
                            result = itertools.chain(result, [c])
                        else:
                            result = self.squash(result, [c])
                        value = self.get_literals(next(i), i, depth)
                        if value is not None:
                            result = self.squash(result, value)
                            is_empty = False
                    else:
                        # Lower level: Try to find group, but give up if cannot acquire.
                        value = self.get_literals(c, i, depth)
                        if value is not None:
                            result = itertools.chain(result, value)
                            is_empty = False

                c = next(i)

        except StopIteration:
            self.release_expanding(release)
            raise

    def get_range(self, i: StringIter) -> Iterator[str] | None:
        """
        Check and retrieve range if value is a valid range.

        Here we are looking to see if the value is series or range.
        We look for `{1..2[..inc]}` or `{a..z[..inc]}` (negative numbers are fine).
        """

        try:
            m = i.match(RE_INT_ITER)
            if m:
                return self.get_int_range(*m.groups())

            m = i.match(RE_CHR_ITER)
            if m:
                return self.get_char_range(*m.groups())
        except ExpansionLimitException:
            raise
        except Exception:  # pragma: no cover
            # TODO: We really should never fail here,
            # but if we do, assume the sequence range
            # was invalid. This catch can probably
            # be removed in the future with more testing.
            pass

        return None

    def format_values(self, values: Iterable[int], padding: int) -> Iterator[str]:
        """Get padding adjusting for negative values."""

        for value in values:
            yield "{:0{pad}d}".format(value, pad=padding) if padding else str(value)

    def get_int_range(self, start: str, end: str, increment: str | None = None) -> Iterator[str]:
        """Get an integer range between start and end and increments of increment."""

        first, last = int(start), int(end)
        inc = int(increment) if increment is not None else 1
        max_length = max(len(start), len(end))

        # Zero doesn't make sense as an incrementer
        # but like bash, just assume one
        if inc == 0:
            inc = 1

        if start[0] == '-':
            start = start[1:]

        if end[0] == '-':
            end = end[1:]

        if (len(start) > 1 and start[0] == '0') or (len(end) > 1 and end[0] == '0'):
            padding = max_length

        else:
            padding = 0

        if first < last:
            self.update_count(math.ceil(abs(((last + 1) - first) / inc)))
            r = range(first, last + 1, -inc if inc < 0 else inc)
        else:
            self.update_count(math.ceil(abs(((first + 1) - last) / inc)))
            r = range(first, last - 1, inc if inc < 0 else -inc)

        return self.format_values(r, padding)

    def get_char_range(self, start: str, end: str, increment: str | None = None) -> Iterator[str]:
        """Get a range of alphabetic characters."""

        inc = int(increment) if increment else 1
        if inc < 0:
            inc = -inc

        # Zero doesn't make sense as an incrementer
        # but like bash, just assume one
        if inc == 0:
            inc = 1

        inverse = start > end
        alpha = _nalpha if inverse else _alpha

        first = alpha.index(start)
        last = alpha.index(end)

        if first < last:
            self.update_count(math.ceil(((last + 1) - first) / inc))
            return itertools.islice(alpha, first, last + 1, inc)

        else:
            self.update_count(math.ceil(((first + 1) - last) / inc))
            return itertools.islice(alpha, last, first + 1, inc)

    def expand(self, string: str) -> Iterator[str]:
        """Expand."""

        self.expanding = False
        empties = []
        found_literal = False
        if string:
            i = StringIter(string)
            value = self.get_literals(next(i), i, 0)
            if value is not None:
                for x in value:
                    # We don't want to return trailing empty strings.
                    # Store empty strings and output only when followed by a literal.
                    if not x:
                        empties.append(x)
                        continue
                    found_literal = True
                    while empties:
                        yield empties.pop(0)
                    yield x
        empties = []

        # We found no literals so return an empty string
        if not found_literal:
            yield ""
