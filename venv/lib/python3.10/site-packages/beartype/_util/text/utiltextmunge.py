#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

"""
**Beartype string munging utilities** (i.e., callables transforming passed
strings into new strings with generic string operations).

This private submodule is *not* intended for importation by downstream callers.
"""

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeUtilTextException
from beartype._data.kind.datakindtext import CHARS_PUNCTUATION

# ....................{ CASERS                             }....................
def uppercase_str_char_first(text: str) -> str:
    '''
    Uppercase *only* the first character of the passed string.

    Whereas the standard :meth:`str.capitalize` method both uppercases the
    first character of this string *and* lowercases all remaining characters,
    this function *only* uppercases the first character. All remaining
    characters remain unmodified.

    Parameters
    ----------
    text : str
        String whose first character is to be uppercased.

    Returns
    ----------
    str
        This string with the first character uppercased.
    '''
    assert isinstance(text, str), f'{repr(text)} not string.'

    # If...
    if (
        # This string contains at least two characters *AND*...
        len(text) >= 2 and
        # The first character of this string is lowercase...
        text[0].islower()
    ):
        # Then uppercase only this string for readability.
        text = f'{text[0].upper()}{text[1:]}'

    # Return this possibly changed string.
    return text

# ....................{ NUMBERERS                          }....................
def number_str_lines(text: str) -> str:
    '''
    Passed string munged to prefix each line of this string with the 1-based
    number of that line padded by zeroes out to four digits for alignment.

    Parameters
    ----------
    text : str
        String whose lines are to be numbered.

    Returns
    ----------
    str
        This string with all lines numbered.
    '''
    assert isinstance(text, str), f'{repr(text)} not string.'

    # For radical benevolence!
    return '\n'.join(
        '(line {:0>4d}) {}'.format(text_line_number, text_line)
        for text_line_number, text_line in enumerate(
            text.splitlines(), start=1)
    )

# ....................{ REPLACERS                          }....................
def replace_str_substrs(text: str, old: str, new: str) -> str:
    '''
    Passed string with all instances of the passed source substring globally
    replaced by the passed target substring if this string contains at least
    one such instance *or* raise an exception otherwise (i.e., if this string
    contains *no* such instance).

    Caveats
    ----------
    **This higher-level function should always be called in lieu of the
    lower-level** :meth:`str.replace` method, which unconditionally succeeds
    regardless of whether this subject string contains at least one instance of
    this source substring or not.

    Parameters
    ----------
    text : str
        Subject string to perform this global replacement on.
    old : str
        Source substring of this subject string to be globally replaced.
    new : str
        Target substring to globally replace this source substring with in this
        subject string.

    Returns
    ----------
    str
        Subject string with all instances of this source substring globally
        replaced by this target substring.

    Raises
    ----------
    _BeartypeUtilTextException
        If this subject string contains *no* instances of this source
        substring.

    Examples
    ----------
        >>> from beartype._util.text.utiltextmunge import replace_str_substrs
        >>> replace_str_substrs(
        ...     text='And now the STORM-BLAST came, and he',
        ...     old='he', new='hat')
        And now that STORM-BLAST came, and hat
        >>> replace_str_substrs(
        ...     text='I shot the ALBATROSS.', old='dross', new='drat')
        beartype.roar._BeartypeUtilTextException: String "I shot the
        ALBATROSS." substring "dross" not found.
    '''
    assert isinstance(text, str), f'{repr(text)} not string.'
    assert isinstance(old, str), f'{repr(old)} not string.'
    assert isinstance(new, str), f'{repr(new)} not string.'

    # If this subject contains *NO* instances of this substring, raise an
    # exception.
    if old not in text:
        raise _BeartypeUtilTextException(
            f'String "{text}" substring "{old}" not found.')
    # Else, this subject contains one or more instances of this substring.

    # Return this subject with all instances of this source substring globally
    # replaced by this target substring.
    return text.replace(old, new)

# ....................{ SUFFIXERS                          }....................
def suffix_str_unless_suffixed(text: str, suffix: str) -> str:
    '''
    Passed string either suffixed by the passed suffix if this string is not
    yet suffixed by this suffix *or* this string as is otherwise (i.e., if this
    string is already suffixed by this suffix).

    Parameters
    ----------
    text : str
        String to be conditionally suffixed.
    suffix : str
        Suffix to be conditionally appended to this string.

    Returns
    ----------
    str
        Either:

        * If this string is *not* yet suffixed by this suffix, this string
          suffixed by this suffix.
        * Else, this string as is.
    '''
    assert isinstance(text, str), f'{repr(text)} not string.'
    assert isinstance(suffix, str), f'{repr(suffix)} not string.'

    # Suffix us up the redemption arc.
    return text if text.endswith(suffix) else text + suffix

