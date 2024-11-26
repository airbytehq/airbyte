#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **import hook state** (i.e., data class singletons safely centralizing
*all* global state maintained by beartype import hooks, enabling each external
unit test in our test suite to trivially reset that state after completion of
that test).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.claw._importlib.clawimpcache import ModuleNameToBeartypeConf
from beartype.claw._pkg.clawpkgtrie import PackagesTrie
from beartype.typing import Optional
from beartype._data.hint.datahinttyping import ImportPathHook
from threading import RLock

# ....................{ CLASSES                            }....................
class BeartypeClawState(object):
    '''
    **Beartype import hook state** (i.e., non-thread-safe singleton safely
    centralizing global state maintained by beartype import hooks, enabling each
    external unit test in our test suite to trivially reset that state after
    completion of that test).

    Attributes
    ----------
    beartype_pathhook : Optional[ImportPathHook]
        Either:

        * If the
          :func:`beartype.claw._importlib.clawimppath.add_beartype_pathhook`
          function has been previously called at least once under the active
          Python interpreter and the
          :func:`beartype.claw._importlib.clawimppath.add_beartype_pathhook`
          function has not been called more recently, the **Beartype import path
          hook singleton** (i.e., factory closure creating and returning a new
          :class:`importlib.machinery.FileFinder` instance itself creating and
          leveraging a new :class:`.BeartypeSourceFileLoader` instance).
        * Else, :data:`None` otherwise.

        Initialized to :data:`None`.
    module_name_to_beartype_conf : ModuleNameToBeartypeConf
        **Hooked module beartype configuration cache** (i.e., non-thread-safe
        dictionary mapping from the fully-qualified name of each previously
        imported submodule of each package previously registered in our global
        package trie to the beartype configuration configuring type-checking by
        the :func:`beartype.beartype` decorator of that submodule).
    packages_trie : PackagesTrie
        **Package configuration trie** (i.e., non-thread-safe recursively nested
        dictionary implementing a prefix tree such that each key-value pair maps
        from the unqualified basename of each subpackage to be type-checked on
        the first importation of that subpackage to another instance of the
        :class:`.PackagesTrie` class similarly describing the sub-subpackages of
        that subpackage).
    '''

    # ..................{ CLASS VARIABLES                    }..................
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # CAUTION: Subclasses declaring uniquely subclass-specific instance
    # variables *MUST* additionally slot those variables. Subclasses violating
    # this constraint will be usable but unslotted, which defeats our purposes.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently called
    # cache dunder methods. Slotting has been shown to reduce read and write
    # costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        'beartype_pathhook',
        'module_name_to_beartype_conf',
        'packages_trie',
    )

    # ....................{ INITIALIZERS                   }....................
    def __init__(self) -> None:

        # Nullify the proper subset of instance variables requiring
        # nullification *BEFORE* reinitializing this singleton.
        self.beartype_pathhook: Optional[ImportPathHook] = None

        # Reinitialize this singleton safely.
        self._reinit_safe()


    def _reinit_safe(self) -> None:
        '''
        Reinitialize *all* beartype import hook state encapsulated by this data
        class back to its initial defaults, trivially clearing *all* metadata
        pertaining to previously hooked packages and configurations installed by
        previously called beartype import hooks.

        This method performs the subset of reinitialization that is safe to be
        called from the :meth:`__init__` method.
        '''

        # One one-liner to reinitialize them all.
        self.module_name_to_beartype_conf = ModuleNameToBeartypeConf()
        self.packages_trie = PackagesTrie(package_basename=None)


    def reinit(self) -> None:
        '''
        Reinitialize *all* beartype import hook state encapsulated by this data
        class back to its initial defaults, trivially clearing *all* metadata
        pertaining to previously hooked packages and configurations installed by
        previously called beartype import hooks.
        '''

        # Avoid circular import dependencies.
        from beartype.claw._importlib.clawimppath import (
            remove_beartype_pathhook)

        # Perform the subset of reinitialization that is safe to be called from
        # the __init__() method.
        self._reinit_safe()

        # Perform the remainder of reinitialization that is unsafe to be called
        # from the __init__() method.
        #
        # Remove our beartype import path hook if this path hook has already
        # been added (e.g., by a prior call to an import hook) *OR* silently
        # reduce to a noop otherwise.
        remove_beartype_pathhook()

    # ..................{ DUNDERS                            }..................
    def __repr__(self) -> str:

        return '\n'.join((
            f'{self.__class__.__name__}(',
            f'    beartype_pathhook={repr(self.beartype_pathhook)},',
            f'    packages_trie={repr(self.packages_trie)},',
            f'    module_name_to_beartype_conf={self.module_name_to_beartype_conf},',
            f')',
        ))

# ....................{ GLOBALS                            }....................
claw_lock = RLock()
'''
Reentrant reusable thread-safe context manager gating access to the otherwise
non-thread-safe :data:`.claw_state` global.
'''


claw_state = BeartypeClawState()
'''
**Beartype import hook state** (i.e., non-thread-safe singleton safely
centralizing *all* global state maintained by beartype import hooks, enabling
each external unit test in our test suite to trivially reset that state after
completion of that test).
'''
