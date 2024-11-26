#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **typing module globals** (i.e., global constants describing
quasi-standard typing modules).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................

# ....................{ SETS                               }....................
TYPING_MODULE_NAMES_STANDARD = frozenset((
    # Official typing module bundled with the Python stdlib.
    'typing',
    # Third-party typing compatibility layer bundled with @beartype itself.
    'beartype.typing',
))
'''
Frozen set of the fully-qualified names of all **standard typing modules**
(i.e., modules whose public APIs *exactly* conform to that of the standard
:mod:`typing` module).

This set includes both the standard :mod:`typing` module and comparatively
more standard :mod:`beartype.typing` submodule while excluding the third-party
:mod:`typing_extensions` module, whose runtime behaviour often significantly
diverges in non-standard fashion from that of the aforementioned modules.
'''


TYPING_MODULE_NAMES = TYPING_MODULE_NAMES_STANDARD | frozenset((
    # Third-party module backporting "typing" attributes introduced in newer
    # Python versions to older Python versions.
    'typing_extensions',
))
'''
Frozen set of the fully-qualified names of all **quasi-standard typing
modules** (i.e., modules defining attributes usable for creating PEP-compliant
type hints accepted by both static and runtime type checkers).
'''


TYPING_MODULE_NAMES_DOTTED = frozenset(
    f'{typing_module_name}.' for typing_module_name in TYPING_MODULE_NAMES)
'''
Frozen set of the fully-qualified ``.``-suffixed names of all typing modules.

This set is a negligible optimization enabling callers to perform slightly more
efficient testing of string prefixes against items of this specialized set than
those of the more general-purpose :data:`TYPING_MODULE_NAMES` set.

See Also
----------
:data:`TYPING_MODULE_NAMES`
    Further details.
'''
