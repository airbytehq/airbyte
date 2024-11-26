#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **exception handling utilities** (i.e., low-level functions
manipulating exceptions in a general-purpose manner).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._util.text.utiltextmunge import uppercase_str_char_first

# ....................{ CONSTANTS                          }....................
EXCEPTION_PLACEHOLDER = '$%ROOT_PITH_LABEL/~'
'''
Non-human-readable source substring to be globally replaced by a human-readable
target substring in the messages of memoized exceptions passed to the
:func:`reraise_exception` function.

This substring prefixes most exception messages raised by memoized callables,
including code generation factories memoized on passed PEP-compliant type hints
(e.g., the :mod:`beartype._check` and :mod:`beartype._decor` submodules). The
:func:`beartype._util.error.utilerror.reraise_exception_placeholder` function
then dynamically replaces this prefix of the message of the passed exception
with a human-readable synopsis of the current unmemoized exception context,
including the name of both the currently decorated callable *and* the currently
iterated parameter or return of that callable for aforementioned code generation
factories.

Usage
----------
This substring is typically hard-coded into non-human-readable exception
messages raised by low-level callables memoized with the
:func:`beartype._util.cache.utilcachecall.callable_cached` decorator. Why?
Memoization prohibits those callables from raising human-readable exception
messages. Why? Doing so would require those callables to accept fine-grained
parameters unique to each call to those callables, which those callables would
then dynamically format into human-readable exception messages raised by those
callables. The standard example would be a ``exception_prefix`` parameter
labelling the human-readable category of type hint being inspected by the
current call (e.g., ``@beartyped muh_func() parameter "muh_param" PEP type hint
"List[int]"`` for a ``List[int]`` type hint on the `muh_param` parameter of a
``muh_func()`` function decorated by the :func:`beartype.beartype` decorator).
Since the whole point of memoization is to cache callable results between calls,
any callable accepting any fine-grained parameter unique to each call to that
callable is effectively *not* memoizable in any meaningful sense of the
adjective "memoizable." Ergo, memoized callables *cannot* raise human-readable
exception messages unique to each call to those callables.

This substring indirectly solves this issue by inverting the onus of human
readability. Rather than requiring memoized callables to raise human-readable
exception messages unique to each call to those callables (which we've shown
above to be pragmatically infeasible), memoized callables instead raise
non-human-readable exception messages containing this substring where they
instead would have contained the human-readable portions of their messages
unique to each call to those callables. This indirection renders exceptions
raised by memoized callables generic between calls and thus safely memoizable.

This indirection has the direct consequence, however, of shifting the onus of
human readability from those lower-level memoized callables onto higher-level
non-memoized callables -- which are then required to explicitly (in order):

#. Catch exceptions raised by those lower-level memoized callables.
#. Call the :func:`reraise_exception_placeholder` function with those
   exceptions and desired human-readable substrings. That function then:

   #. Replaces this magic substring hard-coded into those exception messages
      with those human-readable substring fragments.
   #. Reraises the original exceptions in a manner preserving their original
      tracebacks.

Unsurprisingly, as with most inversion of control schemes, this approach is
non-intuitive. Surprisingly, however, the resulting code is actually *more*
elegant than the standard approach of raising human-readable exceptions from
low-level callables. Why? Because the standard approach percolates
human-readable substring fragments from the higher-level callables defining
those fragments to the lower-level callables raising exception messages
containing those fragments. The indirect approach avoids percolation, thus
streamlining the implementations of all callables involved. Phew!
'''

