#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype decorator **type-checking expression magic** (i.e., global string
constants embedded in the implementations of boolean expressions type-checking
arbitrary objects against arbitrary PEP-compliant type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._util.error.utilerror import EXCEPTION_PLACEHOLDER
from itertools import count

# ....................{ EXCEPTION                          }....................
EXCEPTION_PREFIX_FUNC_WRAPPER_LOCAL = (
    f'{EXCEPTION_PLACEHOLDER}wrapper parameter ')
'''
Human-readable substring describing a new wrapper parameter required by the
current root type hint in exception messages.
'''


EXCEPTION_PREFIX_HINT = f'{EXCEPTION_PLACEHOLDER}type hint '
'''
Human-readable substring describing the current root type hint generically
(i.e., agnostic of the specific PEP standard to which this hint conforms) in
exception messages.
'''

# ....................{ HINT ~ meta                        }....................
# Iterator yielding the next integer incrementation starting at 0, to be safely
# deleted *AFTER* defining the following 0-based indices via this iterator.
__hint_meta_index_counter = count(start=0, step=1)


HINT_META_INDEX_HINT = next(__hint_meta_index_counter)
'''
0-based index into each tuple of hint metadata providing the currently
visited hint.

For both space and time efficiency, this metadata is intentionally stored as
0-based integer indices of an unnamed tuple rather than:

* Human-readable fields of a named tuple, which incurs space and time costs we
  would rather *not* pay.
* 0-based integer indices of a tiny fixed list. Previously, this metadata was
  actually stored as a fixed list. However, exhaustive profiling demonstrated
  that reinitializing each such list by slice-assigning that list's items from
  a tuple to be faster than individually assigning these items:

  .. code-block:: shell-session

     $ echo 'Slice w/ tuple:' && command python3 -m timeit -s \
          'muh_list = ["a", "b", "c", "d",]' \
          'muh_list[:] = ("e", "f", "g", "h",)'
     Slice w/ tuple:
     2000000 loops, best of 5: 131 nsec per loop
     $ echo 'Slice w/o tuple:' && command python3 -m timeit -s \
          'muh_list = ["a", "b", "c", "d",]' \
          'muh_list[:] = "e", "f", "g", "h"'
     Slice w/o tuple:
     2000000 loops, best of 5: 138 nsec per loop
     $ echo 'Separate:' && command python3 -m timeit -s \
          'muh_list = ["a", "b", "c", "d",]' \
          'muh_list[0] = "e"
     muh_list[1] = "f"
     muh_list[2] = "g"
     muh_list[3] = "h"'
     Separate:
     2000000 loops, best of 5: 199 nsec per loop

So, not only does there exist no performance benefit to flattened fixed lists,
there exists demonstrable performance costs.
'''


HINT_META_INDEX_PLACEHOLDER = next(__hint_meta_index_counter)
'''
0-based index into each tuple of hint metadata providing the **current
placeholder type-checking substring** (i.e., placeholder to be globally
replaced by a Python code snippet type-checking the current pith expression
against the hint described by this metadata on visiting that hint).

This substring provides indirection enabling the currently visited parent hint
to defer and delegate the generation of code type-checking each child argument
of that hint to the later time at which that child argument is visited.

Example
----------
For example, the
:func:`beartype._decor._hint._pep._pephint.make_func_wrapper_code` function might
generate intermediary code resembling the following on visiting the
:data:`Union` parent of a ``Union[int, str]`` object *before* visiting either
the :class:`int` or :class:`str` children of that object:

    if not (
        @{0}! or
        @{1}!
    ):
        raise get_beartype_violation(
            func=__beartype_func,
            pith_name=$%PITH_ROOT_NAME/~,
            pith_value=__beartype_pith_root,
        )

Note the unique substrings ``"@{0}!"`` and ``"@{1}!"`` in that code, which that
function iteratively replaces with code type-checking each of the child
arguments of that :data:`Union` parent (i.e., :class:`int`, :class:`str`). The
final code memoized by that function might then resemble:

    if not (
        isinstance(__beartype_pith_root, int) or
        isinstance(__beartype_pith_root, str)
    ):
        raise get_beartype_violation(
            func=__beartype_func,
            pith_name=$%PITH_ROOT_NAME/~,
            pith_value=__beartype_pith_root,
        )
'''


HINT_META_INDEX_PITH_EXPR = next(__hint_meta_index_counter)
'''
0-based index into each tuple of hint metadata providing the **current
pith expression** (i.e., Python code snippet evaluating to the current possibly
nested object of the passed parameter or return value to be type-checked
against the currently visited hint).
'''


HINT_META_INDEX_PITH_VAR_NAME = next(__hint_meta_index_counter)
'''
0-based index into each tuple of hint metadata providing the **current pith
variable name** (i.e., name of the unique local variable assigned the value of
the current pith either by a prior assignment statement or expression).
'''


HINT_META_INDEX_INDENT = next(__hint_meta_index_counter)
'''
0-based index into each tuple of hint metadata providing **current
indentation** (i.e., Python code snippet expanding to the current level of
indentation appropriate for the currently visited hint).
'''

# Delete the above counter for safety and sanity in equal measure.
del __hint_meta_index_counter
