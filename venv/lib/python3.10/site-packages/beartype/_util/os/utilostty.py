#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **TTY** (i.e., interactive terminal expected to be reasonably
POSIX-compliant, which even recent post-Windows 10 terminals now guarantee)
utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
import sys

# ....................{ TESTERS                            }....................
#FIXME: Unit test us up, please.
def is_stdout_terminal() -> bool:
    '''
    :data:`True` only if standard output is currently attached to a **TTY**
    (i.e., interactive terminal).

    If this tester returns :data:`True`, the TTY to which standard output is
    currently attached may be safely assumed to support **ANSI escape
    sequences** (i.e., POSIX-compliant colour codes). This assumption even holds
    under platforms that are otherwise *not* POSIX-compliant, including:

    * All popular terminals (including the stock Windows Terminal) and
      interactive development environments (IDEs) (including VSCode) bundled
      with Microsoft Windows, beginning at Windows 10.

    Caveats
    ----------
    **This tester is intentionally not memoized** (i.e., via the
    :func:`beartype._util.cache.utilcachecall.callable_cached` decorator), as
    external callers can and frequently do monkey-patch or otherwise modify the
    value of the global :attr:`sys.stdout` output stream.

    See Also
    ----------
    https://stackoverflow.com/questions/3818511/how-to-tell-if-python-script-is-being-run-in-a-terminal-or-via-gui
        StackOverflow thread strongly inspiring this implementation.
    '''
    # print(f'sys.stdout: {repr(sys.stdout)} [{type(sys.stdout)}]')
    # print(f'sys.stderr: {repr(sys.stderr)} [{type(sys.stderr)}]')

    # One-liners for great justice.
    #
    # Note that:
    # * Input and output streams are *NOT* guaranteed to define the isatty()
    #   method. For safety, we defensively test for the existence of that method
    #   before deferring to that method.
    # * All popular terminals under Windows >= 10 -- including terminals bundled
    #   out-of-the-box with Windows -- now support ANSII escape sequences. Since
    #   older Windows versions are compelling security risks and thus ignorable
    #   for contemporary purposes, Windows no longer needs to be excluded from
    #   ANSII-based colourization. All praise Satya Nadella. \o/
    return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    # return hasattr(sys.stdin, 'isatty') and sys.stdin.isatty()
    # return hasattr(sys.stderr, 'isatty') and sys.stderr.isatty()
