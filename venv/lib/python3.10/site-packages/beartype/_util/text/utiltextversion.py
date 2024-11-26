#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **version string utilities** (i.e., low-level callables handling
human-readable ``.``-delimited version strings).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeUtilTextVersionException
from beartype.typing import Tuple
from re import compile as re_compile

# ....................{ CONVERTERS                         }....................
def convert_str_version_to_tuple(version: str) -> Tuple[int, ...]:
    '''
    Convert the passed human-readable ``.``-delimited version string into a
    machine-readable version tuple of corresponding integers, suitable for
    efficient comparison against other such version tuples via standard rich
    comparison operators (e.g., ``<``, ``==``).

    Caveats
    ----------
    **This converter strictly requires each ``.``-delimited substring of this
    string to be a non-negative integer.** The exception is the last
    ``.``-prefixed substring of this string, which this converter permits to
    *not* be a non-negative integer. Specifically, that last substring:

    * *Must* be prefixed by a non-negative integer.
    * *May* be followed by any other arbitrary characters, which this converter
      silently ignores as supplementary software-specific version metadata
      (e.g., release candidates, alpha releases, beta releases). Since that
      metadata does *not* cleanly generalize to all possible use cases, that
      metadata *cannot* be safely converted into a non-negative integer.

    For example, this converter:

    * Converts the valid version string ``"1.26.0"`` to ``(1, 26, 0)``.
    * Converts the valid version string ``"1.26.0rc1"`` to ``(1, 26, 0)`` by
      simply ignoring the non-numeric suffix ``"rc1"``.
    * Raises an exception for the invalid version string ``"1.26.rc1"``.

    Parameters
    ----------
    text : str
        Version string to be converted.

    Returns
    ----------
    Tuple[int, ...]
        Machine-readable version tuple of corresponding integers.

    Raises
    ----------
    _BeartypeUtilTextVersionException
        If this string is syntactically invalid as a version.
    '''
    assert isinstance(version, str), f'{repr(version)} not version string.'

    # List of either:
    # * If this version contains one or more "." delimiters, all "."-delimited
    #   version components split from this version.
    # * If this version contains *NO* "." delimiters, the 1-list "[version,]".
    version_substrs = version.split('.')

    # 0-based index of the last version component in this list.
    version_substr_index_last = len(version_substrs) - 1

    # List of all version components to be returned as a tuple.
    version_list = []

    # For the 0-based index of each "."-delimited version component of this
    # version string and that component...
    for version_substr_index, version_substr in enumerate(version_substrs):
        # Attempt to...
        try:
            # Coerce this version component into an integer.
            version_part = int(version_substr)

            # If this component is negative, raise an exception.
            if version_part < 0:
                raise _BeartypeUtilTextVersionException(
                    f'Version {repr(version)} syntactically invalid '
                    f'(i.e., version component {repr(version_substr)} negative).'
                )
            # Else, this component is non-negative.
        # If doing so raises a "ValueError", this version component is *NOT*
        # syntactically valid as an integer. In this case...
        except ValueError as exception:
            # If the 0-based index of this version component is that of the last
            # version component in this list, this is *NOT* the last version
            # component. In this case, this component is syntactically invalid.
            # Raise an exception.
            if version_substr_index != version_substr_index_last:
                raise _BeartypeUtilTextVersionException(
                    f'Version {repr(version)} syntactically invalid '
                    f'(i.e., version component {repr(version_substr)} '
                    f'not an integer).'
                ) from exception
            # Else, this is the last version component. In this case, reduce
            # this component to its non-negative integer prefix.

            # Match result if this component is prefixed by a non-negative
            # integer *OR* "None" otherwise (i.e., if this component is
            # syntactically invalid).
            version_substr_match = _VERSION_SUBSTR_LAST_REGEX.match(
                version_substr)

            # If this component is syntactically invalid, raise an exception.
            if version_substr_match is None:
                raise _BeartypeUtilTextVersionException(
                    f'Version {repr(version)} syntactically invalid '
                    f'(i.e., version component {repr(version_substr)} '
                    f'not an integer).'
                ) from exception
            # Else, this component is syntactically valid.

            # Non-negative integer prefixing this component.
            version_part = int(version_substr_match.group(1))

        # Append this version component to this list.
        version_list.append(version_part)

    # Return this list coerced into a tuple.
    return tuple(version_list)

# ....................{ PRIVATE ~ constants                }....................
_VERSION_SUBSTR_LAST_REGEX = re_compile(r'([0-9]+).+')
'''
Compiled regular expression matching the non-negative integer prefixing the last
``.``-delimited version component in a version string (e.g., ``"5"`` in the
version string ``"5rc27"``).
'''
