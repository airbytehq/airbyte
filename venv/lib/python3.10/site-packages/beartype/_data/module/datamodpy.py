#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **standard Python module globals** (i.e., global constants
describing modules and packages bundled with CPython's standard library).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................

# ....................{ NAMES                              }....................
BUILTINS_MODULE_NAME = 'builtins'
'''
Fully-qualified name of the **builtins module** (i.e., objects defined by the
standard :mod:`builtins` module and thus globally available by default
*without* requiring explicit importation).
'''
