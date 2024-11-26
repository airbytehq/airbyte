#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **import hook module caches** (i.e., private dictionary singletons
enabling relevant metadata including beartype configurations associated with
submodules of all packages previously registered in our global package trie to
be efficiently stored and retrieved based on various criteria).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.claw._clawmagic import BEARTYPE_OPTIMIZATION_MARKER
from beartype.roar import BeartypeClawImportConfException
from beartype.typing import Dict
from beartype._conf.confcls import BeartypeConf
from pprint import pformat

# Original cache_from_source() function defined by the private (*gulp*)
# "importlib._bootstrap_external" submodule, preserved *BEFORE* temporarily
# replacing that function with our beartype-specific variant in the
# "beartype.claw._importlib._clawimpload" submodule.
from importlib.util import cache_from_source as cache_from_source_original

# ....................{ CLASSES                            }....................
class ModuleNameToBeartypeConf(Dict[str, 'BeartypeConf']):
    '''
    Non-thread-safe **hooked module beartype configuration cache** (i.e.,
    dictionary mapping from the fully-qualified name of each previously imported
    submodule of each package previously registered in our global package trie
    to the beartype configuration configuring type-checking by the
    :func:`beartype.beartype` decorator of that submodule).

    This dictionary subclass improves the human readability of exceptions raised
    by dunder methods of the :class:`dict` superclass (e.g., the
    :meth:`dict.__getitem__` dunder method), whose C-based implementations
    raise non-human-readable exceptions in common use cases encountered by end
    users leveraging beartype import hooks: e.g.,

    .. code-block:: python

        # Otherwise syntactically and semantically correct PEP 526-compliant
        # annotated assignment expressions like this previously raised spurious
        # non-human-readable exceptions from this dictionary resembling:
        #     KeyError: 'muh_module'  # <-- what does this even mean!?!?
        loves_philosophy: float = len('The fountains mingle with the river')

    Motivation
    ----------
    This cache provides an efficient ``O(1)`` alternative to the comparatively
    less efficient
    :func:`beartype.claw._pkg.clawpkgtrie.get_package_conf_or_none` function,
    which exhibits worst-case runtime complexity of ``O(k)`` for ``k`` the
    maximum depth of our global package trie. Doing so enables the
    :mod:`beartype.claw._ast.clawastmain` submodule implementing our abstract
    syntax tree (AST) node transformer to trivially inject efficient code
    looking up the current beartype configuration associated with the currently
    transformed module into the body of that module, which would otherwise be
    quite non-trivial.

    Caveats
    ----------
    **This cache is non-thread-safe.** The caller is responsible for
    guaranteeing thread-safety on writes to this cache. However, Note that reads
    of this cache are implicitly thread-safe. The :meth:`BeartypeConf.__new__`
    instantiator thread-safely stores strong references to the currently
    instantiated beartype configuration in both this and other caches. Since
    these caches and thus *all* configurations persist for the lifetime of the
    active Python interpreter, reads are effectively thread-safe.
    '''

    # ....................{ DUNDERS                        }....................
    def __getitem__(self, module_name: str) -> 'BeartypeConf':
        '''
        Return the previously instantiated beartype configuration associated
        with the module with the passed name.

        Parameters
        ----------
        module_name : str
            Fully-qualified name of the module associated with the beartype
            configuration to be returned.

        Returns
        ----------
        beartype.BeartypeConf
            Beartype configuration associated with this module.

        Raises
        ----------
        BeartypeClawImportConfException
            If no beartype configuration with this module has been previously
            instantiated.
        '''

        # Attempt to defer to the superclass implementation.
        try:
            return super().__getitem__(module_name)
        # If doing so fails with a low-level non-human-readable exception...
        except KeyError as exception:  # pragma: no cover
            #FIXME: Also, consider dropping the parallel
            #"BeartypeSourceFileLoader._main_module_name_beartype" attribute.
            #Does this nonsense supercede that nonsense? Probably. Which leads
            #us directly to...

            # If the module to be inspected is the "__main__" pseudo-module
            # signifying the main entry-point into the active Python process...
            if module_name == '__main__':
                # from sys import argv
                # print(f'Python arguments: "{repr(argv)}"')
                # print(f'Main module spec: "{__main__.__spec__}"')

                # Import this pseudo-module.
                #
                # Note that:
                # * Note that Python guarantees this pseudo-module to *ALWAYS*
                #   be safely importable, regardless of whether a main module
                #   actually was imported as an entry-point or not.
                # * This import *MUST* be delayed as long as feasible. In fact,
                #   this need to delay this import as long as feasible is why
                #   this import is performed here; this block is actually the
                #   last possible code path that this import can be delayed to.
                #
                # Ideally, this import would be performed earlier (e.g., in the
                # BeartypeSourceFileLoader.__init__() method defined in the
                # "beartype.claw._importlib._clawimpload" submodule) for
                # debuggability, efficiency, and idempotency; for this reason, a
                # prior implementation of the aforementioned method performed
                # this import.
                #
                # Pragmatically, doing so:
                # * Succeeded in some common edge cases, including execution of
                #   a third-party "muh_package" package invoked at the command
                #   line as "python -m muh_package", containing:
                #   * A "muh_package.__init__" submodule calling our
                #     beartype.claw.beartype_this_package() import hook.
                #   * A "muh_package.__main__" submodule.
                # * Failed in other common edge cases, including execution of a
                #   third-party "muh_package.muh_submodule" submodule invoked at
                #   the command line as "python -m muh_package.muh_submodule",
                #   containing:
                #   * A "muh_package.__init__" submodule calling our
                #     beartype.claw.beartype_this_package() import hook.
                #   * *NO* "muh_package.__main__" submodule.
                #
                # Why the discrepancy? Because CPython itself (specifically,
                # CPython's "runpy" architecture responsible for bootstrapping
                # CPython at process startup) is buggy. Due to non-trivial
                # "runpy" implementation details that are ultimately irrelevant
                # to @beartype, CPython inconsistently alters the values of
                # various critical system globals necessarily introspected by
                # the "beartype.claw" API, including erroneously reporting that:
                # * In the aforementioned "muh_package.__init__" submodule:
                #   * The "sys.argv" global is just "[-m]", thus truncating the
                #     trailing module name.
                #   * The "__main__" pseudo-module is empty and thus effectively
                #     unimportable for all intents and purposes.
                # * In the aforementioned "muh_package.__main__" and
                #   "muh_package.muh_submodule" submodules:
                #   * The "sys.argv" global is just "['muh_package']" and
                #     "['muh_package.muh_submodule']" (respectively), thus
                #     truncating the leading argument "-m".
                #   * The "__main__" pseudo-module is non-empty and thus
                #     importable for all intents and purposes.
                #
                # CPython blatantly lies about both the "sys.argv" global *AND*
                # "__main__" pseudo-module in top-level "muh_package.__init__"
                # submodules when CPython is passed the "-m" command-line
                # option. Ergo, beartype has *NO* means of introspecting either
                # object from any call in the call stack called by a top-level
                # "muh_package.__init__" submodule -- including any call to any
                # "beartype.claw" import hook. Instead, beartype *MUST* defer
                # that introspection to the last possible time... here.
                #
                # See also this relevant StackOverflow question on the topic,
                # which is nearly a decade-old as of this commit (2023 Q3) but
                # remains unresolved in even the live git version of CPython:
                #     https://stackoverflow.com/questions/42076706/sys-argv-behavior-with-python-m
                import __main__

                # Return the fully-qualified name of the actual user-defined
                # module encapsulated by the "__main__" pseudo-module.
                #
                # Note that the value of the "__main__.__name__" dunder
                # attribute is *ALWAYS* "__main__", yet another blatant lie that
                # only obfuscates the truth. Thankfully, the low-level
                # "importlib"-specific spec object publishes the fully-qualified
                # name of this actual user-defined module. I sleep now. *zzzzzz*
                return super().__getitem__(__main__.__spec__.name)

            # Raise a high-level human-readable exception instead.
            raise BeartypeClawImportConfException(
                f'Beartype configuration associated with '
                f'module "{module_name}" hooked by '
                f'"beartype.claw" not found. '
                f'Existing beartype configurations associated with '
                f'hooked modules include:\n\t{pformat(self)}'
            ) from exception

# ....................{ CACHERS                            }....................
#FIXME: Unit test us up, please.
def cache_from_source_beartype(*args, **kwargs) -> str:
    '''
    Beartype-specific variant of the
    :func:`importlib._bootstrap_external.cache_from_source` function applying a
    beartype-specific optimization marker to that function.

    This, in turn, ensures that submodules residing in packages registered by a
    prior call to the :func:`beartype_package` function are
    compiled to files with the filetype
    ``".pyc{optimization}_{BEARTYPE_OPTIMIZATION_MARKER}"``, where
    ``{optimization}`` is the original ``optimization`` parameter passed to this
    function call.
    '''

    # Original optimization parameter passed to this function call if any *OR*
    # the empty string otherwise.
    NONBEARTYPE_OPTIMIZATION_MARKER = kwargs.get('optimization', '')

    # New optimization parameter applied by this monkey-patch of that function,
    # uniquifying that parameter with a beartype-specific suffix.
    kwargs['optimization'] = (
        f'{NONBEARTYPE_OPTIMIZATION_MARKER}{BEARTYPE_OPTIMIZATION_MARKER}')

    # Defer to the implementation of the original cache_from_source() function.
    return cache_from_source_original(*args, **kwargs)
