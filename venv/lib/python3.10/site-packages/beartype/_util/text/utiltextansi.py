# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **ANSI utilities** (i.e., low-level callables handling ANSI escape
sequences colouring arbitrary strings).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from re import compile as re_compile

# ....................{ CONSTANTS                          }....................
ANSI_RESET = '\033[0m'
'''
ANSI escape sequence resetting the effect of all prior ANSI sequence sequences,
effectively "undoing" all colors and styles applied by those sequences.
'''

# ....................{ CONSTANTS ~ color                  }....................
COLOR_GREEN = '\033[92m'
'''
ANSI escape sequence colouring all subsequent characters as green.
'''


COLOR_RED = '\033[31m'
'''
ANSI escape sequence colouring all subsequent characters as red.
'''


COLOR_BLUE = '\033[34m'
'''
ANSI escape sequence colouring all subsequent characters as blue.
'''


COLOR_YELLOW = '\033[33m'
'''
ANSI escape sequence colouring all subsequent characters as yellow.
'''

# ....................{ CONSTANTS ~ style                  }....................
STYLE_BOLD = '\033[1m'
'''
ANSI escape sequence stylizing all subsequent characters as bold.
'''

# ....................{ TESTERS                            }....................
def is_str_ansi(text: str) -> bool:
    '''
    :data:`True` only if the passed text contains one or more ANSI escape
    sequences.

    Parameters
    ----------
    text : str
        Text to be tested.

    Returns
    ----------
    bool
        :data:`True` only if this text contains one or more ANSI escape
        sequences.
    '''
    assert isinstance(text, str), f'{repr(text)} not string.'

    # Return true only this compiled regex matching ANSI escape sequences
    # returns a non-"None" match object when passed this text.
    return _ANSI_REGEX.search(text) is not None

# ....................{ STRIPPERS                          }....................
def strip_str_ansi(text: str) -> str:
    '''
    Strip *all* ANSI escape sequences from the passed string.

    Parameters
    ----------
    text : str
        Text to be stripped.

    Returns
    ----------
    str
        This text stripped of ANSI.
    '''
    assert isinstance(text, str), f'{repr(text)} not string.'

    # Glory be to the one liner that you are about to read.
    return _ANSI_REGEX.sub('', text)

# ....................{ PRIVATE ~ constants                }....................
_ANSI_REGEX = re_compile(r'\033\[[0-9;?]*[A-Za-z]')
'''
Compiled regular expression matching a single ANSI escape sequence.
'''
