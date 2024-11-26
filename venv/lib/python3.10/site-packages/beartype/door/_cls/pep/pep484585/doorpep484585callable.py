#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **Decidedly Object-Oriented Runtime-checking (DOOR) callable type hint
classes** (i.e., :class:`beartype.door.TypeHint` subclasses implementing support
for :pep:`484`- and :pep:`585`-compliant ``Callable[...]`` type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.door._cls.doorsub import _TypeHintSubscripted
from beartype.door._cls.doorsuper import (
    TypeHint,
    # T,
)
from beartype.roar import BeartypeDoorPepUnsupportedException
from beartype.typing import (
    Any,
    Tuple,
)
from beartype._data.hint.pep.sign.datapepsignset import (
    HINT_SIGNS_CALLABLE_PARAMS)
# from beartype._data.kind.datakindsequence import TUPLE_EMPTY
from beartype._util.cache.utilcachecall import property_cached
from beartype._util.hint.pep.proposal.pep484585.utilpep484585callable import (
    get_hint_pep484585_callable_params,
    get_hint_pep484585_callable_return,
)
from beartype._util.hint.pep.utilpepget import get_hint_pep_sign_or_none

# ....................{ SUBCLASSES                         }....................
class CallableTypeHint(_TypeHintSubscripted):
    '''
    **Callable type hint wrapper** (i.e., high-level object encapsulating a
    low-level :pep:`484`- or :pep:`585`-compliant ``Callable[...]`` type hint).
    '''

    # ..................{ INITIALIZERS                       }..................
    def _make_args(self) -> tuple:
        # print(f'{self}._origin: {self._origin}')

        # Tuple of all child type hints subscripting this callable type hint,
        # localized for both readability and negligible efficiency gains.
        #
        # Note that this is a flattened tuple of the one or more child type
        # hints subscripting this callable type hint. Presumably for space
        # efficiency reasons, both PEP 484- *AND* 585-compliant callable type
        # hints implicitly flatten the "__args__" dunder tuple from the original
        # data structure subscripting those hints. CPython produces this
        # flattened tuple as the concatenation of:
        #
        # * Either:
        #   * If the first child type originally subscripting this hint was a
        #     list, all items subscripting the nested list of zero or more
        #     parameter type hints originally subscripting this hint as is:
        #         >>> Callable[[], bool].__args__
        #         (bool,)
        #         >>> Callable[[int, str], bool].__args__
        #         (int, str, bool)
        #
        #     This includes a list containing only the empty tuple signifying a
        #     callable accepting *NO* parameters, in which case that empty tuple
        #     is preserved as is:
        #         >>> Callable[[()], bool].__args__
        #         ((), bool)
        #   * Else, the first child type originally subscripting this hint as
        #     is. In this case, that child type is required to be either:
        #     * An ellipsis object (i.e., the "Ellipsis" builtin singleton):
        #         >>> Callable[..., bool].__args__
        #         (Ellipsis, bool)
        #     * A PEP 612-compliant parameter specification (i.e.,
        #       "typing.ParamSpec[...]" type hint):
        #         >>> Callable[ParamSpec('P'), bool].__args__
        #         (~P, bool)
        #     * A PEP 612-compliant parameter concatenation (i.e.,
        #       "typing.Concatenate[...]" type hint):
        #         >>> Callable[Concatenate[str, ParamSpec('P')], bool].__args__
        #         (typing.Concatenate[str, ~P], bool)
        # * The return type hint originally subscripting this hint.
        #
        # Note that both PEP 484- *AND* 585-compliant callable type hints
        # guarantee this tuple to contain at least one child type hint. Ergo, we
        # avoid validating that constraint here:
        #     >>> from typing import Callable
        #     >>> Callable[()]
        #     TypeError: Callable must be used as Callable[[arg, ...], result].
        #     >>> from collections.abc import Callable
        #     >>> Callable[()]
        #     TypeError: Callable must be used as Callable[[arg, ...], result].
        # args = self._args
        args = super()._make_args()

        # Note that this branch may be literally unreachable, as an
        # unsubscripted "Callable" should already be implicitly handled by the
        # "ClassTypeHint" subclass. Nonetheless, this branch exists for safety.
        if not args:  # pragma: no cover
            args = (..., Any,)
        else:
            # Parameters type hint(s) subscripting this callable type hint.
            #
            # Note that this:
            # * May be a special object (e.g., ellipsis) rather than a tuple of
            #   zero or more parameter type hints.
            # * Has the essential side effect of eliminating harmful edge cases
            #   (e.g., "Callable[[()], Any]", which is semantically but *NOT*
            #   syntactically equivalent to "Callable[[], Any]").
            args_params = get_hint_pep484585_callable_params(self._hint)

            # Return type hint subscripting this callable type hint.
            args_return = get_hint_pep484585_callable_return(self._hint)

            # Sign uniquely identifying this parameter list if any *OR*
            # "None" otherwise.
            hint_args_sign = get_hint_pep_sign_or_none(args_params)

            # If this hint was first subscripted by a PEP 612-compliant
            # parameter type hint, raise an exception. *sigh*
            if hint_args_sign in HINT_SIGNS_CALLABLE_PARAMS:
                raise BeartypeDoorPepUnsupportedException(
                    f'PEP 484 or 585 callable type hint {repr(self._hint)} '
                    f'PEP 612 child type hint {repr(args_params)} '
                    f'currently unsupported.'
                )
            # Else, this hint was *NOT* first subscripted by a PEP
            # 612-compliant parameter type hint.

            # Parameters type hint(s) subscripting this callable type hint,
            # coerced into a 1-tuple if *NOT* already a tuple.
            args_params_tuple = (
                args_params
                if isinstance(args_params, tuple) else
                (args_params,)
            )

            # Recreate the tuple of child type hints subscripting this parent
            # callable type hint from the tuple of argument type hints
            # introspected above. Why? Because the latter is saner than the
            # former in edge cases (e.g., ellipsis, empty argument lists).
            args = args_params_tuple + (args_return,)

        # Return these child hints.
        return args

    # ..................{ PRIVATE ~ properties               }..................
    @property
    # @property_cached
    def _args_wrapped_tuple(self) -> Tuple[TypeHint, ...]:

        # Tuple of all child type hints subscripting this callable type hint.
        args = self._args

        # Number of child type hints subscripting this callable type hint.
        args_len = len(args)

        # Tuple of all child type hint wrappers subscripting this callable type
        # hint wrapper, initialized to the empty tuple for simplicity.
        args_wrapped_tuple: Tuple[TypeHint, ...] = ()

        # If this type hint is unsubscripted, return the empty tuple.
        if not args_len:
            pass
        # Else, this type hint is subscripted by one or more child type hints.
        #
        # If this type hint is subscripted by exactly one child type hint, then
        # that child type hint signifies this callable's return type hint,
        # implying this callable accepts *NO* parameters. In this case...
        elif args_len == 1:
            # Return a 2-tuple consisting of...
            args_wrapped_tuple = (
                # Empty parameter list.
                TypeHint(Tuple[()]),
                # Return type hint.
                TypeHint(args[-1]),
            )
        # Else, this type hint is subscripted by two or more child type hints.
        #
        # If the first child type hint subscripting this type hint is an
        # ellipsis (i.e., "..."), this callable accepts *ANY* parameters of
        # *ANY* arbitrary types. In this case...
        elif args[0] is ...:
            # Return a 2-tuple consisting of...
            args_wrapped_tuple = (
                # Variadic parameter list.
                TypeHint(Any),
                # Return type hint.
                TypeHint(args[-1]),
            )
        # Else, the first child type hint subscripting this type hint is *NOT*
        # an ellipsis. In this case, defer to the superclass approach.
        else:
            args_wrapped_tuple = super()._args_wrapped_tuple

        # Return this tuple.
        # print(f'Callable: {self._hint}; args: {self._args}; args_wrapped_tuple: {args_wrapped_tuple}')
        return args_wrapped_tuple

    # ..................{ PROPERTIES ~ hints                 }..................
    @property  # type: ignore
    @property_cached
    def param_hints(self) -> Tuple[TypeHint, ...]:
        '''
        Tuple of the one or more parameter type hints subscripting this
        callable type hint.

        Notably, if this callable accepts:

        * *No* parameters (i.e., was originally subscripted by the empty list as
          ``Callable[[], ???]``), this is the 1-tuple
          ``(TypeHint(Tuple[()]),)``.
        * *Any* parameters of *any* arbitrary types (i.e., was originally
          subscripted by an ellipsis as ``Callable[..., ???]``), this is the
          1-tuple ``(TypeHint(Any),)``.
        '''

        return self._args_wrapped_tuple[:-1]


    @property
    def return_hint(self) -> TypeHint:
        '''
        Return type hint subscripting this callable type hint.
        '''

        return self._args_wrapped_tuple[-1]

    # ..................{ PROPERTIES ~ bools                 }..................
    # FIXME: Remove this by instead adding support for ignoring ignorable
    # callable type hints to our core is_hint_ignorable() tester. Specifically:
    # * Ignore "Callable[..., {hint_ignorable}]" type hints, where "..." is the
    #  ellipsis singleton and "{hint_ignorable}" is any ignorable type hint.
    #  This has to be handled in a deep manner by:
    #  * Defining a new is_hint_pep484585_ignorable_or_none() tester in the
    #    existing "utilpep484585" submodule, whose initial implementation tests
    #    for *ONLY* ignorable callable type hints.
    #  * Import that tester in the "utilpeptest" submodule.
    #  * Add that tester to the "_IS_HINT_PEP_IGNORABLE_TESTERS" tuple.
    #  * Add example ignorable callable type hints to our test suite's data.
    @property
    def is_ignorable(self) -> bool:
        # Callable[..., Any] (or just `Callable`)
        return self.is_params_ignorable and self.is_return_ignorable


    @property
    def is_params_ignorable(self) -> bool:
        # Callable[..., ???]
        return self._args[0] is Ellipsis


    @property
    def is_return_ignorable(self) -> bool:
        # Callable[???, Any]
        return self.return_hint.is_ignorable

    # ..................{ PRIVATE ~ testers                  }..................
    #FIXME: Internally comment us up, please.
    def _is_subhint_branch(self, branch: TypeHint) -> bool:

        # If that branch is unsubscripted, assume it is subscripted as
        # "typing.Callable[..., Any]" and just test for compatible origins.
        if branch._is_args_ignorable:
            return issubclass(self._origin, branch._origin)
        elif not isinstance(branch, CallableTypeHint):
            return False
        elif not issubclass(self._origin, branch._origin):
            return False
        elif not branch.is_params_ignorable and (
            (
                self.is_params_ignorable or
                len(self.param_hints) != len(branch.param_hints) or
                any(
                    self_arg > branch_arg
                    for self_arg, branch_arg in zip(
                        self.param_hints, branch.param_hints)
                )
            )
        ):
            return False

        # FIXME: Insufficient, sadly. There are *MANY* different type hints that
        # are ignorable and thus semantically equivalent to "Any". It's likely
        # we should just reduce this to a one-liner resembling:
        #    return self.return_hint <= branch.return_hint
        #
        # Are we missing something? We're probably missing something. *sigh*
        elif not branch.is_return_ignorable:
            return (
                False
                if self.is_return_ignorable else
                self.return_hint <= branch.return_hint
            )

        return True
