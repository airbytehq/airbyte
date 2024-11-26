#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype type-checking error cause sleuth** (i.e., object recursively
fabricating the human-readable string describing the failure of the pith
associated with this object to satisfy this PEP-compliant type hint also
associated with this object) classes.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: The recursive "ViolationCause" class strongly overlaps with the equally
#recursive (and substantially superior) "beartype.door.TypeHint" class. Ideally:
#* Define a new private "beartype.door._doorerror" submodule.
#* Shift the "ViolationCause" class to
#  "beartype.door._doorerror._TypeHintUnbearability".
#* Shift the _TypeHintUnbearability.find_cause() method to a new
#  *PRIVATE* TypeHint._find_cause() method.
#* Preserve most of the remainder of the "_TypeHintUnbearability" class as a
#  dataclass encapsulating metadata describing the current type-checking
#  violation. That metadata (e.g., "cause_indent") is inappropriate for
#  general-purpose type hints. Exceptions include:
#  * "hint", "hint_sign", and "hint_childs" -- all of which are subsumed by the
#    "TypeHint" dataclass and should thus be excised.
#* Refactor the TypeHint._find_cause() method to accept an instance of
#  the "_TypeHintUnbearability" dataclass: e.g.,
#      class TypeHint(...):
#          def _get_unbearability_cause_or_none(
#              self, unbearability: _TypeHintUnbearability) -> Optional[str]:
#              ...
#* Refactor existing find_cause_*() getters (e.g.,
#  find_cause_sequence_args_1(), find_cause_union()) into
#  _get_unbearability_cause_or_none() methods of the corresponding "TypeHint"
#  subclasses, please.
#
#This all seems quite reasonable. Now, let's see whether it is. *gulp*
#FIXME: Actually, the above comment now ties directly into feature request #235.
#Resolving the above comment mostly suffices to resolve #235. That said, the
#above isn't *QUITE* right. It's pretty nice -- but we can do better. See the
#following comment at #235 for that better:
#    https://github.com/beartype/beartype/issues/235#issuecomment-1707127231

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeCallHintPepRaiseException
from beartype.typing import (
    Any,
    Callable,
    Optional,
    Tuple,
)
from beartype._cave._cavemap import NoneTypeOr
from beartype._conf.confcls import BeartypeConf
from beartype._data.hint.datahinttyping import TypeStack
from beartype._data.hint.pep.sign.datapepsignset import (
    HINT_SIGNS_SUPPORTED_DEEP,
    HINT_SIGNS_ORIGIN_ISINSTANCEABLE,
)
from beartype._util.hint.pep.utilpepget import (
    get_hint_pep_args,
    get_hint_pep_sign,
)
from beartype._util.hint.pep.utilpeptest import (
    is_hint_pep,
    is_hint_pep_args,
)
from beartype._check.convert.convsanify import sanify_hint_any
from beartype._util.hint.utilhinttest import is_hint_ignorable