# ....................{ TRUNCATERS                         }....................
def truncate_str(
    # Mandatory parameters.
    text: str,

    # Optional parameters.
    max_len: int = 96,
) -> str:
    '''
    Truncate the passed string to the passed maximum string length.

    Specifically, this function returns either:

    * If the length of this string is less than this maximum, this string
      unmodified as is.
    * Else, this string with the suffix of this string exceeding this maximum
      replaced by an ASCII ellipsis (i.e., ``"..."`` substring).

    Caveats
    ----------
    **This function is unavoidably slow and should thus not be called from
    optimized performance-critical code.** This function internally performs
    mildly expensive operations, including iterating-based string munging.
    Ideally, this function should *only* be called to create user-oriented
    exception messages where performance is a negligible concern.

    Parameters
    ----------
    obj : object
        String to be truncated.
    max_len: int, optional
        Maximum length of the string to be returned. Defaults to a standard
        line length of 100 characters minus output indentation of 4 characters.

    Returns
    ----------
    str
        This string possibly truncated.
    '''
    assert isinstance(text, str), f'{repr(text)} not string.'
    assert isinstance(max_len, int), f'{repr(max_len)} not integer.'
    assert max_len >= 0, f'{max_len} < 0.'

    # If this maximum length is *NOT* long enough to at least allow truncation
    # to ellipsis (i.e., a substring of length 3). In this case, truncate this
    # string to this length *WITHOUT* ellipsis.
    if max_len <= 3:
        return text[:max_len]
    # Else, this maximum length is long enough to at least allow truncation to
    # ellipsis (i.e., a substring of length 3).

    # Length of this string.
    text_len = len(text)

    # If this string does *NOT* exceed this maximum length, this string requires
    # *NO* truncation. In this case, return this string as is.
    if text_len <= max_len:
        return text
    # Else, this string exceeds this maximum length and thus requires
    # truncation.

    # Length of this string minus one.
    text_len_minus_1 = text_len - 1

    # Length of the truncated prefix of this string to be returned below,
    # initialized to this maximum length minus the length of the ellipsis (i.e.,
    # 3 characters) to be injected into this string.
    text_prefix_len = max_len - 3

    # 0-based index of the last character of this string that is *NOT* a
    # punctuation character, initialized to the length of this string.
    text_suffix_start_index = text_len
    # print(f'\nstring: {text}')
    # print(f'text_len: {text_len}')
    # print(f'max_len: {max_len}')
    # print(f'[before backing up] text_prefix_len: {text_prefix_len}')
    # print(f'[before backing up] text_suffix_start_index: {text_suffix_start_index}')

    # While...
    while (
        # There exists at least one remaining character to truncate from this
        # string *AND*...
        text_prefix_len >= 1 and
        # The character preceding the current trailing punctuation character of
        # this string is also a punctuation character...
        text[text_suffix_start_index - 1] in CHARS_PUNCTUATION
    ):
        # Truncate one additional character from this string.
        text_prefix_len -= 1

        # Prepend one additional trailing punctuation character onto this
        # suffixing substring.
        text_suffix_start_index -= 1
    # print(f'[after backing up] text_prefix_len: {text_prefix_len}')
    # print(f'[after backing up] text_suffix_start_index: {text_suffix_start_index}')

    # While...
    while (
        # There exists at least one remaining trailing punctuation character to
        # inspect in this string *AND*...
        text_suffix_start_index <= text_len_minus_1 and
        # The character currently prefixing this suffixing substring of
        # trailing punctuation characters is a period...
        text[text_suffix_start_index] == '.'
    ):
        # Append one additional character back onto this string.
        text_prefix_len += 1

        # Remove this period from this suffixing substring. Why? Because this
        # period will already be included in the ellipsis injected into this
        # string below. Look. It's complicated. Just wave your hands in the air!
        text_suffix_start_index += 1
    # print(f'[after eating dots] text_prefix_len: {text_prefix_len}')
    # print(f'[after eating dots up] text_suffix_start_index: {text_suffix_start_index}')

    # Truncated string to be returned, comprising...
    text = (
        # The prefixing substring of this string *NOT* exceeding this maximum
        # length.
        f'{text[:text_prefix_len]}'
        # An ellipsis replacing the remaining truncated middle of this string.
        f'...'
        # The suffixing substring of trailing punctuation characters.
        f'{text[text_suffix_start_index:]}'
    )

    # Return this truncated string.
    return text
