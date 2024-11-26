#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **import hook managers** (i.e., lower-level private-facing functions
internally driving the higher-level public facing import hooks exported by the
:mod:`beartype.claw._clawmain` submodule).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.claw._pkg.clawpkgenum import BeartypeClawCoverage
from beartype.claw._pkg.clawpkgtrie import (
    PackagesTrie,
    iter_packages_trie,
    remove_beartype_pathhook_unless_packages_trie,
)
from beartype.claw._pkg._clawpkgmake import (
    make_conf_hookable,
    make_package_names_from_args,
)
from beartype.claw._importlib.clawimppath import (
    add_beartype_pathhook,
    # remove_beartype_pathhook,
)
from beartype.roar import (
    BeartypeClawHookException,
)
from beartype.typing import (
    Iterable,
    Optional,
)
from beartype._conf.confcls import BeartypeConf

# ....................{ (UN)HOOKERS                        }....................
#FIXME: Unit test us up, please.
def hook_packages(
    # Keyword-only arguments.
    *,

    # Mandatory keyword-only arguments.
    claw_coverage: BeartypeClawCoverage,
    conf: BeartypeConf,

    # Optional keyword-only arguments.
    package_name: Optional[str] = None,
    package_names: Optional[Iterable[str]] = None,
) -> None:
    '''
    Register a new **beartype package import path hook** (i.e., callable
    inserted to the front of the standard :mod:`sys.path_hooks` list recursively
    applying the :func:`beartype.beartype` decorator to all typed callables and
    classes of all submodules of all packages with the passed names on the first
    importation of those submodules).

    Parameters
    ----------
    claw_coverage : BeartypeClawCoverage
        **Import hook coverage** (i.e., competing package scope over which to
        apply the path hook added by this function, each with concomitant
        tradeoffs with respect to runtime complexity and quality assurance).
    conf : BeartypeConf, optional
        **Beartype configuration** (i.e., dataclass configuring the
        :mod:`beartype.beartype` decorator for *all* decoratable objects
        recursively decorated by the path hook added by this function).
    package_name : Optional[str]
        Either:

        * If ``coverage`` is :attr:`BeartypeClawCoverage.PACKAGES_ONE`, the
          fully-qualified name of the package to be type-checked.
        * Else, ignored.

        Defaults to :data:`None`.
    package_names : Optional[Iterable[str]]]
        Either:

        * If ``coverage`` is :attr:`BeartypeClawCoverage.PACKAGES_MANY`, an
          iterable of the fully-qualified names of one or more packages to be
          type-checked.
        * Else, ignored.

        Defaults to :data:`None`.

    Raises
    ----------
    BeartypeClawHookException
        If either:

        * The passed ``package_names`` parameter is either:

          * Neither a string nor an iterable (i.e., fails to satisfy the
            :class:`collections.abc.Iterable` protocol).
          * An empty string or iterable.
          * A non-empty string that is *not* a valid **package name** (i.e.,
            ``"."``-delimited concatenation of valid Python identifiers).
          * A non-empty iterable containing at least one item that is either:

            * *Not* a string.
            * The empty string.
            * A non-empty string that is *not* a valid **package name** (i.e.,
              ``"."``-delimited concatenation of valid Python identifiers).

        * The passed ``conf`` parameter is *not* a beartype configuration (i.e.,
          :class:`BeartypeConf` instance).

    See Also
    ----------
    https://stackoverflow.com/a/43573798/2809027
        StackOverflow answer strongly inspiring the low-level implementation of
        this function with respect to inscrutable :mod:`importlib` machinery.
    '''

    # Avoid circular import dependencies.
    from beartype.claw._clawstate import (
        claw_lock,
        claw_state,
    )

    # Replace this beartype configuration (which is typically unsuitable for
    # usage in import hooks) with a new beartype configuration suitable for
    # usage in import hooks.
    conf = make_conf_hookable(conf)

    # Iterable of the passed fully-qualified names of all packages to be hooked.
    package_names = make_package_names_from_args(
        claw_coverage=claw_coverage,
        conf=conf,
        package_name=package_name,
        package_names=package_names,
    )

    # With a submodule-specific thread-safe reentrant lock...
    with claw_lock:
        # If the caller requested all-packages coverage...
        if claw_coverage is BeartypeClawCoverage.PACKAGES_ALL:
            # Beartype configuration currently associated with *ALL* packages by
            # a prior call to this function if any *OR* "None" (i.e., if this
            # function has yet to be called under this Python interpreter).
            conf_curr = claw_state.packages_trie.conf_if_hooked

            # If the higher-level beartype_all() function (calling this
            # lower-level adder) has yet to be called under this interpreter,
            # associate this configuration with *ALL* packages.
            if conf_curr is None:
                claw_state.packages_trie.conf_if_hooked = conf
            # Else, beartype_all() was already called under this interpreter.
            #
            # If the caller passed a different configuration to that prior call
            # than that passed to this current call, raise an exception.
            elif conf_curr != conf:
                raise BeartypeClawHookException(
                    f'beartype_all() previously passed '
                    f'conflicting beartype configuration:\n'
                    f'\t----------( OLD "conf" PARAMETER )----------\n'
                    f'\t{repr(conf_curr)}\n'
                    f'\t----------( NEW "conf" PARAMETER )----------\n'
                    f'\t{repr(conf)}\n'
                )
            # Else, the caller passed the same configuration to that prior call
            # than that passed to the current call.
        # Else, the caller requested coverage over a subset of packages. In this
        # case...
        else:
            # For the fully-qualified name of each package to be registered...
            for package_name in package_names:  # type: ignore[union-attr]
                # List of each unqualified basename comprising this name, split
                # from this fully-qualified name on "." delimiters. Note that
                # the "str.split('.')" and "str.rsplit('.')" calls produce the
                # exact same lists under all possible edge cases. We arbitrarily
                # call the former rather than the latter for simplicity.
                package_basenames = package_name.split('.')

                # Current subtrie of the global package trie describing the
                # currently iterated basename of this package, initialized to
                # the global trie configuring all top-level packages.
                subpackages_trie = claw_state.packages_trie

                # For each unqualified basename comprising the directed path from
                # the root parent package of that package to that package...
                for package_basename in package_basenames:
                    # Current subtrie of that trie describing that parent package if
                    # that parent package was registered by a prior call to the
                    # hook_packages() function *OR* "None" (i.e., if that parent
                    # package has yet to be registered).
                    subpackages_subtrie = subpackages_trie.get(package_basename)

                    # If this is the first registration of that parent package,
                    # register a new subtrie describing that parent package.
                    #
                    # Note that this test could be obviated away by refactoring our
                    # "PackagesTrie" subclass from the "collections.defaultdict"
                    # superclass rather than the standard "dict" class. Since doing
                    # so would obscure erroneous attempts to access non-existing
                    # keys, however, this test is preferable to inviting even *MORE*
                    # bugs into this bug-riddled codebase. Just kidding! There are
                    # absolutely no bugs in this codebase. *wink*
                    if subpackages_subtrie is None:
                        subpackages_subtrie = \
                            subpackages_trie[package_basename] = \
                            PackagesTrie(package_basename=package_basename)
                    # Else, that parent package was already registered by a prior
                    # call to this function.

                    # Iterate the current subtrie one subpackage deeper.
                    subpackages_trie = subpackages_subtrie
                # Since the "package_basenames" list contains at least one basename,
                # the above iteration set the currently examined subdictionary
                # "subpackages_trie" to at least one subtrie of the global package
                # trie. Moreover, that subtrie is guaranteed to describe the current
                # (sub)package being registered.
                # print(f'Hooked package "{package_name}" subpackage trie {repr(subpackages_trie)}...')

                # Beartype configuration currently associated with that package by a
                # prior call to this function if any *OR* "None" (i.e., if that
                # package has yet to be registered by a prior call to this
                # function).
                conf_curr = subpackages_trie.conf_if_hooked

                # If that package has yet to be registered, associate this
                # configuration with that package.
                if conf_curr is None:
                    subpackages_trie.conf_if_hooked = conf
                # Else, that package was already registered by a previous call to
                # this function.
                #
                # If the caller passed a different configuration to that prior call
                # than that passed to this current call, raise an exception.
                elif conf_curr != conf:
                    raise BeartypeClawHookException(
                        f'Beartype import hook '
                        f'(e.g., beartype.claw.beartype_*() function) '
                        f'previously passed '
                        f'conflicting beartype configuration for '
                        f'package name "{package_name}":\n'
                        f'\t----------( OLD "conf" PARAMETER )----------\n'
                        f'\t{repr(conf_curr)}\n'
                        f'\t----------( NEW "conf" PARAMETER )----------\n'
                        f'\t{repr(conf)}\n'
                    )
                # Else, the caller passed the same configuration to that prior call
                # than that passed to the current call. In this case, silently
                # ignore this redundant request to reregister that package.

        # Lastly, if our beartype import path hook singleton has *NOT* already
        # been added to the standard "sys.path_hooks" list, do so now.
        #
        # Note that we intentionally:
        # * Do so in a thread-safe manner *INSIDE* this lock.
        # * Defer doing so until *AFTER* the above iteration has successfully
        #   registered the desired packages with our global trie. Why? This path
        #   hook subsequently calls the companion get_package_conf_or_none()
        #   function, which accesses this trie.
        add_beartype_pathhook()