# ....................{ RAISERS                            }....................
def reraise_exception_placeholder(
    # Mandatory parameters.
    exception: Exception,
    target_str: str,

    # Optional parameters.
    source_str: str = EXCEPTION_PLACEHOLDER,
) -> None:
    '''
    Reraise the passed exception in a safe manner preserving both this exception
    object *and* the original traceback associated with this exception object,
    but globally replacing all instances of the passed source substring
    hard-coded into this exception's message with the passed target substring.

    Parameters
    ----------
    exception : Exception
        Exception to be reraised.
    target_str : str
        Target human-readable format substring to replace the passed source
        substring previously hard-coded into this exception's message.
    source_str : Optional[str]
        Source non-human-readable substring previously hard-coded into this
        exception's message to be replaced by the passed target substring.
        Defaults to :data:`.EXCEPTION_PLACEHOLDER`.

    Raises
    ----------
    exception
        The passed exception, globally replacing all instances of this source
        substring in this exception's message with this target substring.


    See Also
    ----------
    :data:`.EXCEPTION_PLACEHOLDER`
        Further commentary on usage and motivation.
    https://stackoverflow.com/a/62662138/2809027
        StackOverflow answer mildly inspiring this implementation.

    Examples
    ----------
        >>> from beartype.roar import BeartypeDecorHintPepException
        >>> from beartype._util.cache.utilcachecall import callable_cached
        >>> from beartype._util.error.utilerror import (
        ...     reraise_exception_placeholder, EXCEPTION_PLACEHOLDER)
        >>> from random import getrandbits
        >>> @callable_cached
        ... def portend_low_level_winter(is_winter_coming: bool) -> str:
        ...     if is_winter_coming:
        ...         raise BeartypeDecorHintPepException(
        ...             '{} intimates that winter is coming.'.format(
        ...                 EXCEPTION_PLACEHOLDER))
        ...     else:
        ...         return 'PRAISE THE SUN'
        >>> def portend_high_level_winter() -> None:
        ...     try:
        ...         print(portend_low_level_winter(is_winter_coming=False))
        ...         print(portend_low_level_winter(is_winter_coming=True))
        ...     except BeartypeDecorHintPepException as exception:
        ...         reraise_exception_placeholder(
        ...             exception=exception,
        ...             target_str=(
        ...                 'Random "Song of Fire and Ice" spoiler' if getrandbits(1) else
        ...                 'Random "Dark Souls" plaintext meme'
        ...             ))
        >>> portend_high_level_winter()
        PRAISE THE SUN
        Traceback (most recent call last):
          File "<input>", line 30, in <module>
            portend_high_level_winter()
          File "<input>", line 27, in portend_high_level_winter
            'Random "Dark Souls" plaintext meme'
          File "/home/leycec/py/beartype/beartype._util.error.utilerror.py", line 225, in reraise_exception_placeholder
            raise exception.with_traceback(exception.__traceback__)
          File "<input>", line 20, in portend_high_level_winter
            print(portend_low_level_winter(is_winter_coming=True))
          File "/home/leycec/py/beartype/beartype/_util/cache/utilcachecall.py", line 296, in _callable_cached
            raise exception
          File "/home/leycec/py/beartype/beartype/_util/cache/utilcachecall.py", line 289, in _callable_cached
            *args, **kwargs)
          File "<input>", line 13, in portend_low_level_winter
            EXCEPTION_PLACEHOLDER))
        beartype.roar.BeartypeDecorHintPepException: Random "Song of Fire and Ice" spoiler intimates that winter is coming.
    '''
    assert isinstance(exception, Exception), (
        f'{repr(exception)} not exception.')
    assert isinstance(source_str, str), f'{repr(source_str)} not string.'
    assert isinstance(target_str, str), f'{repr(target_str)} not string.'

    # If...
    if (
        # Exception arguments are a tuple (as is typically but not necessarily
        # the case) *AND*...
        isinstance(exception.args, tuple) and
        # This tuple is non-empty (as is typically but not necessarily the
        # case) *AND*...
        exception.args and
        # The first item of this tuple is a string providing this exception's
        # message (as is typically but not necessarily the case)...
        isinstance(exception.args[0], str)
    # Then this is a conventional exception. In this case...
    ):
        # Munged exception message globally replacing all instances of this
        # source substring with this target substring.
        #
        # Note that we intentionally call the lower-level str.replace() method
        # rather than the higher-level
        # beartype._util.text.utiltextmunge.replace_str_substrs() function
        # here, as the latter unnecessarily requires this exception message to
        # contain one or more instances of this source substring.
        exception_message = exception.args[0].replace(source_str, target_str)

        # If doing so actually changed this message...
        if exception_message != exception.args[0]:
            # Uppercase the first character of this message if needed.
            exception_message = uppercase_str_char_first(exception_message)

            # Reconstitute this exception argument tuple from this message.
            #
            # Note that if this tuple contains only this message, this slice
            # "exception.args[1:]" safely yields the empty tuple. Go, Python!
            exception.args = (exception_message,) + exception.args[1:]
        # Else, this message remains preserved as is.
    # Else, this is an unconventional exception. In this case, preserve this
    # exception as is.

    # Re-raise this exception while preserving its original traceback.
    raise exception.with_traceback(exception.__traceback__)
