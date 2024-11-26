#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **string singletons** (i.e., strings and data structures of strings
commonly required throughout this codebase, reducing space and time consumption
by preallocating widely used string-centric objects).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from string import punctuation

# ....................{ SETS ~ punctuation                 }....................
CHARS_PUNCTUATION = frozenset(punctuation)
'''
Frozen set of all **ASCII punctuation characters** (i.e., non-Unicode
characters satisfying the conventional definition of English punctuation).

Note that the :attr:`string.punctuation` object is actually an inefficient
string of these characters rather than an efficient collection. Ergo, this set
should *ALWAYS* be accessed in lieu of that string.
'''
