#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **magic strings** (i.e., globally applicable string constants).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ CODE ~ indent                      }....................
CODE_INDENT_1 = '    '
'''
PEP-agnostic code snippet expanding to a single level of indentation.
'''


CODE_INDENT_2 = CODE_INDENT_1*2
'''
PEP-agnostic code snippet expanding to two levels of indentation.
'''


CODE_INDENT_3 = CODE_INDENT_2 + CODE_INDENT_1
'''
PEP-agnostic code snippet expanding to three levels of indentation.
'''

# ....................{ CODE ~ operator                    }....................
LINE_RSTRIP_INDEX_AND = -len(' and')
'''
Negative index relative to the end of any arbitrary newline-delimited Python
code string suffixed by the boolean operator ``" and"`` required to strip that
suffix from that substring.
'''


LINE_RSTRIP_INDEX_OR = -len(' or')
'''
Negative index relative to the end of any arbitrary newline-delimited Python
code string suffixed by the boolean operator ``" or"`` required to strip that
suffix from that substring.
'''
