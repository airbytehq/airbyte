#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **string joining utilities** (i.e., callables joining passed
strings into new strings delimited by passed substring delimiters).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import Iterable as typing_Iterable
from beartype._data.hint.datahinttyping import IterableStrs
from collections.abc import (
    Iterable,
    Sequence,
)

# ....................{ JOINERS                            }....................
#FIXME: Unit test the "is_double_quoted" parameter, please.
def join_delimited(
    # Mandatory parameters.
    strs: IterableStrs,

    # Mandatory keyword-only parameters.
    *,
    delimiter_if_two: str,
    delimiter_if_three_or_more_nonlast: str,
    delimiter_if_three_or_more_last: str,

    # Optional keyword-only parameters.
    is_double_quoted: bool = False,
) -> str:
    '''
    Concatenate the passed iterable of zero or more strings delimited by the
    passed delimiter (conditionally depending on both the length of this
    sequence and index of each string in this sequence), yielding a
    human-readable string listing arbitrarily many substrings.

    Specifically, this function returns either:

    * If this iterable contains no strings, the empty string.
    * If this iterable contains one string, this string as is is unmodified.
    * If this iterable contains two strings, these strings delimited by the
      passed ``delimiter_if_two`` delimiter.
    * If this iterable contains three or more strings, a string listing these
      contained strings such that:

      * All contained strings except the last two are suffixed by the passed
        ``delimiter_if_three_or_more_nonlast`` delimiter.
      * The last two contained strings are delimited by the passed
        ``delimiter_if_three_or_more_last`` separator.

    Parameters
    ----------
    strs : Iterable[str]
        Iterable of all strings to be joined.
    delimiter_if_two : str
        Substring separating each string contained in this iterable if this
        iterable contains exactly two strings.
    delimiter_if_three_or_more_nonlast : str
        Substring separating each string *except* the last two contained in
        this iterable if this iterable contains three or more strings.
    delimiter_if_three_or_more_last : str
        Substring separating each string the last two contained in this
        iterable if this iterable contains three or more strings.
    is_double_quoted : bool, optional
        :data:`True` only if **double-quoting** (i.e., both prefixing and
        suffixing by the ``"`` character) each item of this iterable. Defaults
        to :data:`False`.

    Returns
    ----------
    str
        Concatenation of these strings.

    Examples
    ----------
        >>> join_delimited(
        ...     strs=('Fulgrim', 'Perturabo', 'Angron', 'Mortarion'),
        ...     delimiter_if_two=' and ',
        ...     delimiter_if_three_or_more_nonlast=', ',
        ...     delimiter_if_three_or_more_last=', and '
        ... )
        'Fulgrim, Perturabo, Angron, and Mortarion'
    '''
    assert isinstance(strs, Iterable) and not isinstance(strs, str), (
        f'{repr(strs)} not non-string iterable.')
    assert isinstance(delimiter_if_two, str), (
        f'{repr(delimiter_if_two)} not string.')
    assert isinstance(delimiter_if_three_or_more_nonlast, str), (
        f'{repr(delimiter_if_three_or_more_nonlast)} not string.')
    assert isinstance(delimiter_if_three_or_more_last, str), (
        f'{repr(delimiter_if_three_or_more_last)} not string.')

    # If this iterable is *NOT* a sequence, internally coerce this iterable
    # into a sequence for subsequent indexing purposes.
    if not isinstance(strs, Sequence):
        strs = tuple(strs)
    # Else, this iterable is already a sequence.
    #
    # In either case, this iterable is now a sequence.

    # If double-quoting these strings, do so.
    if is_double_quoted:
        strs = tuple(f'"{text}"' for text in strs)
    # Else, preserve these strings as is.

    # Number of strings in this sequence.
    num_strs = len(strs)

    # If no strings are passed, return the empty string.
    if num_strs == 0:
        return ''
    # If one string is passed, return this string as is.
    elif num_strs == 1:
        # This is clearly a string, yet mypy thinks it's Any
        return strs[0]  # type: ignore[no-any-return]
    # If two strings are passed, return these strings delimited appropriately.
    elif num_strs == 2:
        return f'{strs[0]}{delimiter_if_two}{strs[1]}'
    # Else, three or more strings are passed.

    # All such strings except the last two, delimited appropriately.
    strs_nonlast = delimiter_if_three_or_more_nonlast.join(strs[0:-2])

    # The last two such strings, delimited appropriately.
    strs_last = f'{strs[-2]}{delimiter_if_three_or_more_last}{strs[-1]}'

    # Return these two substrings, delimited appropriately.
    return f'{strs_nonlast}{delimiter_if_three_or_more_nonlast}{strs_last}'

# ....................{ JOINERS ~ disjunction              }....................
def join_delimited_disjunction(strs: IterableStrs, **kwargs) -> str:
    '''
    Concatenate the passed iterable of zero or more strings delimited by commas
    and/or the disjunction "or" (conditionally depending on both the length of
    this iterable and index of each string in this iterable), yielding a
    human-readable string listing arbitrarily many substrings disjunctively.

    Specifically, this function returns either:

    * If this iterable contains no strings, the empty string.
    * If this iterable contains one string, this string as is is unmodified.
    * If this iterable contains two strings, these strings delimited by the
      disjunction "or".
    * If this iterable contains three or more strings, a string listing these
      contained strings such that:

      * All contained strings except the last two are suffixed by commas.
      * The last two contained strings are delimited by the disjunction "or".

    Parameters
    ----------
    strs : Iterable[str]
        Iterable of all strings to be concatenated disjunctively.

    All remaining keyword parameters are passed as is to the lower-level
    :func:`.join_delimeted` function underlying this higher-level function.

    Returns
    ----------
    str
        Disjunctive concatenation of these strings.
    '''

    # He will join us... OR DIE! *cackling heard*
    return join_delimited(
        strs=strs,
        delimiter_if_two=' or ',
        delimiter_if_three_or_more_nonlast=', ',
        delimiter_if_three_or_more_last=', or ',
        **kwargs
    )


def join_delimited_disjunction_types(types: typing_Iterable[type]) -> str:
    '''
    Concatenate the human-readable classname of each class in the passed
    iterable delimited by commas and/or the disjunction "or" (conditionally
    depending on both the length of this iterable and index of each string in
    this iterable), yielding a human-readable string listing arbitrarily many
    classnames disjunctively.

    Parameters
    ----------
    types : Iterable[type]
        Iterable of all classes whose human-readable classnames are to be
        concatenated disjunctively.

    Returns
    ----------
    str
        Disjunctive concatenation of these classnames.
    '''

    # Avoid circular import dependencies.
    from beartype._util.text.utiltextlabel import label_type

    # Make it so, ensign.
    return join_delimited_disjunction(label_type(cls) for cls in types)
