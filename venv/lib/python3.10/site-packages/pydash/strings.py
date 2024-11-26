"""
String functions.

.. versionadded:: 1.1.0
"""

import html
import math
import re
import typing
import typing as t
import unicodedata
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import pydash as pyd

from .helpers import UNSET, Unset
from .types import NumberT


__all__ = (
    "camel_case",
    "capitalize",
    "chop",
    "chop_right",
    "chars",
    "clean",
    "count_substr",
    "deburr",
    "decapitalize",
    "ends_with",
    "ensure_ends_with",
    "ensure_starts_with",
    "escape",
    "escape_reg_exp",
    "has_substr",
    "human_case",
    "insert_substr",
    "join",
    "kebab_case",
    "lines",
    "lower_case",
    "lower_first",
    "number_format",
    "pad",
    "pad_end",
    "pad_start",
    "pascal_case",
    "predecessor",
    "prune",
    "quote",
    "reg_exp_js_match",
    "reg_exp_js_replace",
    "reg_exp_replace",
    "repeat",
    "replace",
    "replace_end",
    "replace_start",
    "separator_case",
    "series_phrase",
    "series_phrase_serial",
    "slugify",
    "snake_case",
    "split",
    "start_case",
    "starts_with",
    "strip_tags",
    "substr_left",
    "substr_left_end",
    "substr_right",
    "substr_right_end",
    "successor",
    "surround",
    "swap_case",
    "title_case",
    "to_lower",
    "to_upper",
    "trim",
    "trim_end",
    "trim_start",
    "truncate",
    "unescape",
    "unquote",
    "upper_case",
    "upper_first",
    "url",
    "words",
)

T = t.TypeVar("T")
T2 = t.TypeVar("T2")


class JSRegExp:
    """
    Javascript-style regular expression pattern.

    Converts a Javascript-style regular expression to the equivalent Python version.
    """

    def __init__(self, reg_exp: str) -> None:
        pattern, options = reg_exp[1:].rsplit("/", 1)

        self._global = "g" in options
        self._ignore_case = "i" in options

        flags = re.I if self._ignore_case else 0
        self.pattern = re.compile(pattern, flags=flags)

    def find(self, text: str) -> t.List[str]:
        """Return list of regular expression matches."""
        if self._global:
            results = self.pattern.findall(text)
        else:
            res = self.pattern.search(text)
            if res:
                results = [res.group()]
            else:
                results = []
        return results

    def replace(self, text: str, repl: t.Union[str, t.Callable[[re.Match], str]]) -> str:
        """Replace parts of text that match the regular expression."""
        count = 0 if self._global else 1
        return self.pattern.sub(repl, text, count=count)


