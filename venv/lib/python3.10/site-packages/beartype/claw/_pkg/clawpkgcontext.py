#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype import path hook context managers** (i.e., data structure caching package names
on behalf of the higher-level :func:`beartype.claw._clawmain` submodule, which
beartype import path hooks internally created by that submodule subsequently
lookup when deciding whether or not (and how) to decorate by
:func:`beartype.beartype` the currently imported user-specific submodule).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.claw._clawstate import (
    claw_lock,
    claw_state,
)
from beartype.claw._pkg.clawpkgtrie import (
    is_packages_trie,
    remove_beartype_pathhook_unless_packages_trie,
)
from beartype.typing import (
    Iterator,
    Optional,
)
from beartype._conf.confcls import (
    BEARTYPE_CONF_DEFAULT,
    BeartypeConf,
)
from contextlib import contextmanager

# ....................{ CONTEXTS                           }....................
#FIXME: Unit test us up, please.
@contextmanager
def beartyping(
    # Optional keyword-only parameters.
    *,
    conf: BeartypeConf = BEARTYPE_CONF_DEFAULT,
) -> Iterator[None]:
    '''
    Context manager temporarily registering a new **universal beartype import
    path hook** (i.e., callable inserted to the front of the standard
    :mod:`sys.path_hooks` list recursively decorating *all* typed callables and
    classes of *all* submodules of *all* packages on the first importation of
    those submodules with the :func:`beartype.beartype` decorator, wrapping
    those callables and classes with performant runtime type-checking).

    Specifically, this context manager (in order):

    #. Temporarily registers this hook by calling the public
       :func:`beartype.claw.beartype_all` function.
    #. Runs the body of the caller-defined ``with beartyping(...):`` block.
    #. Unregisters the hook registered by the prior call to that function.

    This context manager is thread-safe.

    Parameters
    ----------
    conf : BeartypeConf, optional
        **Beartype configuration** (i.e., dataclass configuring the
        :mod:`beartype.beartype` decorator for *all* decoratable objects
        recursively decorated by the path hook added by this function).
        Defaults to ``BeartypeConf()``, the default ``O(1)`` configuration.

    Yields
    ----------
    None
        This context manager yields *no* objects.

    Raises
    ----------
    BeartypeClawHookException
        If the passed ``conf`` parameter is *not* a beartype configuration
        (i.e., :class:`BeartypeConf` instance).

    See Also
    ----------
    :func:`beartype.claw.beartype_all`
        Arguably unsafer alternative to this function globalizing the effect of
        this function to *all* imports performed anywhere.
    '''

    # Avoid circular import dependencies.
    from beartype.claw import beartype_all

    # Prior global beartype configuration registered by a prior call to the
    # beartype_all() function if any *OR* "None" otherwise.
    packages_trie_conf_if_hooked_old: Optional[BeartypeConf] = None

    # Attempt to...
    try:
        # With a "beartype.claw"-specific thread-safe reentrant lock...
        with claw_lock:
            # Store the prior global beartype configuration if any.
            packages_trie_conf_if_hooked_old = (
                claw_state.packages_trie.conf_if_hooked)

            # Prevent the beartype_all() function from raising an exception on
            # conflicting registrations of beartype configurations.
            claw_state.packages_trie.conf_if_hooked = None

        # Globalize the passed beartype configuration.
        beartype_all(conf=conf)

        # Defer to the caller body of the parent "with beartyping(...):" block.
        yield
    # After doing so (regardless of whether doing so raised an exception)...
    finally:
        # With a "beartype.claw"-specific thread-safe reentrant lock...
        with claw_lock:
            # If the current global beartype configuration is still the passed
            # beartype configuration, then the caller's body of the parent "with
            # beartyping(...):" block has *NOT* itself called the beartype_all()
            # function with a conflicting beartype configuration. In this
            # case...
            if claw_state.packages_trie.conf_if_hooked == conf:
                # Restore the prior global beartype configuration if any.
                claw_state.packages_trie.conf_if_hooked = (
                    packages_trie_conf_if_hooked_old)

                # Possibly remove our beartype import path hook added by the
                # above call to beartype_all() if *NO* packages are registered.
                remove_beartype_pathhook_unless_packages_trie()
            # Else, the caller's body of the parent "with beartyping(...):"
            # block has itself called the beartype_all() function with a
            # conflicting beartype configuration. In this case, preserve that
            # configuration as is.


#FIXME: Unit test us up, please.
@contextmanager
def packages_trie_cleared() -> Iterator[None]:
    '''
    Test-specific context manager reverting (i.e., clearing, resetting) the
    :data:`beartype.claw._pkg.clawpkgtrie.packages_trie` global back to its
    initial state *after* running the body of the caller-defined ``with
    beartyping(...):`` block.

    This context manager is thread-safe.

    Caveats
    ----------
    **This context manager is intentionally hidden from users as a private
    attribute of this submodule** rather than publicly exported. Why? Because
    this context manager is *only* intended to be invoked by unit and
    integration tests in our test suite.

    Yields
    ----------
    None
        This context manager yields *no* objects.
    '''

    # Assert that *NO* packages are still registered by a prior call to a
    # beartype import hook.
    assert not is_packages_trie()

    # Perform the caller-defined body of the parent "with" statement.
    try:
        yield
    # After doing so, regardless of whether doing so raised an exception...
    finally:
        # print(f'claw_state [after test]: {repr(claw_state)}')

        # With a submodule-specific thread-safe reentrant lock, reset our import
        # hook state back to its initial defaults.
        with claw_lock:
            claw_state.reinit()
