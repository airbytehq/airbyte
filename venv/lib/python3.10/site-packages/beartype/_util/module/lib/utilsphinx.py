#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **Sphinx** utilities (i.e., callables handling the third-party
:mod:`sphinx` package as an optional runtime dependency of this project).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To prevent this project from accidentally requiring third-party
# packages as mandatory runtime dependencies, avoid importing from *ANY* such
# package via a module-scoped import. These imports should be isolated to the
# bodies of callables declared below.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype._util.func.utilfuncframe import iter_frames
from sys import modules as module_imported_names

# ....................{ PRIVATE ~ magic                    }....................
_SPHINX_AUTODOC_SUBPACKAGE_NAME = 'sphinx.ext.autodoc'
'''
Fully-qualified name of the subpackage providing the ``autodoc`` extension
bundled with Sphinx.
'''

# ....................{ TESTERS                            }....................
def is_sphinx_autodocing() -> bool:
    '''
    ``True`` only if Sphinx is currently **autogenerating documentation**
    (i.e., if this function has been called from a Python call stack invoked by
    the ``autodoc`` extension bundled with the optional third-party build-time
    :mod:`sphinx` package).
    '''

    # If the "autodoc" extension has *NOT* been imported, Sphinx by definition
    # *CANNOT* be autogenerating documentation. In this case, return false.
    #
    # Note this technically constitutes an optional (albeit pragmatically
    # critical) optimization. This test is O(1) with negligible constants,
    # whereas the additional test below is O(n) with non-negligible constants.
    # Ergo, this efficient test short-circuits the inefficient test below.
    if _SPHINX_AUTODOC_SUBPACKAGE_NAME not in module_imported_names:
        return False
    # Else, the "autodoc" extension has been imported. Since this does *NOT*
    # conclusively imply that Sphinx is currently autogenerating documentation,
    # further testing is required to avoid returning false positives (and thus
    # erroneously reducing @beartype to a noop, which would be horrifying).
    #
    # Specifically, we iteratively search up the call stack for a stack frame
    # originating from the "autodoc" extension. If we find such a stack frame,
    # Sphinx is currently autogenerating documentation; else, Sphinx is not.

    #FIXME: Refactor this to leverage a genuinely valid working solution
    #hopefully provided out-of-the-box by some hypothetical new bleeding-edge
    #version of Sphinx *AFTER* they resolve our feature request for this:
    #    https://github.com/sphinx-doc/sphinx/issues/9805

    # For each stack frame on the call stack, ignoring the stack frame
    # encapsulating the call to this tester...
    for frame in iter_frames(func_stack_frames_ignore=1):
        # Fully-qualified name of this scope's module if this scope defines
        # this name *OR* "None" otherwise.
        frame_module_name = frame.f_globals.get('__name__')
        # print(f'Visiting frame (module: "{func_frame_module_name}")...')

        # If this scope's module is the "autodoc" extension, Sphinx is
        # currently autogenerating documentation. In this case, return true.
        if (
            frame_module_name and
            frame_module_name.startswith(_SPHINX_AUTODOC_SUBPACKAGE_NAME)
        ):
            return True
        # Else, this scope's module is *NOT* the "autodoc" extension.

    # Else, *NO* scope's module is the "autodoc" extension. Return false.
    return False