HTML_ESCAPES = {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;", "`": "&#96;"}

DEBURRED_LETTERS = {
    "\xC0": "A",
    "\xC1": "A",
    "\xC2": "A",
    "\xC3": "A",
    "\xC4": "A",
    "\xC5": "A",
    "\xE0": "a",
    "\xE1": "a",
    "\xE2": "a",
    "\xE3": "a",
    "\xE4": "a",
    "\xE5": "a",
    "\xC7": "C",
    "\xE7": "c",
    "\xD0": "D",
    "\xF0": "d",
    "\xC8": "E",
    "\xC9": "E",
    "\xCA": "E",
    "\xCB": "E",
    "\xE8": "e",
    "\xE9": "e",
    "\xEA": "e",
    "\xEB": "e",
    "\xCC": "I",
    "\xCD": "I",
    "\xCE": "I",
    "\xCF": "I",
    "\xEC": "i",
    "\xED": "i",
    "\xEE": "i",
    "\xEF": "i",
    "\xD1": "N",
    "\xF1": "n",
    "\xD2": "O",
    "\xD3": "O",
    "\xD4": "O",
    "\xD5": "O",
    "\xD6": "O",
    "\xD8": "O",
    "\xF2": "o",
    "\xF3": "o",
    "\xF4": "o",
    "\xF5": "o",
    "\xF6": "o",
    "\xF8": "o",
    "\xD9": "U",
    "\xDA": "U",
    "\xDB": "U",
    "\xDC": "U",
    "\xF9": "u",
    "\xFA": "u",
    "\xFB": "u",
    "\xFC": "u",
    "\xDD": "Y",
    "\xFD": "y",
    "\xFF": "y",
    "\xC6": "Ae",
    "\xE6": "ae",
    "\xDE": "Th",
    "\xFE": "th",
    "\xDF": "ss",
    "\xD7": " ",
    "\xF7": " ",
}

# Use Javascript style regex to make Lo-Dash compatibility easier.
# Lodash Regex definitions: https://github.com/lodash/lodash/blob/master/.internal/unicodeWords.js

# References: https://github.com/lodash/lodash/blob/master/words.js#L8
RS_ASCII_WORDS = "/[^\x00-\x2f\x3a-\x40\x5b-\x60\x7b-\x7f]+/g"
RS_LATIN1 = "/[\xC0-\xFF]/g"

# Used to compose unicode character classes.
RS_ASTRAL_RANGE = "\\ud800-\\udfff"
RS_COMBO_MARKS_RANGE = "\\u0300-\\u036f"
RE_COMBO_HALF_MARKS_RANGE = "\\ufe20-\\ufe2f"
RS_COMBO_SYMBOLS_RANGE = "\\u20d0-\\u20ff"
RS_COMBO_MARKS_EXTENDED_RANGE = "\\u1ab0-\\u1aff"
RS_COMBO_MARKS_SUPPLEMENT_RANGE = "\\u1dc0-\\u1dff"
RS_COMBO_RANGE = (
    RS_COMBO_MARKS_RANGE
    + RE_COMBO_HALF_MARKS_RANGE
    + RS_COMBO_SYMBOLS_RANGE
    + RS_COMBO_MARKS_EXTENDED_RANGE
    + RS_COMBO_MARKS_SUPPLEMENT_RANGE
)
RS_DINGBAT_RANGE = "\\u2700-\\u27bf"
RS_LOWER_RANGE = "a-z\\xdf-\\xf6\\xf8-\\xff"
RS_MATH_OP_RANGE = "\\xac\\xb1\\xd7\\xf7"
RS_NON_CHAR_RANGE = "\\x00-\\x2f\\x3a-\\x40\\x5b-\\x60\\x7b-\\xbf"
RS_PUNCTUATION_RANGE = "\\u2000-\\u206f"
RS_SPACE_RANGE = (
    " \\t\\x0b\\f\\xa0\\ufeff\\n\\r\\u2028\\u2029\\"
    "u1680\\u180e\\u2000\\u2001\\u2002\\u2003\\u2004\\u2005\\u2006\\"
    "u2007\\u2008\\u2009\\u200a\\u202f\\u205f\\u3000"
)
RS_UPPER_RANGE = "A-Z\\xc0-\\xd6\\xd8-\\xde"
RS_VAR_RANGE = "\\ufe0e\\ufe0f"
RS_BREAK_RANGE = RS_MATH_OP_RANGE + RS_NON_CHAR_RANGE + RS_PUNCTUATION_RANGE + RS_SPACE_RANGE

# Used to compose unicode capture groups.
RS_APOS = "['\u2019]"
RS_BREAK = f"[{RS_BREAK_RANGE}]"
RS_COMBO = f"[{RS_COMBO_RANGE}]"
RS_DIGIT = "\\d"
RS_DINGBAT = f"[{RS_DINGBAT_RANGE}]"
RS_LOWER = f"[{RS_LOWER_RANGE}]"
RS_MISC = (
    f"[^{RS_ASTRAL_RANGE}{RS_BREAK_RANGE}{RS_DIGIT}"
    f"{RS_DINGBAT_RANGE}{RS_LOWER_RANGE}{RS_UPPER_RANGE}]"
)
RS_FITZ = "\\ud83c[\\udffb-\\udfff]"
RS_MODIFIER = f"(?:{RS_COMBO}|{RS_FITZ})"
RS_NON_ASTRAL = f"[^{RS_ASTRAL_RANGE}]"
RS_REGIONAL = "(?:\\ud83c[\\udde6-\\uddff]){2}"
RS_SURR_PAIR = "[\\ud800-\\udbff][\\udc00-\\udfff]"
RS_UPPER = f"[{RS_UPPER_RANGE}]"
RS_ZWJ = "\\u200d"

# Used to compose unicode regexes.
RS_MISC_LOWER = f"(?:{RS_LOWER}|{RS_MISC})"
RS_MISC_UPPER = f"(?:{RS_UPPER}|{RS_MISC})"
RS_OPT_CONTR_LOWER = f"(?:{RS_APOS}(?:d|ll|m|re|s|t|ve))?"
RS_OPT_CONTR_UPPER = f"(?:{RS_APOS}(?:D|LL|M|RE|S|T|VE))?"
RE_OPT_MOD = f"{RS_MODIFIER}?"
RS_OPT_VAR = f"[{RS_VAR_RANGE}]?"
RS_OPT_JOIN = (
    f"(?:{RS_ZWJ}(?:{RS_NON_ASTRAL}|{RS_REGIONAL}|{RS_SURR_PAIR}){RS_OPT_VAR}{RE_OPT_MOD})*"
)
RS_ORD_LOWER = "\\d*(?:1st|2nd|3rd|(?![123])\\dth)(?=\\b|[A-Z_])"
RS_ORD_UPPER = "\\d*(?:1ST|2ND|3RD|(?![123])\\dTH)(?=\\b|[a-z_])"
RS_SEQ = RS_OPT_VAR + RE_OPT_MOD + RS_OPT_JOIN
RS_EMOJI = f"(?:{RS_DINGBAT}|{RS_REGIONAL}|{RS_SURR_PAIR}){RS_SEQ}"

RS_HAS_UNICODE_WORD = "[a-z][A-Z]|[A-Z]{2}[a-z]|[0-9][a-zA-Z]|[a-zA-Z][0-9]|[^a-zA-Z0-9 ]"
RS_UNICODE_WORDS = (
    f"/"
    f"{RS_UPPER}?{RS_LOWER}+{RS_OPT_CONTR_LOWER}(?={RS_BREAK}|{RS_UPPER}|$)"
    f"|{RS_MISC_UPPER}+{RS_OPT_CONTR_UPPER}(?={RS_BREAK}|{RS_UPPER}{RS_MISC_LOWER}|$)"
    f"|{RS_UPPER}?{RS_MISC_LOWER}+{RS_OPT_CONTR_LOWER}"
    f"|{RS_UPPER}+{RS_OPT_CONTR_UPPER}"
    f"|{RS_ORD_UPPER}"
    f"|{RS_ORD_LOWER}"
    f"|{RS_DIGIT}+"
    f"|{RS_EMOJI}"
    f"/g"
)

# Compiled regexes for use in functions.
JS_RE_ASCII_WORDS = JSRegExp(RS_ASCII_WORDS)
JS_RE_UNICODE_WORDS = JSRegExp(RS_UNICODE_WORDS)
JS_RE_LATIN1 = JSRegExp(RS_LATIN1)
RE_HAS_UNICODE_WORD = re.compile(RS_HAS_UNICODE_WORD)
RE_APOS = re.compile(RS_APOS)
RE_HTML_TAGS = re.compile(r"<\/?[^>]+>")


def camel_case(text: t.Any) -> str:
    """
    Converts `text` to camel case.

    Args:
        text: String to convert.

    Returns:
        String converted to camel case.

    Example:

        >>> camel_case('FOO BAR_bAz')
        'fooBarBAz'

    .. versionadded:: 1.1.0

    .. versionchanged:: 5.0.0
        Improved unicode word support.
    """
    text = "".join(word.title() for word in compounder(text))
    return text[:1].lower() + text[1:]


def capitalize(text: t.Any, strict: bool = True) -> str:
    """
    Capitalizes the first character of `text`.

    Args:
        text: String to capitalize.
        strict: Whether to cast rest of string to lower case. Defaults to ``True``.

    Returns:
        Capitalized string.

    Example:

        >>> capitalize('once upon a TIME')
        'Once upon a time'
        >>> capitalize('once upon a TIME', False)
        'Once upon a TIME'

    .. versionadded:: 1.1.0

    .. versionchanged:: 3.0.0
        Added `strict` option.
    """
    text = pyd.to_string(text)
    return text.capitalize() if strict else text[:1].upper() + text[1:]


def chars(text: t.Any) -> t.List[str]:
    """
    Split `text` into a list of single characters.

    Args:
        text: String to split up.

    Returns:
        List of individual characters.

    Example:

        >>> chars('onetwo')
        ['o', 'n', 'e', 't', 'w', 'o']

    .. versionadded:: 3.0.0
    """
    return list(pyd.to_string(text))


def chop(text: t.Any, step: int) -> t.List[str]:
    """
    Break up `text` into intervals of length `step`.

    Args:
        text: String to chop.
        step: Interval to chop `text`.

    Returns:
        List of chopped characters. If `text` is `None` an empty list is returned.

    Example:

        >>> chop('abcdefg', 3)
        ['abc', 'def', 'g']

    .. versionadded:: 3.0.0
    """
    if text is None:
        return []

    text = pyd.to_string(text)

    if step <= 0:
        chopped = [text]
    else:
        chopped = [text[i : i + step] for i in range(0, len(text), step)]

    return chopped


def chop_right(text: t.Any, step: int) -> t.List[str]:
    """
    Like :func:`chop` except `text` is chopped from right.

    Args:
        text: String to chop.
        step: Interval to chop `text`.

    Returns:
        List of chopped characters.

    Example:

        >>> chop_right('abcdefg', 3)
        ['a', 'bcd', 'efg']

    .. versionadded:: 3.0.0
    """
    if text is None:
        return []

    text = pyd.to_string(text)

    if step <= 0:
        chopped = [text]
    else:
        text_len = len(text)
        chopped = [text[-(i + step) : text_len - i] for i in range(0, text_len, step)][::-1]

    return chopped


def clean(text: t.Any) -> str:
    """
    Trim and replace multiple spaces with a single space.

    Args:
        text: String to clean.

    Returns:
        Cleaned string.

    Example:

        >>> clean('a  b   c    d')
        'a b c d'

    .. versionadded:: 3.0.0
    """
    text = pyd.to_string(text)
    return " ".join(pyd.compact(text.split()))


def count_substr(text: t.Any, subtext: t.Any) -> int:
    """
    Count the occurrences of `subtext` in `text`.

    Args:
        text: Source string to count from.
        subtext: String to count.

    Returns:
        Number of occurrences of `subtext` in `text`.

    Example:

        >>> count_substr('aabbccddaabbccdd', 'bc')
        2

    .. versionadded:: 3.0.0
    """
    if text is None or subtext is None:
        return 0

    text = pyd.to_string(text)
    subtext = pyd.to_string(subtext)

    return text.count(subtext)


def deburr(text: t.Any) -> str:
    """
    Deburrs `text` by converting latin-1 supplementary letters to basic latin letters.

    Args:
        text: String to deburr.

    Returns:
        Deburred string.

    Example:

        >>> deburr('déjà vu')
        '...
        >>> 'deja vu'
        'deja vu'

    .. versionadded:: 2.0.0
    """
    text = pyd.to_string(text)
    return JS_RE_LATIN1.replace(
        text, lambda match: DEBURRED_LETTERS.get(match.group(), match.group())
    )


def decapitalize(text: t.Any) -> str:
    """
    Decaptitalizes the first character of `text`.

    Args:
        text: String to decapitalize.

    Returns:
        Decapitalized string.

    Example:

        >>> decapitalize('FOO BAR')
        'fOO BAR'

    .. versionadded:: 3.0.0
    """
    text = pyd.to_string(text)
    return text[:1].lower() + text[1:]


def ends_with(text: t.Any, target: t.Any, position: t.Union[int, None] = None) -> bool:
    """
    Checks if `text` ends with a given target string.

    Args:
        text: String to check.
        target: String to check for.
        position: Position to search from. Defaults to end of `text`.

    Returns:
        Whether `text` ends with `target`.

    Example:

        >>> ends_with('abc def', 'def')
        True
        >>> ends_with('abc def', 4)
        False

    .. versionadded:: 1.1.0
    """
    target = pyd.to_string(target)
    text = pyd.to_string(text)

    if position is None:
        position = len(text)

    return text[:position].endswith(target)


def ensure_ends_with(text: t.Any, suffix: t.Any) -> str:
    """
    Append a given suffix to a string, but only if the source string does not end with that suffix.

    Args:
        text: Source string to append `suffix` to.
        suffix: String to append to the source string if the source string does not end with
            `suffix`.

    Returns:
        source string possibly extended by `suffix`.

    Example:

        >>> ensure_ends_with('foo bar', '!')
        'foo bar!'
        >>> ensure_ends_with('foo bar!', '!')
        'foo bar!'

    .. versionadded:: 2.4.0
    """
    text = pyd.to_string(text)
    suffix = pyd.to_string(suffix)
    if text.endswith(suffix):
        return text
    return f"{text}{suffix}"


def ensure_starts_with(text: t.Any, prefix: t.Any) -> str:
    """
    Prepend a given prefix to a string, but only if the source string does not start with that
    prefix.

    Args:
        text: Source string to prepend `prefix` to.
        prefix: String to prepend to the source string if the source string does not start
            with `prefix`.

    Returns:
        source string possibly prefixed by `prefix`

    Example:

        >>> ensure_starts_with('foo bar', 'Oh my! ')
        'Oh my! foo bar'
        >>> ensure_starts_with('Oh my! foo bar', 'Oh my! ')
        'Oh my! foo bar'

    .. versionadded:: 2.4.0
    """
    text = pyd.to_string(text)
    prefix = pyd.to_string(prefix)
    if text.startswith(prefix):
        return text
    return f"{prefix}{text}"


def escape(text: t.Any) -> str:
    r"""
    Converts the characters ``&``, ``<``, ``>``, ``"``, ``'``, and ``\``` in `text` to their
    corresponding HTML entities.

    Args:
        text: String to escape.

    Returns:
        HTML escaped string.

    Example:

        >>> escape('"1 > 2 && 3 < 4"')
        '&quot;1 &gt; 2 &amp;&amp; 3 &lt; 4&quot;'

    .. versionadded:: 1.0.0

    .. versionchanged:: 1.1.0
        Moved function to :mod:`pydash.strings`.
    """
    text = pyd.to_string(text)
    # NOTE: Not using html.escape because Lo-Dash escapes certain chars differently (e.g. `'` isn't
    # escaped by html.escape() but is by Lo-Dash).
    return "".join(HTML_ESCAPES.get(char, char) for char in text)


def escape_reg_exp(text: t.Any) -> str:
    """
    Escapes the RegExp special characters in `text`.

    Args:
        text: String to escape.

    Returns:
        RegExp escaped string.

    Example:

        >>> escape_reg_exp('[()]')
        '\\\\[\\\\(\\\\)\\\\]'

    .. versionadded:: 1.1.0

    .. versionchanged:: 4.0.0
        Removed alias ``escape_re``
    """
    text = pyd.to_string(text)
    return re.escape(text)


def has_substr(text: t.Any, subtext: t.Any) -> bool:
    """
    Returns whether `subtext` is included in `text`.

    Args:
        text: String to search.
        subtext: String to search for.

    Returns:
        Whether `subtext` is found in `text`.

    Example:

        >>> has_substr('abcdef', 'bc')
        True
        >>> has_substr('abcdef', 'bb')
        False

    .. versionadded:: 3.0.0
    """
    text = pyd.to_string(text)
    subtext = pyd.to_string(subtext)
    return text.find(subtext) >= 0


def human_case(text: t.Any) -> str:
    """
    Converts `text` to human case which has only the first letter capitalized and each word
    separated by a space.

    Args:
        text: String to convert.

    Returns:
        String converted to human case.

    Example:

        >>> human_case('abc-def_hij lmn')
        'Abc def hij lmn'
        >>> human_case('user_id')
        'User'

    .. versionadded:: 3.0.0

    .. versionchanged:: 5.0.0
        Improved unicode word support.
    """
    return (
        pyd.chain(text)
        .snake_case()
        .reg_exp_replace("_id$", "")
        .replace("_", " ")
        .capitalize()
        .value()
    )


def insert_substr(text: t.Any, index: int, subtext: t.Any) -> str:
    """
    Insert `subtext` in `text` starting at position `index`.

    Args:
        text: String to add substring to.
        index: String index to insert into.
        subtext: String to insert.

    Returns:
        Modified string.

    Example:

        >>> insert_substr('abcdef', 3, '--')
        'abc--def'

    .. versionadded:: 3.0.0
    """
    text = pyd.to_string(text)
    subtext = pyd.to_string(subtext)
    return text[:index] + subtext + text[index:]


def join(array: t.Iterable[t.Any], separator: t.Any = "") -> str:
    """
    Joins an iterable into a string using `separator` between each element.

    Args:
        array: Iterable to implode.
        separator: Separator to using when joining. Defaults to ``''``.

    Returns:
        Joined string.

    Example:

        >>> join(['a', 'b', 'c']) == 'abc'
        True
        >>> join([1, 2, 3, 4], '&') == '1&2&3&4'
        True
        >>> join('abcdef', '-') == 'a-b-c-d-e-f'
        True

    .. versionadded:: 2.0.0

    .. versionchanged:: 4.0.0
        Removed alias ``implode``.
    """
    return pyd.to_string(separator).join(pyd.map_(array or (), pyd.to_string))


def kebab_case(text: t.Any) -> str:
    """
    Converts `text` to kebab case (a.k.a. spinal case).

    Args:
        text: String to convert.

    Returns:
        String converted to kebab case.

    Example:

        >>> kebab_case('a b c_d-e!f')
        'a-b-c-d-e-f'

    .. versionadded:: 1.1.0

    .. versionchanged:: 5.0.0
        Improved unicode word support.
    """
    return "-".join(word.lower() for word in compounder(text) if word)


def lines(text: t.Any) -> t.List[str]:
    r"""
    Split lines in `text` into an array.

    Args:
        text: String to split.

    Returns:
        String split by lines.

    Example:

        >>> lines('a\nb\r\nc')
        ['a', 'b', 'c']

    .. versionadded:: 3.0.0
    """
    text = pyd.to_string(text)
    return text.splitlines()


def lower_case(text: t.Any) -> str:
    """
    Converts string to lower case as space separated words.

    Args:
        text: String to convert.

    Returns:
        String converted to lower case as space separated words.

    Example:

        >>> lower_case('fooBar')
        'foo bar'
        >>> lower_case('--foo-Bar--')
        'foo bar'
        >>> lower_case('/?*Foo10/;"B*Ar')
        'foo 10 b ar'

    .. versionadded:: 4.0.0

    .. versionchanged:: 5.0.0
        Improved unicode word support.
    """
    return " ".join(compounder(text)).lower()


def lower_first(text: str) -> str:
    """
    Converts the first character of string to lower case.

    Args:
        text: String passed in by the user.

    Returns:
        String in which the first character is converted to lower case.

    Example:

        >>> lower_first('FRED')
        'fRED'
        >>> lower_first('Foo Bar')
        'foo Bar'
        >>> lower_first('1foobar')
        '1foobar'
        >>> lower_first(';foobar')
        ';foobar'

    .. versionadded:: 4.0.0
    """
    return text[:1].lower() + text[1:]


def number_format(
    number: NumberT, scale: int = 0, decimal_separator: str = ".", order_separator: str = ","
) -> str:
    """
    Format a number to scale with custom decimal and order separators.

    Args:
        number: Number to format.
        scale: Number of decimals to include. Defaults to ``0``.
        decimal_separator: Decimal separator to use. Defaults to ``'.'``.
        order_separator: Order separator to use. Defaults to ``','``.

    Returns:
        Number formatted as string.

    Example:

        >>> number_format(1234.5678)
        '1,235'
        >>> number_format(1234.5678, 2, ',', '.')
        '1.234,57'

    .. versionadded:: 3.0.0
    """
    # Create a string formatter which converts number to the appropriately scaled representation.
    fmt = f"{{0:.{scale:d}f}}"

    try:
        num_parts = fmt.format(number).split(".")
    except ValueError:
        text = ""
    else:
        int_part = num_parts[0]
        dec_part = (num_parts + [""])[1]

        # Reverse the integer part, chop it into groups of 3, join on `order_separator`, and then
        # un-reverse the string.
        int_part = order_separator.join(chop(int_part[::-1], 3))[::-1]

        text = decimal_separator.join(pyd.compact([int_part, dec_part]))

    return text


def pad(text: t.Any, length: int, chars: t.Any = " ") -> str:
    """
    Pads `text` on the left and right sides if it is shorter than the given padding length. The
    `chars` string may be truncated if the number of padding characters can't be evenly divided by
    the padding length.

    Args:
        text: String to pad.
        length: Amount to pad.
        chars: Characters to pad with. Defaults to ``" "``.

    Returns:
        Padded string.

    Example:

        >>> pad('abc', 5)
        ' abc '
        >>> pad('abc', 6, 'x')
        'xabcxx'
        >>> pad('abc', 5, '...')
        '.abc.'

    .. versionadded:: 1.1.0

    .. versionchanged:: 3.0.0
        Fix handling of multiple `chars` so that padded string isn't over padded.
    """
    # pylint: disable=redefined-outer-name
    text = pyd.to_string(text)
    text_len = len(text)

    if text_len >= length:
        return text

    mid = (length - text_len) / 2.0
    left_len = int(math.floor(mid))
    right_len = int(math.ceil(mid))
    chars = pad_end("", right_len, chars)

    return chars[:left_len] + text + chars


def pad_end(text: t.Any, length: int, chars: t.Any = " ") -> str:
    """
    Pads `text` on the right side if it is shorter than the given padding length. The `chars` string
    may be truncated if the number of padding characters can't be evenly divided by the padding
    length.

    Args:
        text: String to pad.
        length: Amount to pad.
        chars: Characters to pad with. Defaults to ``" "``.

    Returns:
        Padded string.

    Example:

        >>> pad_end('abc', 5)
        'abc  '
        >>> pad_end('abc', 5, '.')
        'abc..'

    .. versionadded:: 1.1.0

    .. versionchanged:: 4.0.0
        Renamed from ``pad_right`` to ``pad_end``.
    """
    # pylint: disable=redefined-outer-name
    text = pyd.to_string(text)
    length = max((length, len(text)))
    return (text + repeat(chars, length))[:length]


def pad_start(text: t.Any, length: int, chars: t.Any = " ") -> str:
    """
    Pads `text` on the left side if it is shorter than the given padding length. The `chars` string
    may be truncated if the number of padding characters can't be evenly divided by the padding
    length.

    Args:
        text: String to pad.
        length: Amount to pad.
        chars: Characters to pad with. Defaults to ``" "``.

    Returns:
        Padded string.

    Example:

        >>> pad_start('abc', 5)
        '  abc'
        >>> pad_start('abc', 5, '.')
        '..abc'

    .. versionadded:: 1.1.0

    .. versionchanged:: 4.0.0
        Renamed from ``pad_left`` to ``pad_start``.
    """
    # pylint: disable=redefined-outer-name
    text = pyd.to_string(text)
    length = max(length, len(text))
    return (repeat(chars, length) + text)[-length:]


def pascal_case(text: t.Any, strict: bool = True) -> str:
    """
    Like :func:`camel_case` except the first letter is capitalized.

    Args:
        text: String to convert.
        strict: Whether to cast rest of string to lower case. Defaults to ``True``.

    Returns:
        String converted to class case.

    Example:

        >>> pascal_case('FOO BAR_bAz')
        'FooBarBaz'
        >>> pascal_case('FOO BAR_bAz', False)
        'FooBarBAz'

    .. versionadded:: 3.0.0

    .. versionchanged:: 5.0.0
        Improved unicode word support.
    """
    text = pyd.to_string(text)

    if strict:
        text = text.lower()

    return capitalize(camel_case(text), strict=False)


def predecessor(char: t.Any) -> str:
    """
    Return the predecessor character of `char`.

    Args:
        char: Character to find the predecessor of.

    Returns:
        Predecessor character.

    Example:

        >>> predecessor('c')
        'b'
        >>> predecessor('C')
        'B'
        >>> predecessor('3')
        '2'

    .. versionadded:: 3.0.0
    """
    char = pyd.to_string(char)
    return chr(ord(char) - 1)


def prune(text: t.Any, length: int = 0, omission: str = "...") -> str:
    """
    Like :func:`truncate` except it ensures that the pruned string doesn't exceed the original
    length, i.e., it avoids half-chopped words when truncating. If the pruned text + `omission` text
    is longer than the original text, then the original text is returned.

    Args:
        text: String to prune.
        length: Target prune length. Defaults to ``0``.
        omission: Omission text to append to the end of the pruned string. Defaults
            to ``'...'``.

    Returns:
        Pruned string.

    Example:

        >>> prune('Fe fi fo fum', 5)
        'Fe fi...'
        >>> prune('Fe fi fo fum', 6)
        'Fe fi...'
        >>> prune('Fe fi fo fum', 7)
        'Fe fi...'
        >>> prune('Fe fi fo fum', 8, ',,,')
        'Fe fi fo,,,'

    .. versionadded:: 3.0.0
    """
    text = pyd.to_string(text)
    text_len = len(text)
    omission_len = len(omission)

    if text_len <= length:
        return text

    # Replace non-alphanumeric chars with whitespace.
    def repl(match):
        char = match.group(0)
        return " " if char.upper() == char.lower() else char

    subtext = reg_exp_replace(text[: length + 1], r".(?=\W*\w*$)", repl)

    if re.match(r"\w\w", subtext[-2:]):
        # Last two characters are alphanumeric. Remove last "word" from end of string so that we
        # prune to the next whole word.
        subtext = reg_exp_replace(subtext, r"\s*\S+$", "")
    else:
        # Last character (at least) is whitespace. So remove that character as well as any other
        # whitespace.
        subtext = subtext[:-1].rstrip()

    subtext_len = len(subtext)

    # Only add omission text if doing so will result in a string that is equal to or smaller than
    # the original.
    if (subtext_len + omission_len) <= text_len:
        text = text[:subtext_len] + omission

    return text


def quote(text: t.Any, quote_char: t.Any = '"') -> str:
    """
    Quote a string with another string.

    Args:
        text: String to be quoted.
        quote_char: the quote character. Defaults to ``'"'``.

    Returns:
        the quoted string.

    Example:

        >>> quote('To be or not to be')
        '"To be or not to be"'
        >>> quote('To be or not to be', "'")
        "'To be or not to be'"

    .. versionadded:: 2.4.0
    """
    return surround(text, quote_char)


def reg_exp_js_match(text: t.Any, reg_exp: str) -> t.List[str]:
    """
    Return list of matches using Javascript style regular expression.

    Args:
        text: String to evaluate.
        reg_exp: Javascript style regular expression.

    Returns:
        List of matches.

    Example:

        >>> reg_exp_js_match('aaBBcc', '/bb/')
        []
        >>> reg_exp_js_match('aaBBcc', '/bb/i')
        ['BB']
        >>> reg_exp_js_match('aaBBccbb', '/bb/i')
        ['BB']
        >>> reg_exp_js_match('aaBBccbb', '/bb/gi')
        ['BB', 'bb']

    .. versionadded:: 2.0.0

    .. versionchanged:: 3.0.0
        Reordered arguments to make `text` first.

    .. versionchanged:: 4.0.0
        Renamed from ``js_match`` to ``reg_exp_js_match``.
    """
    text = pyd.to_string(text)
    return JSRegExp(reg_exp).find(text)


def reg_exp_js_replace(
    text: t.Any, reg_exp: str, repl: t.Union[str, t.Callable[[re.Match], str]]
) -> str:
    """
    Replace `text` with `repl` using Javascript style regular expression to find matches.

    Args:
        text: String to evaluate.
        reg_exp: Javascript style regular expression.
        repl: Replacement string or callable.

    Returns:
        Modified string.

    Example:

        >>> reg_exp_js_replace('aaBBcc', '/bb/', 'X')
        'aaBBcc'
        >>> reg_exp_js_replace('aaBBcc', '/bb/i', 'X')
        'aaXcc'
        >>> reg_exp_js_replace('aaBBccbb', '/bb/i', 'X')
        'aaXccbb'
        >>> reg_exp_js_replace('aaBBccbb', '/bb/gi', 'X')
        'aaXccX'

    .. versionadded:: 2.0.0

    .. versionchanged:: 3.0.0
        Reordered arguments to make `text` first.

    .. versionchanged:: 4.0.0
        Renamed from ``js_replace`` to ``reg_exp_js_replace``.
    """
    text = pyd.to_string(text)
    if not pyd.is_function(repl):
        repl = pyd.to_string(repl)
    return JSRegExp(reg_exp).replace(text, repl)


def reg_exp_replace(
    text: t.Any,
    pattern: t.Any,
    repl: t.Union[str, t.Callable[[re.Match], str]],
    ignore_case: bool = False,
    count: int = 0,
) -> str:
    """
    Replace occurrences of regex `pattern` with `repl` in `text`. Optionally, ignore case when
    replacing. Optionally, set `count` to limit number of replacements.

    Args:
        text: String to replace.
        pattern: Pattern to find and replace.
        repl: String to substitute `pattern` with.
        ignore_case: Whether to ignore case when replacing. Defaults to ``False``.
        count: Maximum number of occurrences to replace. Defaults to ``0`` which
            replaces all.

    Returns:
        Replaced string.

    Example:

        >>> reg_exp_replace('aabbcc', 'b', 'X')
        'aaXXcc'
        >>> reg_exp_replace('aabbcc', 'B', 'X', ignore_case=True)
        'aaXXcc'
        >>> reg_exp_replace('aabbcc', 'b', 'X', count=1)
        'aaXbcc'
        >>> reg_exp_replace('aabbcc', '[ab]', 'X')
        'XXXXcc'

    .. versionadded:: 3.0.0

    .. versionchanged:: 4.0.0
        Renamed from ``re_replace`` to ``reg_exp_replace``.
    """
    if pattern is None:
        return pyd.to_string(text)

    return replace(text, pattern, repl, ignore_case=ignore_case, count=count, escape=False)


def repeat(text: t.Any, n: t.SupportsInt = 0) -> str:
    """
    Repeats the given string `n` times.

    Args:
        text: String to repeat.
        n: Number of times to repeat the string.

    Returns:
        Repeated string.

    Example:

        >>> repeat('.', 5)
        '.....'

    .. versionadded:: 1.1.0
    """
    return pyd.to_string(text) * int(n)


def replace(
    text: t.Any,
    pattern: t.Any,
    repl: t.Union[str, t.Callable[[re.Match], str]],
    ignore_case: bool = False,
    count: int = 0,
    escape: bool = True,
    from_start: bool = False,
    from_end: bool = False,
) -> str:
    """
    Replace occurrences of `pattern` with `repl` in `text`. Optionally, ignore case when replacing.
    Optionally, set `count` to limit number of replacements.

    Args:
        text: String to replace.
        pattern: Pattern to find and replace.
        repl: String to substitute `pattern` with.
        ignore_case: Whether to ignore case when replacing. Defaults to ``False``.
        count: Maximum number of occurrences to replace. Defaults to ``0`` which
            replaces all.
        escape: Whether to escape `pattern` when searching. This is needed if a
            literal replacement is desired when `pattern` may contain special regular expression
            characters. Defaults to ``True``.
        from_start: Whether to limit replacement to start of string.
        from_end: Whether to limit replacement to end of string.

    Returns:
        Replaced string.

    Example:

        >>> replace('aabbcc', 'b', 'X')
        'aaXXcc'
        >>> replace('aabbcc', 'B', 'X', ignore_case=True)
        'aaXXcc'
        >>> replace('aabbcc', 'b', 'X', count=1)
        'aaXbcc'
        >>> replace('aabbcc', '[ab]', 'X')
        'aabbcc'
        >>> replace('aabbcc', '[ab]', 'X', escape=False)
        'XXXXcc'

    .. versionadded:: 3.0.0

    .. versionchanged:: 4.1.0
        Added ``from_start`` and ``from_end`` arguments.

    .. versionchanged:: 5.0.0
        Added support for ``pattern`` as ``typing.Pattern`` object.
    """
    text = pyd.to_string(text)

    if pattern is None:
        return text

    if not pyd.is_function(repl):
        repl = pyd.to_string(repl)

    flags = re.IGNORECASE if ignore_case else 0

    if isinstance(pattern, typing.Pattern):
        pat = pattern
    else:
        pattern = pyd.to_string(pattern)

        if escape:
            pattern = re.escape(pattern)

        if from_start and not pattern.startswith("^"):
            pattern = "^" + pattern

        if from_end and not pattern.endswith("$"):
            pattern += "$"

        pat = re.compile(pattern, flags=flags)

    return pat.sub(repl, text, count=count)


def replace_end(
    text: t.Any,
    pattern: t.Any,
    repl: t.Union[str, t.Callable[[re.Match], str]],
    ignore_case: bool = False,
    escape: bool = True,
) -> str:
    """
    Like :func:`replace` except it only replaces `text` with `repl` if `pattern` mathces the end of
    `text`.

    Args:
        text: String to replace.
        pattern: Pattern to find and replace.
        repl: String to substitute `pattern` with.
        ignore_case: Whether to ignore case when replacing. Defaults to ``False``.
        escape: Whether to escape `pattern` when searching. This is needed if a
            literal replacement is desired when `pattern` may contain special regular expression
            characters. Defaults to ``True``.

    Returns:
        Replaced string.

    Example:

        >>> replace_end('aabbcc', 'b', 'X')
        'aabbcc'
        >>> replace_end('aabbcc', 'c', 'X')
        'aabbcX'

    .. versionadded:: 4.1.0
    """
    return replace(text, pattern, repl, ignore_case=ignore_case, escape=escape, from_end=True)


def replace_start(
    text: t.Any,
    pattern: t.Any,
    repl: t.Union[str, t.Callable[[re.Match], str]],
    ignore_case: bool = False,
    escape: bool = True,
) -> str:
    """
    Like :func:`replace` except it only replaces `text` with `repl` if `pattern` mathces the start
    of `text`.

    Args:
        text: String to replace.
        pattern: Pattern to find and replace.
        repl: String to substitute `pattern` with.
        ignore_case: Whether to ignore case when replacing. Defaults to ``False``.
        escape: Whether to escape `pattern` when searching. This is needed if a
            literal replacement is desired when `pattern` may contain special regular expression
            characters. Defaults to ``True``.

    Returns:
        Replaced string.

    Example:

        >>> replace_start('aabbcc', 'b', 'X')
        'aabbcc'
        >>> replace_start('aabbcc', 'a', 'X')
        'Xabbcc'

    .. versionadded:: 4.1.0
    """
    return replace(text, pattern, repl, ignore_case=ignore_case, escape=escape, from_start=True)


def separator_case(text: t.Any, separator: str) -> str:
    """
    Splits `text` on words and joins with `separator`.

    Args:
        text: String to convert.
        separator: Separator to join words with.

    Returns:
        Converted string.

    Example:

        >>> separator_case('a!!b___c.d', '-')
        'a-b-c-d'

    .. versionadded:: 3.0.0

    .. versionchanged:: 5.0.0
        Improved unicode word support.
    """
    return separator.join(word.lower() for word in words(text) if word)


def series_phrase(
    items: t.List[t.Any],
    separator: t.Any = ", ",
    last_separator: t.Any = " and ",
    serial: bool = False,
) -> str:
    """
    Join items into a grammatical series phrase, e.g., ``"item1, item2, item3 and item4"``.

    Args:
        items: List of string items to join.
        separator: Item separator. Defaults to ``', '``.
        last_separator: Last item separator. Defaults to ``' and '``.
        serial: Whether to include `separator` with `last_separator` when number of
            items is greater than 2. Defaults to ``False``.

    Returns:
        Joined string.

    Example:

        >>> series_phrase(['apples', 'bananas', 'peaches'])
        'apples, bananas and peaches'
        >>> series_phrase(['apples', 'bananas', 'peaches'], serial=True)
        'apples, bananas, and peaches'
        >>> series_phrase(['apples', 'bananas', 'peaches'], '; ', ', or ')
        'apples; bananas, or peaches'


    .. versionadded:: 3.0.0
    """
    items = pyd.chain(items).map(pyd.to_string).compact().value()
    item_count = len(items)

    separator = pyd.to_string(separator)
    last_separator = pyd.to_string(last_separator)

    if item_count > 2 and serial:
        last_separator = separator.rstrip() + last_separator

    if item_count >= 2:
        items = items[:-2] + [last_separator.join(items[-2:])]

    return separator.join(items)


def series_phrase_serial(
    items: t.List[t.Any], separator: t.Any = ", ", last_separator: t.Any = " and "
) -> str:
    """
    Join items into a grammatical series phrase using a serial separator, e.g., ``"item1, item2,
    item3, and item4"``.

    Args:
        items: List of string items to join.
        separator: Item separator. Defaults to ``', '``.
        last_separator: Last item separator. Defaults to ``' and '``.

    Returns:
        Joined string.

    Example:

        >>> series_phrase_serial(['apples', 'bananas', 'peaches'])
        'apples, bananas, and peaches'

    .. versionadded:: 3.0.0
    """
    return series_phrase(items, separator, last_separator, serial=True)


def slugify(text: t.Any, separator: str = "-") -> str:
    """
    Convert `text` into an ASCII slug which can be used safely in URLs. Incoming `text` is converted
    to unicode and noramlzied using the ``NFKD`` form. This results in some accented characters
    being converted to their ASCII "equivalent" (e.g. ``é`` is converted to ``e``). Leading and
    trailing whitespace is trimmed and any remaining whitespace or other special characters without
    an ASCII equivalent are replaced with ``-``.

    Args:
        text: String to slugify.
        separator: Separator to use. Defaults to ``'-'``.

    Returns:
        Slugified string.

    Example:

        >>> slugify('This is a slug.') == 'this-is-a-slug'
        True
        >>> slugify('This is a slug.', '+') == 'this+is+a+slug'
        True

    .. versionadded:: 3.0.0

    .. versionchanged:: 5.0.0
        Improved unicode word support.

    .. versionchanged:: 7.0.0
        Remove single quotes from output.
    """
    normalized = (
        unicodedata.normalize("NFKD", pyd.to_string(text))
        .encode("ascii", "ignore")
        .decode("utf8")
        .replace("'", "")
    )

    return separator_case(normalized, separator)


def snake_case(text: t.Any) -> str:
    """
    Converts `text` to snake case.

    Args:
        text: String to convert.

    Returns:
        String converted to snake case.

    Example:

        >>> snake_case('This is Snake Case!')
        'this_is_snake_case'

    .. versionadded:: 1.1.0

    .. versionchanged:: 4.0.0
        Removed alias ``underscore_case``.

    .. versionchanged:: 5.0.0
        Improved unicode word support.
    """
    return "_".join(word.lower() for word in compounder(text) if word)


def split(text: t.Any, separator: t.Union[str, Unset, None] = UNSET) -> t.List[str]:
    """
    Splits `text` on `separator`. If `separator` not provided, then `text` is split on whitespace.
    If `separator` is falsey, then `text` is split on every character.

    Args:
        text: String to explode.
        separator: Separator string to split on. Defaults to ``NoValue``.

    Returns:
        Split string.

    Example:

        >>> split('one potato, two potatoes, three potatoes, four!')
        ['one', 'potato,', 'two', 'potatoes,', 'three', 'potatoes,', 'four!']
        >>> split('one potato, two potatoes, three potatoes, four!', ',')
        ['one potato', ' two potatoes', ' three potatoes', ' four!']

    .. versionadded:: 2.0.0

    .. versionchanged:: 3.0.0
        Changed `separator` default to ``NoValue`` and supported splitting on whitespace by default.

    .. versionchanged:: 4.0.0
        Removed alias ``explode``.
    """
    text = pyd.to_string(text)

    if separator is UNSET:
        ret = text.split()
    elif separator:
        ret = text.split(separator)
    else:
        ret = chars(text)

    return ret


def start_case(text: t.Any) -> str:
    """
    Convert `text` to start case.

    Args:
        text: String to convert.

    Returns:
        String converted to start case.

    Example:

        >>> start_case("fooBar")
        'Foo Bar'

    .. versionadded:: 3.1.0

    .. versionchanged:: 5.0.0
        Improved unicode word support.
    """
    return " ".join(capitalize(word, strict=False) for word in compounder(text))


def starts_with(text: t.Any, target: t.Any, position: int = 0) -> bool:
    """
    Checks if `text` starts with a given target string.

    Args:
        text: String to check.
        target: String to check for.
        position: Position to search from. Defaults to beginning of `text`.

    Returns:
        Whether `text` starts with `target`.

    Example:

        >>> starts_with('abcdef', 'a')
        True
        >>> starts_with('abcdef', 'b')
        False
        >>> starts_with('abcdef', 'a', 1)
        False

    .. versionadded:: 1.1.0
    """
    text = pyd.to_string(text)
    target = pyd.to_string(target)
    return text[position:].startswith(target)


def strip_tags(text: t.Any) -> str:
    """
    Removes all HTML tags from `text`.

    Args:
        text: String to strip.

    Returns:
        String without HTML tags.

    Example:

        >>> strip_tags('<a href="#">Some link</a>')
        'Some link'

    .. versionadded:: 3.0.0
    """
    return RE_HTML_TAGS.sub("", pyd.to_string(text))


def substr_left(text: t.Any, subtext: str) -> str:
    """
    Searches `text` from left-to-right for `subtext` and returns a substring consisting of the
    characters in `text` that are to the left of `subtext` or all string if no match found.

    Args:
        text: String to partition.
        subtext: String to search for.

    Returns:
        Substring to left of `subtext`.

    Example:

        >>> substr_left('abcdefcdg', 'cd')
        'ab'

    .. versionadded:: 3.0.0
    """
    text = pyd.to_string(text)
    return text.partition(subtext)[0] if subtext else text


def substr_left_end(text: t.Any, subtext: str) -> str:
    """
    Searches `text` from right-to-left for `subtext` and returns a substring consisting of the
    characters in `text` that are to the left of `subtext` or all string if no match found.

    Args:
        text: String to partition.
        subtext: String to search for.

    Returns:
        Substring to left of `subtext`.

    Example:

        >>> substr_left_end('abcdefcdg', 'cd')
        'abcdef'

    .. versionadded:: 3.0.0
    """
    text = pyd.to_string(text)
    return text.rpartition(subtext)[0] or text if subtext else text


def substr_right(text: t.Any, subtext: str) -> str:
    """
    Searches `text` from right-to-left for `subtext` and returns a substring consisting of the
    characters in `text` that are to the right of `subtext` or all string if no match found.

    Args:
        text: String to partition.
        subtext: String to search for.

    Returns:
        Substring to right of `subtext`.

    Example:

        >>> substr_right('abcdefcdg', 'cd')
        'efcdg'

    .. versionadded:: 3.0.0
    """
    text = pyd.to_string(text)
    return text.partition(subtext)[2] or text if subtext else text


def substr_right_end(text: t.Any, subtext: str) -> str:
    """
    Searches `text` from left-to-right for `subtext` and returns a substring consisting of the
    characters in `text` that are to the right of `subtext` or all string if no match found.

    Args:
        text: String to partition.
        subtext: String to search for.

    Returns:
        Substring to right of `subtext`.

    Example:

        >>> substr_right_end('abcdefcdg', 'cd')
        'g'

    .. versionadded:: 3.0.0
    """
    text = pyd.to_string(text)
    return text.rpartition(subtext)[2] if subtext else text


def successor(char: t.Any) -> str:
    """
    Return the successor character of `char`.

    Args:
        char: Character to find the successor of.

    Returns:
        Successor character.

    Example:

        >>> successor('b')
        'c'
        >>> successor('B')
        'C'
        >>> successor('2')
        '3'

    .. versionadded:: 3.0.0
    """
    char = pyd.to_string(char)
    return chr(ord(char) + 1)


def surround(text: t.Any, wrapper: t.Any) -> str:
    """
    Surround a string with another string.

    Args:
        text: String to surround with `wrapper`.
        wrapper: String by which `text` is to be surrounded.

    Returns:
        Surrounded string.

    Example:

        >>> surround('abc', '"')
        '"abc"'
        >>> surround('abc', '!')
        '!abc!'

    .. versionadded:: 2.4.0
    """
    text = pyd.to_string(text)
    wrapper = pyd.to_string(wrapper)
    return f"{wrapper}{text}{wrapper}"


def swap_case(text: t.Any) -> str:
    """
    Swap case of `text` characters.

    Args:
        text: String to swap case.

    Returns:
        String with swapped case.

    Example:

        >>> swap_case('aBcDeF')
        'AbCdEf'

    .. versionadded:: 3.0.0
    """
    text = pyd.to_string(text)
    return text.swapcase()


def title_case(text: t.Any) -> str:
    """
    Convert `text` to title case.

    Args:
        text: String to convert.

    Returns:
        String converted to title case.

    Example:

        >>> title_case("bob's shop")
        "Bob's Shop"

    .. versionadded:: 3.0.0
    """
    text = pyd.to_string(text)
    # NOTE: Can't use text.title() since it doesn't handle apostrophes.
    return " ".join(word.capitalize() for word in re.split(" ", text))


def to_lower(text: t.Any) -> str:
    """
    Converts the given :attr:`text` to lower text.

    Args:
        text: String to convert.

    Returns:
        String converted to lower case.

    Example:

        >>> to_lower('--Foo-Bar--')
        '--foo-bar--'
        >>> to_lower('fooBar')
        'foobar'
        >>> to_lower('__FOO_BAR__')
        '__foo_bar__'

    .. versionadded:: 4.0.0
    """
    return pyd.to_string(text).lower()


def to_upper(text: t.Any) -> str:
    """
    Converts the given :attr:`text` to upper text.

    Args:
        text: String to convert.

    Returns:
        String converted to upper case.

    Example:

        >>> to_upper('--Foo-Bar--')
        '--FOO-BAR--'
        >>> to_upper('fooBar')
        'FOOBAR'
        >>> to_upper('__FOO_BAR__')
        '__FOO_BAR__'

    .. versionadded:: 4.0.0
    """
    return pyd.to_string(text).upper()


def trim(text: t.Any, chars: t.Union[str, None] = None) -> str:
    r"""
    Removes leading and trailing whitespace or specified characters from `text`.

    Args:
        text: String to trim.
        chars: Specific characters to remove.

    Returns:
        Trimmed string.

    Example:

        >>> trim('  abc efg\r\n ')
        'abc efg'

    .. versionadded:: 1.1.0
    """
    # pylint: disable=redefined-outer-name
    text = pyd.to_string(text)
    return text.strip(chars)


def trim_end(text: t.Any, chars: t.Union[str, None] = None) -> str:
    r"""
    Removes trailing whitespace or specified characters from `text`.

    Args:
        text: String to trim.
        chars: Specific characters to remove.

    Returns:
        Trimmed string.

    Example:

        >>> trim_end('  abc efg\r\n ')
        '  abc efg'

    .. versionadded:: 1.1.0

    .. versionchanged:: 4.0.0
        Renamed from ``trim_right`` to ``trim_end``.
    """
    text = pyd.to_string(text)
    return text.rstrip(chars)


def trim_start(text: t.Any, chars: t.Union[str, None] = None) -> str:
    r"""
    Removes leading  whitespace or specified characters from `text`.

    Args:
        text: String to trim.
        chars: Specific characters to remove.

    Returns:
        Trimmed string.

    Example:

        >>> trim_start('  abc efg\r\n ')
        'abc efg\r\n '

    .. versionadded:: 1.1.0

    .. versionchanged:: 4.0.0
        Renamed from ``trim_left`` to ``trim_start``.
    """
    text = pyd.to_string(text)
    return text.lstrip(chars)


def truncate(
    text: t.Any,
    length: int = 30,
    omission: str = "...",
    separator: t.Union[str, re.Pattern, None] = None,
) -> str:
    """
    Truncates `text` if it is longer than the given maximum string length. The last characters of
    the truncated string are replaced with the omission string which defaults to ``...``.

    Args:
        text: String to truncate.
        length: Maximum string length. Defaults to ``30``.
        omission: String to indicate text is omitted.
        separator: Separator pattern to truncate to.

    Returns:
        Truncated string.

    Example:

        >>> truncate('hello world', 5)
        'he...'
        >>> truncate('hello world', 5, '..')
        'hel..'
        >>> truncate('hello world', 10)
        'hello w...'
        >>> truncate('hello world', 10, separator=' ')
        'hello...'

    .. versionadded:: 1.1.0

    .. versionchanged:: 4.0.0
        Removed alias ``trunc``.
    """
    text = pyd.to_string(text)

    if len(text) <= length:
        return text

    omission_len = len(omission)
    text_len = length - omission_len
    text = text[:text_len]

    trunc_len = len(text)

    if pyd.is_string(separator):
        trunc_len = text.rfind(separator)
    elif pyd.is_reg_exp(separator):
        last = None
        for match in separator.finditer(text):
            last = match

        if last is not None:
            trunc_len = last.start()

    return text[:trunc_len] + omission


def unescape(text: t.Any) -> str:
    """
    The inverse of :func:`escape`. This method converts the HTML entities ``&amp;``, ``&lt;``,
    ``&gt;``, ``&quot;``, ``&#39;``, and ``&#96;`` in `text` to their corresponding characters.

    Args:
        text: String to unescape.

    Returns:
        HTML unescaped string.

    Example:

        >>> results = unescape('&quot;1 &gt; 2 &amp;&amp; 3 &lt; 4&quot;')
        >>> results == '"1 > 2 && 3 < 4"'
        True

    .. versionadded:: 1.0.0

    .. versionchanged:: 1.1.0
        Moved to :mod:`pydash.strings`.
    """
    text = pyd.to_string(text)
    return html.unescape(text)


def upper_case(text: t.Any) -> str:
    """
    Converts string to upper case, as space separated words.

    Args:
        text: String to be converted to uppercase.

    Returns:
        String converted to uppercase, as space separated words.

    Example:

        >>> upper_case('--foo-bar--')
        'FOO BAR'
        >>> upper_case('fooBar')
        'FOO BAR'
        >>> upper_case('/?*Foo10/;"B*Ar')
        'FOO 10 B AR'

    .. versionadded:: 4.0.0

    .. versionchanged:: 5.0.0
        Improved unicode word support.
    """
    return " ".join(compounder(text)).upper()


def upper_first(text: str) -> str:
    """
    Converts the first character of string to upper case.

    Args:
        text: String passed in by the user.

    Returns:
        String in which the first character is converted to upper case.

    Example:

        >>> upper_first('fred')
        'Fred'
        >>> upper_first('foo bar')
        'Foo bar'
        >>> upper_first('1foobar')
        '1foobar'
        >>> upper_first(';foobar')
        ';foobar'

    .. versionadded:: 4.0.0
    """
    return text[:1].upper() + text[1:]


def unquote(text: t.Any, quote_char: t.Any = '"') -> str:
    """
    Unquote `text` by removing `quote_char` if `text` begins and ends with it.

    Args:
        text: String to unquote.
        quote_char: Quote character to remove. Defaults to `"`.

    Returns:
        Unquoted string.

    Example:

        >>> unquote('"abc"')
        'abc'
        >>> unquote('"abc"', '#')
        '"abc"'
        >>> unquote('#abc', '#')
        '#abc'
        >>> unquote('#abc#', '#')
        'abc'

    .. versionadded:: 3.0.0
    """
    text = pyd.to_string(text)
    inner = text[1:-1]

    if text == f"{quote_char}{inner}{quote_char}":
        text = inner

    return text


def url(*paths: t.Any, **params: t.Any) -> str:
    """
    Combines a series of URL paths into a single URL. Optionally, pass in keyword arguments to
    append query parameters.

    Args:
        paths: URL paths to combine.

    Keyword Args:
        params: Query parameters.

    Returns:
        URL string.

    Example:

        >>> link = url('a', 'b', ['c', 'd'], '/', q='X', y='Z')
        >>> path, params = link.split('?')
        >>> path == 'a/b/c/d/'
        True
        >>> set(params.split('&')) == set(['q=X', 'y=Z'])
        True

    .. versionadded:: 2.2.0
    """
    # allow reassignment different type
    paths = pyd.chain(paths).flatten_deep().map(pyd.to_string).value()  # type: ignore
    paths_list = []
    params_list = flatten_url_params(params)

    for path in paths:
        scheme, netloc, path, query, fragment = urlsplit(path)
        query = parse_qsl(query)
        params_list += query
        paths_list.append(urlunsplit((scheme, netloc, path, "", fragment)))

    path = delimitedpathjoin("/", *paths_list)
    scheme, netloc, path, query, fragment = urlsplit(path)
    query = urlencode(params_list)

    return urlunsplit((scheme, netloc, path, query, fragment))


def words(text: t.Any, pattern: t.Union[str, None] = None) -> t.List[str]:
    """
    Return list of words contained in `text`.

    References:
        https://github.com/lodash/lodash/blob/master/words.js#L30

    Args:
        text: String to split.
        pattern: Custom pattern to split words on. Defaults to ``None``.

    Returns:
        List of words.

    Example:

        >>> words('a b, c; d-e')
        ['a', 'b', 'c', 'd', 'e']
        >>> words('fred, barney, & pebbles', '/[^, ]+/g')
        ['fred', 'barney', '&', 'pebbles']

    .. versionadded:: 2.0.0

    .. versionchanged:: 3.2.0
        Added `pattern` argument.

    .. versionchanged:: 3.2.0
        Improved matching for one character words.

    .. versionchanged:: 5.0.0
        Improved unicode word support.
    """
    text = pyd.to_string(text)
    if pattern is None:
        if has_unicode_word(text):
            reg_exp = JS_RE_UNICODE_WORDS
        else:
            reg_exp = JS_RE_ASCII_WORDS
    else:
        reg_exp = JSRegExp(pattern)
    return reg_exp.find(text)


#
# Utility functions not a part of main API
#


def compounder(text):
    """
    Remove single quote before passing into words() to match Lodash-style outputs.

    Required by certain functions such as kebab_case, camel_case, start_case etc.

    References:
        https://github.com/lodash/lodash/blob/4.17.15/lodash.js#L4968
    """
    return words(deburr(RE_APOS.sub("", pyd.to_string(text))))


def has_unicode_word(text):
    """
    Check if the text contains unicode or requires more complex regex to handle.

    References:
        https://github.com/lodash/lodash/blob/master/words.js#L3
    """
    result = RE_HAS_UNICODE_WORD.search(text)
    return bool(result)


def delimitedpathjoin(delimiter, *paths):
    """
    Join delimited path using specified delimiter.

    >>> assert delimitedpathjoin('.', '') == ''
    >>> assert delimitedpathjoin('.', '.') == '.'
    >>> assert delimitedpathjoin('.', ['', '.a']) == '.a'
    >>> assert delimitedpathjoin('.', ['a', '.']) == 'a.'
    >>> assert delimitedpathjoin('.', ['', '.a', '', '', 'b']) == '.a.b'
    >>> ret = '.a.b.c.d.e.'
    >>> assert delimitedpathjoin('.', ['.a.', 'b.', '.c', 'd', 'e.']) == ret
    >>> assert delimitedpathjoin('.', ['a', 'b', 'c']) == 'a.b.c'
    >>> ret = 'a.b.c.d.e.f'
    >>> assert delimitedpathjoin('.', ['a.b', '.c.d.', '.e.f']) == ret
    >>> ret = '.a.b.c.1.'
    >>> assert delimitedpathjoin('.', '.', 'a', 'b', 'c', 1, '.') == ret
    >>> assert delimitedpathjoin('.', []) == ''
    """
    paths = [pyd.to_string(path) for path in pyd.flatten_deep(paths) if path]

    if len(paths) == 1:
        # Special case where there's no need to join anything. Doing this because if
        # path==[delimiter], then an extra delimiter would be added if the else clause ran instead.
        path = paths[0]
    else:
        leading = delimiter if paths and paths[0].startswith(delimiter) else ""
        trailing = delimiter if paths and paths[-1].endswith(delimiter) else ""
        middle = delimiter.join([path.strip(delimiter) for path in paths if path.strip(delimiter)])
        path = "".join([leading, middle, trailing])

    return path


def flatten_url_params(
    params: t.Union[
        t.Dict[T, t.Union[T2, t.Iterable[T2]]],
        t.List[t.Tuple[T, t.Union[T2, t.Iterable[T2]]]],
    ],
) -> t.List[t.Tuple[T, T2]]:
    """
    Flatten URL params into list of tuples. If any param value is a list or tuple, then map each
    value to the param key.

    >>> params = [('a', 1), ('a', [2, 3])]
    >>> assert flatten_url_params(params) == [('a', 1), ('a', 2), ('a', 3)]
    >>> params = {'a': [1, 2, 3]}
    >>> assert flatten_url_params(params) == [('a', 1), ('a', 2), ('a', 3)]
    """
    if isinstance(params, dict):
        params = list(params.items())

    flattened: t.List = []
    for param, value in params:
        if isinstance(value, (list, tuple)):
            flattened += zip([param] * len(value), value)
        else:
            flattened.append((param, value))

    return flattened
