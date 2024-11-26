#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype import path hook trie** (i.e., data structure caching package names
on behalf of the higher-level :func:`beartype.claw._clawmain` submodule, which
beartype import path hooks internally created by that submodule subsequently
lookup when deciding whether or not (and how) to decorate by
:func:`beartype.beartype` the currently imported user-specific submodule).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.claw._importlib.clawimppath import remove_beartype_pathhook
from beartype.typing import (
    Dict,
    Iterable,
    # Iterator,
    Optional,
)
from beartype._cave._cavemap import NoneTypeOr
from beartype._conf.confcls import BeartypeConf
# from pprint import pformat

# ....................{ CLASSES                            }....................
#FIXME: Unit test us up, please.
class PackagesTrie(
    #FIXME: Use "beartype.typing.Self" here instead once we backport that.
    Dict[str, Optional['PackagesTrie']]):
    '''
    **(Sub)package configuration (sub)trie** (i.e., recursively nested
    dictionary mapping from the unqualified basename of each subpackage of the
    current package to be runtime type-checked on the first importation of that
    subpackage to another instance of this class similarly describing the
    sub-subpackages of that subpackage).

    This (sub)cache is suitable for caching as the values of:

    * The :data:`.packages_trie` global dictionary.
    * Each (sub)value mapped to by that global dictionary.

    Motivation
    ----------
    This dictionary is intentionally implemented as a nested trie data structure
    rather than a trivial non-nested flat dictionary. Why? Efficiency. Consider
    this flattened set of package names:

        .. code-block:: python

           package_names = {'a.b', 'a.c', 'd'}

    Deciding whether an arbitrary package name is in this set requires
    worst-case ``O(n)`` iteration across the set of ``n`` package names.

    Consider instead this nested dictionary whose keys are package names split
    on ``"."`` delimiters and whose values are either recursively nested
    dictionaries of the same format *or* the :data:`None` singleton (terminating
    the current package name):

        .. code-block:: python

           package_names_trie = {'a': {'b': None, 'c': None}, 'd': None}

    Deciding whether an arbitrary package name is in this dictionary only
    requires worst-case ``O(h)`` iteration across the height ``h`` of this
    dictionary (equivalent to the largest number of ``"."`` delimiters for any
    fully-qualified package name encapsulated by this dictionary). ``h <<<< n``,
    so this dictionary offers *much* faster worst-case lookup than that set.

    Moreover, in the worst case:

    * That set requires one inefficient string prefix test for each item.
    * This dictionary requires *only* one efficient string equality test for
      each nested key-value pair while descending towards the target package
      name.

    Let's do this, fam.

    Caveats
    ----------
    **This dictionary is only safely accessible in a thread-safe manner from
    within a** ``with claw_lock:`` **context manager.** Equivalently, this
    dictionary is *not* safely accessible outside that manager.

    Examples
    ----------
    An example instance of this dictionary hooked on submodules of the root
    ``package_z`` package, the child ``package_a.subpackage_k`` submodule, and
    the ``package_a.subpackage_b.subpackage_c`` and
    ``package_a.subpackage_b.subpackage_d`` submodules:

        >>> packages_trie = PackagesTrie({
        ...     'package_a': PackagesTrie({
        ...         'subpackage_b': PackagesTrie({
        ...             'subpackage_c': None,
        ...             'subpackage_d': None,
        ...         }),
        ...         'subpackage_k': None,
        ...     }),
        ...     'package_z': None,
        ... })

    Attributes
    ----------
    conf_if_hooked : Optional[BeartypeConf]
        Either:

        * If this (sub)package has been explicitly registered by a prior call to
          the :func:`add_package_names` function, the **beartype
          configuration** (i.e., dataclass encapsulating all settings
          configuring type-checking for this (sub)package).
        * Else, :data:`None`.
    package_basename : Optional[str]
        Either:

        * If this (sub)trie is the global trie :data:`.packages_trie`,
          :data:`None`.
        * Else, the unqualified basename of the (sub)package configured by this
          (sub)trie.
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
        'package_basename',
        'conf_if_hooked',
    )

    # ..................{ INITIALIZERS                       }..................
    def __init__(
        self,
        package_basename : Optional[str],
        *args, **kwargs
    ) -> None:
        '''
        Initialize this package name (sub)cache.

        Parameters
        ----------
        basename : Optional[str]
            Either:

            * If this (sub)trie is the global trie :data:`.packages_trie`,
              :data:`None`.
            * Else, the unqualified basename of the (sub)package configured by
              this (sub)trie.

        All remaining passed parameters are passed as is to the superclass
        :meth:`dict.__init__` method.
        '''
        assert isinstance(package_basename, NoneTypeOr[str]), (
            f'{repr(package_basename)} neither string nor "None".')

        # Initialize our superclass with all passed parameters.
        super().__init__(*args, **kwargs)

        # Classify all remaining passed parameters.
        self.package_basename = package_basename

        # Nullify all subclass-specific parameters for safety.
        self.conf_if_hooked: Optional[BeartypeConf] = None

    # ..................{ DUNDERS                            }..................
    def __repr__(self) -> str:

        return '\n'.join((
            f'{self.__class__.__name__}(',
            f'    package_basename={repr(self.package_basename)},',
            f'    conf_if_hooked={repr(self.conf_if_hooked)},',
            f'    dict={super().__repr__()},',
            f')',
        ))

# ....................{ TESTERS                            }....................
#FIXME: Unit test us up, please.
def is_packages_trie() -> bool:
    '''
    :data:`True` only if one or more packages have been registered by a prior
    call to the :func:`beartype.claw._pkg.clawpkghook.hook_packages` function.

    Returns
    ----------
    bool
        :data:`True` only if one or more packages have been registered.
    '''

    # Avoid circular import dependencies.
    from beartype.claw._clawstate import claw_state

    # Return true only if either...
    return (
        # A global configuration has been added by a prior call to the public
        # beartype.claw.beartype_all() function *OR*...
        claw_state.packages_trie.conf_if_hooked is not None or
        # One or more package-specific configurations have been added by prior
        # calls to public beartype.claw.beartype_*() functions.
        bool(claw_state.packages_trie)
    )

# ....................{ GETTERS                            }....................
#FIXME: Unit test us up, please.
def get_package_conf_or_none(package_name: str) -> Optional[BeartypeConf]:
    '''
    Beartype configuration with which to type-check the package with the passed
    name if that package *or* a parent package of that package was registered by
    a prior call to the :func:`.hook_packages` function *or* :data:`None`
    otherwise (i.e., if neither that package *nor* a parent package of that
    package was registered by such a call).

    Parameters
    ----------
    package_name : str
        Fully-qualified name of the package to be inspected.

    Returns
    ----------
    Optional[BeartypeConf]
        Either:

        * If that package or a parent package of that package was registered by
          a prior call to the :func:`.hook_packages` function, the beartype
          configuration with which to type-check that package.
        * Else, :data:`None`.
    '''

    # Avoid circular import dependencies.
    from beartype.claw._clawstate import claw_state

    # Beartype configuration registered for the currently iterated package,
    # defaulting to the beartype configuration registered for the global trie
    # applicable to *ALL* packages if an external caller previously called the
    # public beartype.claw.beartype_all() function *OR* "None" otherwise (i.e.,
    # if that function has yet to be called).
    subpackage_conf = claw_state.packages_trie.conf_if_hooked

    # For each subpackages trie describing each parent package transitively
    # containing this package (as well as that of that package itself)...
    for subpackages_trie in iter_packages_trie(package_name):
        # Beartype configuration registered with either...
        subpackage_conf = (
            # That parent package if any *OR*...
            #
            # Since that parent package is more granular (i.e., unique) than
            # any transitive parent package of that parent package, the
            # former takes precedence over the latter when defined.
            subpackages_trie.conf_if_hooked or
            # A transitive parent package of that parent package if any.
            subpackage_conf
        )

    # Return this beartype configuration if any *OR* "None" otherwise.
    return subpackage_conf

# ....................{ ITERATORS                          }....................
#FIXME: Unit test us up, please.
def iter_packages_trie(package_name: str) -> Iterable[PackagesTrie]:
    '''
    Generator iteratively yielding one **(sub)package configuration (sub)trie**
    (i.e., :class:`PackagesTrie` instance) describing each transitive parent
    package of the package with the passed name if that package *or* a parent
    package of that package was registered by a prior call to the
    :func:`beartype.claw._pkg.clawpkghook..hook_packages` function *or* the
    empty iterable otherwise otherwise (i.e., if neither that package *nor* a
    parent package of that package was registered by such a call).

    Specifically, this generator yields (in order):

    #. The subtrie of that trie configuring the root package of the passed
       (sub)package.
    #. And so on, until eventually yielding...
    #. The subsubtrie of that subtrie configuring the passed (sub)package
       itself.

    This generator intentionally avoids yielding the global trie
    :data:`.packages_trie`, which is already accessible via that global.

    Parameters
    ----------
    package_name : str
        Fully-qualified name of the package to be inspected.

    Yields
    ----------
    PackagesTrie
        (Sub)package configuration (sub)trie describing the currently iterated
        transitive parent package of the package with this name.
    '''
    assert isinstance(package_name, str), f'{repr(package_name)} not string.'

    # Avoid circular import dependencies.
    from beartype.claw._clawstate import (
        claw_lock,
        claw_state,
    )

    # List of each unqualified basename comprising this name, split from this
    # fully-qualified name on "." delimiters. Note that the "str.split('.')" and
    # "str.rsplit('.')" calls produce the exact same lists under all possible
    # edge cases. We arbitrarily call the former rather than the latter for
    # simplicity and readability.
    package_basenames = package_name.split('.')

    # With a submodule-specific thread-safe reentrant lock...
    with claw_lock:
        # Current subtrie of the global trie describing the currently iterated
        # basename of this package, initialized to this global trie itself.
        subpackages_trie: Optional[PackagesTrie] = claw_state.packages_trie

        # For each unqualified basename of each parent package transitively
        # containing this package (as well as that of that package itself)...
        for package_basename in package_basenames:
            # Current subtrie of that trie describing that parent package if
            # that parent package was registered by a prior call to the
            # hook_packages() function *OR* "None" otherwise (i.e., if that
            # parent package has yet to be registered).
            subpackages_trie = subpackages_trie.get(package_basename)  # type: ignore[union-attr]

            # If that parent package has yet to be registered, halt iteration.
            if subpackages_trie is None:
                break
            # Else, that parent package was previously registered.

            # Yield the current subtrie describing that parent package.
            yield subpackages_trie

# ....................{ REMOVERS                           }....................
#FIXME: Unit test us up, please.
def remove_beartype_pathhook_unless_packages_trie() -> None:
    '''
    Remove our **beartype import path hook singleton** (i.e., single callable
    guaranteed to be inserted at most once to the front of the standard
    :mod:`sys.path_hooks` list recursively applying the
    :func:`beartype.beartype` decorator to all well-typed callables and classes
    defined by all submodules of all packages previously registered by a call to
    a public :func:`beartype.claw` function) if this path hook has already been
    added and all previously registered packages have been unregistered *or*
    silently reduce to a noop otherwise (i.e., if either this path hook has yet
    to be added or one or more packages are still registered).

    Caveats
    ----------
    **This function is non-thread-safe.** For both simplicity and efficiency,
    the caller is expected to provide thread-safety through a higher-level
    locking primitive managed by the caller.
    '''

    # If all previously registered packages have been unregistered, safely
    # remove our import path hook from the "sys.path_hooks" list.
    if not is_packages_trie():
        remove_beartype_pathhook()
