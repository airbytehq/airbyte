#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **string getters** (i.e., low-level callables slicing and returning
substrings out of arbitrary strings, typically to acquire prefixes and suffixes
satisfying various conditions).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
# from beartype.roar._roarexc import _BeartypeUtilTextException

# ....................{ GETTERS                            }....................
#FIXME: Uncomment if ever needed.
# def get_str_prefix_greedy(text: str, anchor: str) -> str:
#     '''
#     **Greedily anchored prefix** (i.e., substring ranging from the first
#     character to the last instance of the passed substring) of the passed
#     string if any *or* raise an exception otherwise (i.e., if this string
#     contains no such substring).
#
#     Parameters
#     ----------
#     text : str
#         String to be searched.
#     anchor: str
#         Substring to search this string for.
#
#     Returns
#     ----------
#     str
#         Prefix of this string preceding the last instance of this substring.
#
#     Raises
#     ----------
#     _BeartypeUtilTextException
#         If this string contains *no* instance of this substring.
#
#     See Also
#     ----------
#     :func:`get_str_prefix_greedy_or_none`
#         Further details.
#     '''
#
#     # Greedily anchored prefix of this string if any *OR* "None" otherwise.
#     text_prefix_greedy = get_str_prefix_greedy_or_none(text, anchor)
#
#     # If this string contains *NO* such prefix, raise an exception.
#     if text_prefix_greedy is None:
#         raise _BeartypeUtilTextException(
#             f'String "{text}" substring "{anchor}" not found.')
#
#     # Else, return this prefix.
#     return text_prefix_greedy


#FIXME: Uncomment if ever needed.
# def get_str_prefix_greedy_or_none(text: str, anchor: str) -> 'Optional[str]':
#     '''
#     **Greedily anchored prefix** (i.e., substring ranging from the first
#     character to the last instance of the passed substring) of the passed
#     string if any *or* ``None`` otherwise (i.e., if this string contains no
#     such substring).
#
#     Parameters
#     ----------
#     text : str
#         String to be searched.
#     anchor: str
#         Substring to search this string for.
#
#     Returns
#     ----------
#     Optional[str]
#         Either:
#
#         * If this string contains this substring, the prefix of this string
#           preceding the last instance of this substring.
#         * Else, ``None``.
#
#     Examples
#     ----------
#         >>> from beartype._util.text.utiltextget import (
#         ...     get_str_prefix_greedy_or_none)
#         >>> get_str_prefix_greedy_or_none(
#         ...     text='Opposition...contradiction...premonition...compromise.',
#         ...     anchor='.')
#         Opposition...contradiction...premonition...compromise
#         >>> get_str_prefix_greedy_or_none(
#         ...     text='This is an anomaly. Disabled. What is true?',
#         ...     anchor='!')
#         None
#     '''
#     assert isinstance(text, str), f'{repr(text)} not string.'
#     assert isinstance(anchor, str), f'{repr(anchor)} not string.'
#
#     # Return either...
#     return (
#         # If this string contains this substring, the substring of this string
#         # preceding the last instance of this substring in this string.
#         text[:text.rindex(anchor)]
#         if anchor in text else
#         # Else, "None".
#         None
#     )
