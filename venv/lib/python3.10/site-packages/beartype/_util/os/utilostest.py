#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **platform tester** (i.e., functions detecting the current
platform the active Python interpreter is running under) utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._util.cache.utilcachecall import callable_cached
from platform import system as platform_system
from sys import platform as sys_platform

# ....................{ TESTERS                            }....................
@callable_cached
def is_os_linux() -> bool:
    '''
    ``True`` only if the current platform is a **Linux distribution.**

    This tester is memoized for efficiency.
    '''

    return platform_system() == 'Linux'



@callable_cached
def is_os_macos() -> bool:
    '''
    ``True`` only if the current platform is **Apple macOS**, the operating
    system previously known as "OS X."

    This tester is memoized for efficiency.
    '''

    return platform_system() == 'Darwin'


@callable_cached
def is_os_windows_vanilla() -> bool:
    '''
    ``True`` only if the current platform is **vanilla Microsoft Windows**
    (i.e., *not* running the Cygwin POSIX compatibility layer).

    This tester is memoized for efficiency.
    '''

    return sys_platform == 'win32'