#FIXME: Unit test us up, please.
def unhook_packages(
    # Keyword-only arguments.
    *,

    # Mandatory keyword-only arguments.
    claw_coverage: BeartypeClawCoverage,
    conf: BeartypeConf,

    # Optional keyword-only arguments.
    package_name: Optional[str] = None,
    package_names: Optional[Iterable[str]] = None,
) -> None:
    '''
    Unregister a previously registered **beartype package import path hook**
    (i.e., callable inserted to the front of the standard :mod:`sys.path_hooks`
    list recursively applying the :func:`beartype.beartype` decorator to all
    typed callables and classes of all submodules of all packages with the
    passed names on the first importation of those submodules).

    See Also
    ----------
    :func:`.hook_packages`
        Further details.
    '''

    # Avoid circular import dependencies.
    from beartype.claw._clawstate import (
        claw_lock,
        claw_state,
    )

    # Replace this beartype configuration (which is typically unsuitable for
    # usage in import hooks) with a new beartype configuration suitable for
    # usage in import hooks.
    conf = make_conf_hookable(conf)

    # Iterable of the passed fully-qualified names of all packages to be
    # unhooked.
    package_names = make_package_names_from_args(
        claw_coverage=claw_coverage,
        conf=conf,
        package_name=package_name,
        package_names=package_names,
    )

    # With a submodule-specific thread-safe reentrant lock...
    with claw_lock:
        # If the caller requested all-packages coverage...
        if claw_coverage is BeartypeClawCoverage.PACKAGES_ALL:
            # Unhook the beartype configuration previously associated with *ALL*
            # packages by a prior call to the beartype_all() function.
            claw_state.packages_trie.conf_if_hooked = None
        # Else, the caller requested coverage over a subset of packages. In this
        # case...
        else:
            # For the fully-qualified names of each package to be
            # unregistered...
            for package_name in package_names:  # type: ignore[union-attr]
                # List of all subpackages tries describing each parent package
                # transitively containing the passed package (as well as that of
                # that package itself).
                subpackages_tries = list(iter_packages_trie(package_name))

                # Reverse this list in-place, such that:
                # * The first item of this list is the subpackages trie
                #   describing that package itself.
                # * The last item of this list is the subpackages trie
                #   describing the root package of that package.
                subpackages_tries.reverse()

                # Unhook the beartype configuration previously associated with
                # that package by a prior call to the hook_packages() function.
                subpackages_tries[0].conf_if_hooked = None

                # Child sub-subpackages trie of the currently iterated
                # subpackages trie, describing the child subpackage of the
                # current parent package transitively containing that package.
                subsubpackages_trie = None

                # For each subpackages trie describing a parent package
                # transitively containing that package...
                for subpackages_trie in subpackages_tries:
                    # If this is *NOT* the first iteration of this loop (in
                    # which case this subpackages trie is a parent package
                    # rather than that package itself) *AND*...
                    if subsubpackages_trie is not None:
                        # If this child sub-subpackages trie describing this
                        # child sub-subpackage has one or more children, then
                        # this child sub-subpackages trie still stores
                        # meaningful metadata and is thus *NOT* safely
                        # deletable. Moreover, this implies that:
                        # * *ALL* parent subpackages tries of this child
                        #   sub-subpackages trie also still store meaningful
                        #   metadata and are thus also *NOT* safely deletable.
                        # * There exists no more meaningful work to be performed
                        #   by this iteration. Ergo, we immediately halt this
                        #   iteration now.
                        if subsubpackages_trie:
                            break
                        # Else, this child sub-subpackages trie describing this
                        # child sub-subpackage has *NO* children, implying this
                        # child sub-subpackages trie no longer stores any
                        # meaningful metadata and is thus safely deletable.

                        # Unqualified basename of this child sub-subpackage.
                        subsubpackage_basename = (
                            subsubpackages_trie.package_basename)

                        # Delete this child sub-subpackages trie from this
                        # parent subpackages trie.
                        del subpackages_trie[subsubpackage_basename]  # pyright: ignore[reportGeneralTypeIssues]
                    # Else, this is the first iteration of this loop.

                    # Treat this parent subpackages trie as the child
                    # sub-subpackages trie in the next iteration of this loop.
                    subsubpackages_trie = subpackages_trie

        # Lastly, if *ALL* meaningful metadata has now been removed from our
        # global trie, remove our beartype import path hook singleton from the
        # standard "sys.path_hooks" list.
        #
        # Note that we intentionally:
        # * Do so in a thread-safe manner *INSIDE* this lock.
        # * Defer doing so until *AFTER* the above iteration has successfully
        #   unregistered the desired packages with our global trie.
        remove_beartype_pathhook_unless_packages_trie()
