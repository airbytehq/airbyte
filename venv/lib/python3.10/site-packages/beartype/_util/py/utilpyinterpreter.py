#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **Python interpreter** utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import (
    _BeartypeUtilPythonInterpreterException,
)
from beartype._data.hint.datahinttyping import CommandWords
from beartype._util.cache.utilcachecall import callable_cached
from platform import python_implementation
from sys import executable as sys_executable

# ....................{ TESTERS                            }....................
@callable_cached
def is_py_pypy() -> bool:
    '''
    :data:`True` only if the active Python interpreter is **PyPy**.

    This tester is memoized for efficiency.
    '''

    return python_implementation() == 'PyPy'

# ....................{ GETTERS ~ path                     }....................
@callable_cached
def get_interpreter_command_words() -> CommandWords:
    '''
    **Active Python interpreter command words** (i.e., iterable of one or more
    shell words unambiguously running the executable binary for this interpreter
    and machine architecture).

    This getter is memoized for efficiency.

    Caveats
    ----------
    **This high-level getter should always be called in lieu of the low-level**
    :func:`.get_interpreter_filename` **getter** when attempting to rerun this
    interpreter as a subprocess of the active Python process. Why? Because the
    absolute filename of the executable binary for this interpreter is
    insufficient to unambiguously run this binary under edge cases, including:

    * **macOS.** Under macOS, the executable binary for this interpreter may be
      bundled with one or more other executable binaries targeting different
      machine architectures (e.g., 32-bit, 64-bit) in a single so-called
      "universal binary." Distinguishing between these bundled binaries requires
      passing this interpreter to a prefixing macOS-specific command: ``arch``.

    Returns
    ----------
    CommandWords
        Iterable of one or more shell words unambiguously running this binary.
    '''

    #FIXME: Uncomment if required. Although this was certainly required a decade
    #ago, it's unclear whether this is still required; indeed, given the
    #increased prevalence of Apple Silicon, it seems likely that an entirely
    #different macOS-specific prefix might be required now. Thus, I sigh. *sigh*
    # # Avoid circular import dependencies.
    # from beartype._util.os.utilostest import is_os_macos
    #
    # # List of such shell words.
    # command_words = None  # type: ignore[assignment]
    #
    # # If the current platform is macOS, this interpreter is only unambiguously runnable via the
    # # macOS-specific "arch" command. In this case...
    # if is_os_macos():
    #     # Run the "arch" command.
    #     command_words = ['arch']
    #
    #     # Instruct this command to run the architecture-specific binary in
    #     # Python's universal binary corresponding to the current architecture.
    #     if is_wordsize_64():
    #         command_words.append('-i386')
    #     else:
    #         command_words.append('-x86_64')
    #
    #     # Instruct this command, lastly, to run this interpreter.
    #     command_words.append(get_interpreter_filename())
    # # Else, this interpreter is unambiguously runnable as is.
    # else:
    #     command_words = [get_interpreter_filename()]

    # Iterable of all interpreter shell words to be returned.
    command_words = (get_interpreter_filename(),)

    # Return this iterable.
    return command_words


@callable_cached
def get_interpreter_filename() -> str:
    '''
    Absolute filename of the executable binary underlying the active Python
    interpreter if Python provides this filename *or* raise an exception
    otherwise (i.e., if Python refuses to provide this filename, typically due
    to this filename being embedded in a frozen bundle of some sort).

    This getter is memoized for efficiency.

    Raises
    ----------
    _BeartypeUtilPathException
        If Python successfully queried this filename but no such file exists.
    _BeartypeUtilPythonInterpreterException
        If Python failed to query this filename.

    Returns
    ----------
    str
        Absolute filename of this binary.
    '''

    # Avoid circular import dependencies.
    from beartype._util.path.utilpathtest import die_unless_file_executable

    # If Python refuses to provide this filename, raise an exception.
    #
    # Note that this test intentionally matches both the empty string and
    # "None", as the official documentation for "sys.executable" states:
    #     If Python is unable to retrieve the real path to its executable,
    #     sys.executable will be an empty string or None.
    if not sys_executable:
        raise _BeartypeUtilPythonInterpreterException(
            'Absolute filename of active Python interpreter not found.')
    # Else, Python provides this filename.

    # If this file is *NOT* executable, raise an exception.
    die_unless_file_executable(sys_executable)
    # Else, this file is executable.

    # Return this filename.
    return sys_executable
