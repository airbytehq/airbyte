# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype exception message color utilities** (i.e., low-level callables
conditionally accenting type-checking violation messages with ANSI escape
sequences colouring those strings when configured to do so by the
:func:`beartype.beartype`-decorated callables raising those violations).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._conf.confcls import BeartypeConf
from beartype._util.os.utilostty import is_stdout_terminal
from beartype._util.text.utiltextansi import (
    ANSI_RESET,
    COLOR_GREEN,
    COLOR_RED,
    COLOR_BLUE,
    COLOR_YELLOW,
    STYLE_BOLD,
    strip_str_ansi,
)

# ....................{ COLOURIZERS                        }....................
def color_error(text: str) -> str:
    '''
    Colour the passed substring as an error.

    Parameters
    ----------
    text : str
        Text to be coloured as an error.

    Returns
    ----------
    str
        This text coloured as an error.
    '''

    assert isinstance(text, str), f'{repr(text)} not string.'

    return f'{STYLE_BOLD}{COLOR_RED}{text}{ANSI_RESET}'


def color_hint(text: str) -> str:
    '''
    Colour the passed substring as a PEP-compliant type hint.

    Parameters
    ----------
    text : str
        Text to be coloured as a type hint.

    Returns
    ----------
    str
        This text coloured as a type hint.
    '''
    assert isinstance(text, str), f'{repr(text)} not string.'

    return f'{STYLE_BOLD}{COLOR_BLUE}{text}{ANSI_RESET}'


def color_repr(text: str) -> str:
    '''
    Colour the passed substring as a **representation** (i.e., machine-readable
    string returned by the :func:`repr` builtin).

    Parameters
    ----------
    text : str
        Text to be coloured as a representation.

    Returns
    ----------
    str
        This text coloured as a representation.
    '''
    assert isinstance(text, str), f'{repr(text)} not string.'

    return f'{COLOR_YELLOW}{text}{ANSI_RESET}'


def color_type(text: str) -> str:
    '''
    Colour the passed substring as a simple class.

    Parameters
    ----------
    text : str
        Text to be coloured as a simple class.

    Returns
    ----------
    str
        This text coloured as a simple class.
    '''
    assert isinstance(text, str), f'{repr(text)} not string.'

    return f'{STYLE_BOLD}{COLOR_GREEN}{text}{ANSI_RESET}'

# ....................{ STRIPPERS                          }....................
#FIXME: Unit test us up, please.
#FIXME: Inefficient and thus non-ideal. Since efficiency isn't a pressing
#concern in an exception raiser, this is more a matter of design purity than
#anything. Still, it would be preferable to avoid embedding ANSI escape
#sequences in the cause when the user requests that rather than forcibly
#stripping those sequences out after the fact via an inefficient regex. To do
#so, we'll want to:
#* Augment the color_*() family of functions with a mandatory "conf:
#  BeartypeConf" parameter.
#* Pass that parameter to *EVERY* call to one of those functions.
#* Refactor those functions to respect that parameter. The ideal means of
#  doing so would probably be define in the
#  "beartype._util.text.utiltextansi" submodule:
#  * A new "_BeartypeTheme" dataclass mapping from style names to format
#    strings embedding the ANSI escape sequences styling those styles.
#  * A new pair of private "_THEME_MONOCHROME" and "_THEME_PRISMATIC"
#    instances of that dataclass. The values of the "_THEME_MONOCHROME"
#    dictionary should all just be the default format string: e.g.,
#    _THEME_MONOCHROME = _BeartypeTheme(
#        format_error='{text}',
#        ...
#    )
#
#    _THEME_PRISMATIC = _BeartypeTheme(
#        format_error=f'{_STYLE_BOLD}{_COLOUR_RED}{{text}}{_COLOUR_RESET}',
#        ...
#    )
#  * A new "_THEME_DEFAULT" instance of that dataclass conditionally defined
#    as either "_THEME_MONOCHROME" or "_THEME_PRISMATIC" depending on
#    whether stdout is attached to a TTY or not. Alternately, to avoid
#    performing that somewhat expensive logic at module scope (and thus on
#    initial beartype importation), it might be preferable to instead define
#    a new cached private getter resembling:
#
#    @callable_cached
#    def _get_theme_default() -> _BeartypeTheme:
#        return (
#            _THEME_PRISMATIC
#            if is_stdout_terminal() else
#            _THEME_MONOCHROME
#        )
def strip_text_ansi_if_configured(text: str, conf: BeartypeConf) -> str:
    '''
    Strip all ANSI escape sequences from the passed string if the
    :attr:`BeartypeConf.is_color` instance variable of the passed beartype
    configuration instructs this function to do so.

    Specifically:

    * If ``conf.is_color is True``, this function silently reduces to a noop.
    * If ``conf.is_color is False``, this function unconditionally strips all
      ANSI escape sequences from this string.
    * If ``conf.is_color is None``, this function conditionally strips all
      ANSI escape sequences from this string only if standard output is
      currently attached to an interactive terminal.

    Parameters
    ----------
    text : str
        Text to be stripped of ANSI.
    conf : BeartypeConf
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all flags, options, settings, and other metadata configuring the
        current decoration of the decorated callable or class).

    Returns
    ----------
    str
        This text stripped of ANSI.
    '''
    assert isinstance(text, str), f'{repr(text)} not string.'
    assert isinstance(conf, BeartypeConf), f'{repr(conf)} not configuration.'

    # Return either...
    return (
        # This string with all ANSI stripped when this configuration instructs
        # this function to either...
        strip_str_ansi(text)
        if (
            # Unconditionally strip all ANSI from this string *OR*...
            # Conditionally strip all ANSI from this string only when standard
            # output is *NOT* attached to an interactive terminal;
            conf.is_color is False or
            (conf.is_color is None and not is_stdout_terminal())
        ) else
        # Else, this string unmodified.
        text
    )