# ....................{ CLASSES                            }....................
class ViolationCause(object):
    '''
    **Type-checking error cause sleuth** (i.e., object recursively fabricating
    the human-readable string describing the failure of the pith associated
    with this object to satisfy this PEP-compliant type hint also associated
    with this object).

    Attributes
    ----------
    cause_indent : str
        **Indentation** (i.e., string of zero or more spaces) preceding each
        line of the string returned by this getter if this string spans
        multiple lines *or* ignored otherwise (i.e., if this string is instead
        embedded in the current line).
    cause_str_or_none : Optional[str]
        If this pith either:

        * Violates this hint, a human-readable string describing this violation.
        * Satisfies this hint, ``None``.
    cls_stack : TypeStack, optional
        **Type stack** (i.e., either a tuple of the one or more
        :func:`beartype.beartype`-decorated classes lexically containing the
        class variable or method annotated by this hint *or* :data:`None`).
    conf : BeartypeConf
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all flags, options, settings, and other metadata configuring the
        current decoration of the decorated callable or class).
    exception_prefix : str
        Human-readable label describing the parameter or return value from
        which this object originates, typically embedded in exceptions raised
        from this getter in the event of unexpected runtime failure.
    func : Callable
        Decorated callable generating this type-checking error.
    hint_sign : Any
        Unsubscripted :mod:`typing` attribute identifying this hint if this hint
        is PEP-compliant *or* ``None`` otherwise.
    hint_childs : Optional[Tuple]
        Either:

        * If this hint is PEP-compliant, the possibly empty tuple of all
          arguments subscripting (indexing) this hint.

        * Else, :data:`None`.
    pith : Any
        Arbitrary object to be validated.
    pith_name : Optional[str]
        Either:

        * If this hint directly annotates a callable parameter (as the root type
          hint of that parameter), the name of this parameter.
        * If this hint directly annotates a callable return (as the root type
          hint of that return), the magic string ``"return"``.
        * Else, :data:`None`.
    random_int : Optional[int]
        **Pseudo-random integer** (i.e., unsigned 32-bit integer
        pseudo-randomly generated by the parent :func:`beartype.beartype`
        wrapper function in type-checking randomly indexed container items by
        the current call to that function) if that function generated such an
        integer *or* ``None`` otherwise (i.e., if that function generated *no*
        such integer). See the same parameter accepted by the higher-level
        :func:`beartype._decor.error.errormain.get_beartype_violation`
        function for further details.

    Attributes (Private)
    ----------
    _hint : Any
        Type hint to validate this object against.
    '''

    # ..................{ CLASS VARIABLES                    }..................
    # Slot *ALL* instance variables defined on this object to both:
    # * Prevent accidental declaration of erroneous instance variables.
    # * Minimize space and time complexity.
    __slots__ = (
        'cause_indent',
        'cause_str_or_none',
        'cls_stack',
        'conf',
        'exception_prefix',
        'func',
        'hint_sign',
        'hint_childs',
        'pith',
        'pith_name',
        'random_int',
        '_hint',
    )


    _INIT_PARAM_NAMES = frozenset((
        'cause_indent',
        'cause_str_or_none',
        'cls_stack',
        'conf',
        'exception_prefix',
        'func',
        'hint',
        'pith',
        'pith_name',
        'random_int',
    ))
    '''
    Frozen set of the names of all parameters accepted by the :meth:`init`
    method, defined as a set to enable efficient membership testing.
    '''

    # ..................{ INITIALIZERS                       }..................
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # CAUTION: Whenever adding, deleting, or renaming any parameter accepted by
    # this method, make similar changes to the "_INIT_PARAM_NAMES" set above.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    def __init__(
        self,

        # Mandatory parameters.
        func: Callable,
        cls_stack: TypeStack,
        conf: BeartypeConf,
        pith: Any,
        pith_name: Optional[str],
        hint: Any,
        cause_indent: str,
        exception_prefix: str,
        random_int: Optional[int],

        # Optional parameters.
        cause_str_or_none: Optional[str] = None,
    ) -> None:
        '''
        Initialize this object.

        Parameters
        ----------
        See the class docstring for a description of these parameters.
        '''
        assert callable(func), f'{repr(func)} not callable.'
        assert isinstance(cls_stack, NoneTypeOr[tuple]), (
            f'{repr(cls_stack)} neither tuple nor "None".')
        assert isinstance(conf, BeartypeConf), (
            f'{repr(conf)} not configuration.')
        assert isinstance(pith_name, NoneTypeOr[str]), (
            f'{repr(pith_name)} not string or "None".')
        assert isinstance(cause_indent, str), (
            f'{repr(cause_indent)} not string.')
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')
        assert isinstance(random_int, NoneTypeOr[int]), (
            f'{repr(random_int)} not integer or "None".')
        assert isinstance(cause_str_or_none, NoneTypeOr[str]), (
            f'{repr(cause_str_or_none)} not string or "None".')

        # Classify all passed parameters.
        self.func = func
        self.cls_stack = cls_stack
        self.conf = conf
        self.pith = pith
        self.pith_name = pith_name
        self.cause_indent = cause_indent
        self.exception_prefix = exception_prefix
        self.random_int = random_int
        self.cause_str_or_none = cause_str_or_none

        # Nullify all remaining parameters for safety.
        self.hint_sign: Any = None
        self.hint_childs: Tuple = None  # type: ignore[assignment]

        # Classify this hint *AFTER* initializing all parameters above.
        #
        # Note that this assignment magically calls the "hint" property setter
        # defined below. Don't ask. Just do it, Python! *sigh*
        self.hint = hint

    # ..................{ PROPERTIES                         }..................
    @property
    def hint(self) -> Any:
        '''
        Type hint to validate this object against.
        '''

        return self._hint


    @hint.setter
    def hint(self, hint: Any) -> None:
        '''
        Set the type hint to validate this object against.
        '''

        # Sanitize this hint if unsupported by @beartype in its current form
        # (e.g., "numpy.typing.NDArray[...]") to another form supported by
        # @beartype (e.g., "typing.Annotated[numpy.ndarray, beartype.vale.*]").
        hint = sanify_hint_any(
            hint=hint,
            conf=self.conf,
            exception_prefix=self.exception_prefix,
            cls_stack=self.cls_stack,
            arg_name=self.pith_name,
        )

        # If this hint is PEP-compliant...
        if is_hint_pep(hint):
            # Arbitrary object uniquely identifying this hint.
            self.hint_sign = get_hint_pep_sign(hint)

            # Tuple of the zero or more arguments subscripting this hint.
            self.hint_childs = get_hint_pep_args(hint)
        # Else, this hint is PEP-noncompliant (e.g., isinstanceable class).

        # Classify this hint *AFTER* all other assignments above.
        self._hint = hint

    # ..................{ GETTERS                            }..................
    def find_cause(self) -> 'ViolationCause':
        '''
        Output cause describing whether the pith of this input cause either
        satisfies or violates the type hint of this input cause.

        Design
        ----------
        This method is intentionally generalized to support objects both
        satisfying and *not* satisfying hints as equally valid use cases. While
        the parent
        :func:`beartype._decor.error.errormain.get_beartype_violation` function
        calling this method is *always* passed an object *not* satisfying the
        passed hint, this method is under no such constraints. Why? Because this
        method is also called to find which of an arbitrary number of objects
        transitively nested in the object passed to
        :func:`beartype._decor.error.errormain.get_beartype_violation` fails to
        satisfy the corresponding hint transitively nested in the hint passed to
        that function.

        For example, consider the PEP-compliant type hint ``List[Union[int,
        str]]`` describing a list whose items are either integers or strings
        and the list ``list(range(256)) + [False,]`` consisting of the integers
        0 through 255 followed by boolean ``False``. Since that list is a
        standard sequence, the
        :func:`._peperrorsequence.find_cause_sequence_args_1`
        function must decide the cause of this list's failure to comply with
        this hint by finding the list item that is neither an integer nor a
        string, implemented by by iteratively passing each list item to the
        :func:`._peperrorunion.find_cause_union` function. Since
        the first 256 items of this list are integers satisfying this hint,
        :func:`._peperrorunion.find_cause_union` returns a dataclass instance
        whose :attr:`cause` field is ``None`` up to
        :func:`._peperrorsequence.find_cause_sequence_args_1`
        before finally finding the non-compliant boolean item and returning the
        human-readable cause.

        Returns
        ----------
        ViolationCause
            Output cause type-checking this pith against this type hint.

        Raises
        ----------
        _BeartypeCallHintPepRaiseException
            If this type hint is either:

            * PEP-noncompliant (e.g., tuple union).
            * PEP-compliant but no getter function has been implemented to
              handle this category of PEP-compliant type hint yet.
        '''

        # If this hint is ignorable, all possible objects satisfy this hint.
        # Since this hint *CANNOT* (by definition) be the cause of this failure,
        # return the same cause as is.
        if is_hint_ignorable(self.hint):
            return self
        # Else, this hint is unignorable.

        # Getter function returning the desired string.
        cause_finder: Callable[[ViolationCause], ViolationCause] = None  # type: ignore[assignment]

        #FIXME: Trivially simplify this method by:
        #* Define a new find_cause_nonpep() function elsewhere whose body is
        #  the body of this "if" conditional branch.
        #* Register this function with HINT_SIGN_TO_GET_CAUSE_FUNC: e.g.,
        #  HINT_SIGN_TO_GET_CAUSE_FUNC = {
        #      ...,
        #      None: find_cause_nonpep,
        #  }
        #* Remove this "if" conditional branch.

        # If *NO* sign uniquely identifies this hint, this hint is either
        # PEP-noncompliant *OR* only contextually PEP-compliant in certain
        # specific use cases. In either case...
        if self.hint_sign is None:
            # If this hint is a tuple union...
            if isinstance(self.hint, tuple):
                # Avoid circular import dependencies.
                from beartype._decor.error._errortype import (
                    find_cause_instance_types_tuple)

                # Defer to the getter function specific to tuple unions.
                cause_finder = find_cause_instance_types_tuple
            # Else, this hint is *NOT* a tuple union. In this case, assume this
            # hint to be an isinstanceable class. If this is *NOT* the case, the
            # getter deferred to below raises a human-readable exception.
            else:
                # Avoid circular import dependencies.
                from beartype._decor.error._errortype import (
                    find_cause_instance_type)

                # Defer to the getter function specific to classes.
                cause_finder = find_cause_instance_type
        # Else, this hint is PEP-compliant.
        #
        # If this hint...
        elif (
            # Originates from an origin type and may thus be shallowly
            # type-checked against that type *AND is either...
            self.hint_sign in HINT_SIGNS_ORIGIN_ISINSTANCEABLE and (
                # Unsubscripted *OR*...
                not is_hint_pep_args(self.hint) or
                #FIXME: Remove this branch *AFTER* deeply supporting all hints.
                # Currently unsupported with deep type-checking...
                self.hint_sign not in HINT_SIGNS_SUPPORTED_DEEP
            )
        # Then this hint is both unsubscripted and originating from a standard
        # type origin. In this case, this hint was type-checked shallowly.
        ):
            # Avoid circular import dependencies.
            from beartype._decor.error._errortype import (
                find_cause_type_instance_origin)

            # Defer to the getter function supporting hints originating from
            # origin types.
            cause_finder = find_cause_type_instance_origin
        # Else, this hint is either subscripted *OR* unsubscripted but not
        # originating from a standard type origin. In either case, this hint
        # was type-checked deeply.
        else:
            # Avoid circular import dependencies.
            from beartype._decor.error.errormain import (
                HINT_SIGN_TO_GET_CAUSE_FUNC)

            # Getter function returning the desired string for this attribute
            # if any *OR* "None" otherwise.
            cause_finder = HINT_SIGN_TO_GET_CAUSE_FUNC.get(
                self.hint_sign, None)  # type: ignore[arg-type]

            # If no such function has been implemented to handle this attribute
            # yet, raise an exception.
            if cause_finder is None:
                raise _BeartypeCallHintPepRaiseException(
                    f'{self.exception_prefix} type hint '
                    f'{repr(self.hint)} unsupported (i.e., no '
                    f'"find_cause_"-prefixed getter function defined '
                    f'for this category of hint).'
                )
            # Else, a getter function has been implemented to handle this
            # attribute.

        # Call this getter function with ourselves and return the string
        # returned by this getter.
        return cause_finder(self)

    # ..................{ PERMUTERS                          }..................
    def permute(self, **kwargs) -> 'ViolationCause':
        '''
        Shallow copy of this object such that each the passed keyword argument
        overwrites the instance variable of the same name in this copy.

        Parameters
        ----------
        Keyword arguments of the same name and type as instance variables of
        this object (e.g., ``hint``, ``pith``).

        Returns
        ----------
        ViolationCause
            Shallow copy of this object such that each keyword argument
            overwrites the instance variable of the same name in this copy.

        Raises
        ----------
        _BeartypeCallHintPepRaiseException
            If the name of any passed keyword argument is *not* the name of an
            existing instance variable of this object.

        Examples
        ----------
            >>> sleuth = ViolationCause(
            ...     pith=[42,]
            ...     hint=typing.List[int],
            ...     cause_indent='',
            ...     exception_prefix='List of integers',
            ... )
            >>> sleuth_copy = sleuth.permute(pith=[24,])
            >>> sleuth_copy.pith
            [24,]
            >>> sleuth_copy.hint
            typing.List[int]
        '''

        # For the name of each passed keyword argument...
        for arg_name in kwargs.keys():
            # If this name is *NOT* that of a parameter accepted by the
            # __init__() method, raise an exception.
            if arg_name not in self._INIT_PARAM_NAMES:
                raise _BeartypeCallHintPepRaiseException(
                    f'{self.__class__}.__init__() parameter '
                    f'{arg_name} unrecognized.'
                )

        # For the name of each parameter accepted by the __init__() method...
        for arg_name in self._INIT_PARAM_NAMES:
            # If this parameter was *NOT* explicitly passed by the caller,
            # default this parameter to its current value from this object.
            if arg_name not in kwargs:
                kwargs[arg_name] = getattr(self, arg_name)

        # Return a new instance of this class initialized with these arguments.
        return ViolationCause(**kwargs)
