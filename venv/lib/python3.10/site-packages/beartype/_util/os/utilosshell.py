#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **shell** (i.e., external low-level command-line environment
encapsulating the active Python interpreter as a parent process of this
interpreter) utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from os import environ

# ....................{ TESTERS                            }....................
get_shell_var_value_or_none = environ.get
'''
String value of the shell environment variable with the passed name if the
parent shell defines this variable *or* :data:`None` otherwise (i.e., if the
parent shell does *not* define this variable).

Caveats
----------
**This getter is a human-readable alias of the comparable**
:func:`os.getenv` **function and** :meth:`os.environ.get` **method.** This
getter exists only for disambiguity and clarity. This getter is *not* an alias
of the :meth:`os.environ.__getitem__` dunder method, which raises a
:exc:`KeyError` exception rather than returns :data:`None` if the parent shell
does *not* define this variable.

See Also
----------
https://stackoverflow.com/a/41626355/2809027
    StackOverflow answer strongly inspiring this alias.
'''
