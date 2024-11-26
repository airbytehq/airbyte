#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **functional validation classes** (i.e., :mod:`beartype`-specific
classes enabling callers to define PEP-compliant validators from arbitrary
caller-defined callables *not* efficiently generating stack-free code).

This private submodule defines the core low-level class hierarchy driving the
entire :mod:`beartype` validation ecosystem.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import (
    BeartypeValeLambdaWarning,
    BeartypeValeValidationException,
)
from beartype.typing import Protocol
from beartype.vale._is._valeisabc import _BeartypeValidatorFactoryABC
from beartype.vale._core._valecore import BeartypeValidator
from beartype.vale._util._valeutilfunc import die_unless_validator_tester
from beartype.vale._util._valeutiltyping import BeartypeValidatorTester
from beartype._data.hint.datahinttyping import LexicalScope
from beartype._util.func.utilfuncscope import add_func_scope_attr
from beartype._util.text.utiltextrepr import (
    represent_func,
    represent_object,
)

# ....................{ PRIVATE ~ protocols                }....................
class _SupportsBool(Protocol):
    '''
    Fast caching protocol matching any object whose class defines the
    :meth:`__bool__` dunder method.
    '''

    def __bool__(self) -> bool: ...


class _SupportsLen(Protocol):
    '''
    Fast caching protocol matching any object whose class defines the
    :meth:`__len__` dunder method.
    '''

    def __len__(self) -> bool: ...


_BoolLike = (_SupportsBool, _SupportsLen)
'''
:func:`isinstance`-able tuple of fast caching protocols matching any
**bool-like** (i.e., object whose class defines at least one of the
:meth:`__bool__` and/or :meth:`__len__` dunder methods).
'''

# ....................{ PRIVATE ~ subclasses               }....................
class _IsFactory(_BeartypeValidatorFactoryABC):
    '''
    **Beartype callable validator factory** (i.e., class that, when subscripted
    (indexed) by an arbitrary callable returning ``True`` when the object
    passed to that callable satisfies a caller-defined constraint, creates a
    new :class:`BeartypeValidator` object encapsulating that callable suitable
    for subscripting (indexing) :attr:`typing.Annotated` type hints, enforcing
    that constraint on :mod:`beartype`-decorated callable parameters and
    returns annotated by those hints).

    This class validates that callable parameters and returns satisfy the
    arbitrary **callable validator** (i.e., callable whose signature satisfies
    ``collections.abc.Callable[[typing.Any], bool]``) subscripting (indexing)
    this class. Callable validators are caller-defined and may thus validate
    the internal integrity, consistency, and structure of arbitrary objects
    ranging from simple builtin scalars like integers and strings to complex
    data structures defined by third-party packages like NumPy arrays and
    Pandas DataFrames.

    This class creates one new :class:`BeartypeValidator` object for each
    callable validator subscripting (indexing) this class. These objects:

    * Are **PEP-compliant** and thus guaranteed to *never* violate existing or
      future standards.
    * Are **Safely ignorable** by *all* static and runtime type checkers other
      than :mod:`beartype` itself.
    * **Less efficient** than :class:`BeartypeValidator` objects created by
      subscripting every other :mod:`beartype.vale` class. Specifically:

      * Every :class:`BeartypeValidator` object created by subscripting this
        class necessarily calls a callable validator and thus incurs at least
        one additional call stack frame per :mod:`beartype`-decorated callable
        call.
      * Every :class:`BeartypeValidator` object created by subscripting every
        other :mod:`beartype.vale` class directly calls *no* callable and thus
        incurs additional call stack frames only when the active Python
        interpreter internally calls dunder methods (e.g., ``__eq__()``) to
        satisfy their validation constraint.

    Usage
    ----------
    Any :mod:`beartype`-decorated callable parameter or return annotated by a
    :attr:`typing.Annotated` type hint subscripted (indexed) by this class
    subscripted (indexed) by a callable validator (e.g.,
    ``typing.Annotated[{cls}, beartype.vale.Is[lambda obj: {expr}]]`` for any
    class ``{cls}``  and Python expression ``{expr}` evaluating to a boolean)
    validates that parameter or return value to be an instance of that class
    satisfying that callable validator.

    Specifically, callers are expected to (in order):

    #. Annotate a callable parameter or return to be validated with a
       :pep:`593`-compliant :attr:`typing.Annotated` type hint.
    #. Subscript that hint with (in order):

       #. The type expected by that parameter or return.
       #. One or more subscriptions (indexations) of this class, each itself
          subscripted (indexed) by a **callable validator** (i.e., callable
          accepting a single arbitrary object and returning either ``True`` if
          that object satisfies an arbitrary constraint *or* ``False``
          otherwise). If that hint is subscripted by:

          * Only one subscription of this class, that parameter or return
            satisfies that hint when both:

            * That parameter or return is an instance of the expected type.
            * That validator returns ``True`` when passed that parameter or
              return.

          * Two or more subscriptions of this class, that parameter or return
            satisfies that hint when both:

            * That parameter or return is an instance of the expected type.
            * *All* callable validators subscripting *all* subscriptions of
              this class return ``True`` when passed that parameter or return.

          Formally, the signature of each callable validator *must* resemble:

          .. code-block:: python

             def is_object_valid(obj) -> bool:
                 return bool(obj)

          Equivalently, each callable validator *must* satisfy the type hint
          ``collections.abc.Callable[[typing.Any,], bool]``. If not the case,
          an exception is raised. Note that:

          * If that parameter or return is *not* an instance of the expected
            type, **no callable validator is called.** Equivalently, each
            callable validator is called *only* when that parameter or return
            is already an instance of the expected type. Callable validators
            need *not* revalidate that type (e.g., by passing that parameter or
            return and type to the :func:`isinstance` builtin).
          * The name of each callable validator is irrelevant. For convenience,
            most callable validators are defined as nameless lambda functions.

    For example, the following type hint only accepts non-empty strings:

    .. code-block:: python

       Annotated[str, Is[lambda text: bool(text)]]

    :class:`BeartypeValidator` objects also support an expressive
    domain-specific language (DSL) enabling callers to trivially synthesize new
    objects from existing objects with standard Pythonic math operators:

    * **Negation** (i.e., ``not``). Negating an :class:`BeartypeValidator`
      object with the ``~`` operator synthesizes a new
      :class:`BeartypeValidator` object whose validator returns ``True`` only
      when the validator of the original object returns ``False``. For example,
      the following type hint only accepts strings containing *no* periods:

      .. code-block:: python

         Annotated[str, ~Is[lambda text: '.' in text]]

    * **Conjunction** (i.e., ``and``). Conjunctively combining two or more
      :class:`BeartypeValidator` objects with the ``&`` operator synthesizes a
      new :class:`BeartypeValidator` object whose validator returns ``True``
      only when all data validators of the original objects return ``True``.
      For example, the following type hint only accepts non-empty strings
      containing *no* periods:

      .. code-block:: python

         Annotated[str, (
              Is[lambda text: bool(text)] &
             ~Is[lambda text: '.' in text]
         )]

    * **Disjunction** (i.e., ``or``). Disjunctively combining two or more
      :class:`BeartypeValidator` objects with the ``|`` operator synthesizes a
      new :class:`BeartypeValidator` object whose validator returns ``True``
      only when at least one validator of the original objects returns
      ``True``. For example, the following type hint accepts both empty strings
      *and* non-empty strings containing at least one period:

      .. code-block:: python

         Annotated[str, (
             ~Is[lambda text: bool(text)] |
              Is[lambda text: '.' in text]
         )]

    See also the **Examples** subsection below.

    Caveats
    ----------
    **This class is currently only supported by the** :func:`beartype.beartype`
    **decorator.** All other static and runtime type checkers silently ignore
    subscriptions of this class subscripting :attr:`typing.Annotated` type
    hints.

    **This class incurs a minor time performance penalty at call time.**
    Specifically, each type hint of a :mod:`beartype`-decorated callable
    subscripted by a subscription of this class adds one additional stack frame
    to each call of that callable. While negligible (in the average case), this
    cost can become non-negligible when compounded across multiple type hints
    annotating a frequently called :mod:`beartype`-decorated callable --
    especially when those type hints are subscripted by multiple subscriptions
    of this class at different nesting levels.

    **This class prohibits instantiation.** This class is *only* intended to be
    subscripted. Attempting to instantiate this class into an object will raise
    an :exc:`.BeartypeValeSubscriptionException` exception.

    Examples
    ----------
    .. code-block:: python

       # Import the requisite machinery.
       >>> from beartype import beartype
       >>> from beartype.vale import Is
       >>> from typing import Annotated

       # Validator matching only strings with lengths ranging [4, 40].
       >>> IsRangy = Is[lambda text: 4 <= len(text) <= 40]

       # Validator matching only unquoted strings.
       >>> IsUnquoted = Is[lambda text:
       ...     text.count('"') < 2 and text.count("'") < 2]

       # Type hint matching only unquoted strings.
       >>> UnquotedString = Annotated[str, IsUnquoted]

       # Type hint matching only quoted strings.
       >>> QuotedString = Annotated[str, ~IsUnquoted]

       # Type hint matching only unquoted strings with lengths ranging [4, 40].
       >>> UnquotedRangyString = Annotated[str, IsUnquoted & IsRangy]

       # Annotate callables by those type hints.
       >>> @beartype
       ... def doublequote_text(text: UnquotedString) -> QuotedString:
       ...     """
       ...     Double-quote the passed unquoted string.
       ...     """
       ...     return f'"{text}"'  # The best things in life are one-liners.
       >>> @beartype
       ... def singlequote_prefix(text: UnquotedRangyString) -> QuotedString:
       ...     """
       ...     Single-quote the prefix spanning characters ``[0, 3]`` of the
       ...     passed unquoted string with length ranging ``[4, 40]``.
       ...     """
       ...     return f"'{text[:3]}'"  # "Guaranteed to work," says @beartype.

       # Call those callables with parameters satisfying those validators.
       >>> doublequote_text("You know anything about nuclear fusion?")
       "You know anything about nuclear fusion?"
       >>> singlequote_prefix("Not now, I'm too tired. Maybe later.")
       'Not'

       # Call those callables with parameters not satisfying those validators.
       >>> doublequote_text('''"Everybody relax, I'm here."''')
       beartype.roar._roarexc.BeartypeCallHintParamViolation: @beartyped
       doublequote_text() parameter text='"Everybody relax, I\'m here."'
       violates type hint typing.Annotated[str, Is[lambda text: text.count('"')
       < 2 and text.count("'") < 2]], as value '"Everybody relax, I\'m here."'
       violates validator Is[lambda text: text.count('"') < 2 and
       text.count("'") < 2].
    '''

    # ..................{ DUNDERS                            }..................
    def __getitem__(  # type: ignore[override]
        self, is_valid: BeartypeValidatorTester) -> BeartypeValidator:
        '''
        Create and return a new beartype validator from the passed **validator
        callable** (i.e., caller-defined callable accepting a single arbitrary
        object and returning either ``True`` if that object satisfies an
        arbitrary constraint *or* ``False`` otherwise), suitable for
        subscripting :pep:`593`-compliant :attr:`typing.Annotated` type hints.

        This method is intentionally *not* memoized, as this method is usually
        subscripted only by subscription-specific lambda functions uniquely
        defined for each subscription of this class.

        Parameters
        ----------
        is_valid : Callable[[Any,], bool]
            Validator callable to validate parameters and returns against.

        Returns
        ----------
        BeartypeValidator
            New object encapsulating this validator callable.

        Raises
        ----------
        BeartypeValeSubscriptionException
            If either:

            * This class was subscripted by two or more arguments.
            * This class was subscripted by one argument that either:

              * Is *not* callable.
              * Is a C-based rather than pure-Python callable.
              * Is a pure-Python callable accepting two or more arguments.

        See Also
        ----------
        :class:`_IsAttrFactory`
            Usage instructions.
        '''

        # ..................{ VALIDATE                       }..................
        # If this class was subscripted by either no arguments *OR* two or more
        # arguments, raise an exception.
        self._die_unless_getitem_args_1(is_valid)
        # Else, this class was subscripted by exactly one argument.

        # If that callable is *NOT* a validator tester, raise an exception.
        die_unless_validator_tester(is_valid)
        # Else, that callable is a validator tester.

        # Lambda function dynamically generating the machine-readable
        # representation of this validator, deferred due to the computational
        # expense of accurately retrieving the source code for this validator
        # (especially when this validator is itself a lambda function).
        get_repr = lambda: (
            f'{self._basename}['
            f'{represent_func(func=is_valid, warning_cls=BeartypeValeLambdaWarning)}'
            f']'
        )

        # ..................{ CLOSURE                        }..................
        #FIXME: Unit test edge cases extensively, please.
        def _is_valid_bool(obj: object) -> bool:
            '''
            :data:`True` only if the passed object satisfies the caller-defined
            validation callable subscripting this :attr:`beartype.vale.Is`
            validator factory.

            This closure wraps that possibly unsafe callable with an implicit
            type cast, guaranteeing that either:

            * If that callable returns a boolean, this closure returns that
              boolean as is.
            * If that callable returns a non-boolean object, either:

              * If that non-boolean is implicitly convertible into a boolean
                (i.e., if passing that non-boolean to the :class:`bool` type
                succeeds *without* raising an exception), this closure coerces
                that non-boolean into a boolean and returns that boolean.
              * Else, this closure raises a human-readable exception.

            This closure is principally intended to massage non-standard
            validation callables defined by popular third-party packages like
            NumPy, which commonly return non-boolean objects that are implicitly
            convertible into boolean objects: e.g.,

            .. code-block::

               >>> import numpy as np
               >>> matrix = np.array([[2, 1], [1, 2]])
               >>> is_all = np.all(matrix > 0))
               >>> type(is_all)
               <class 'numpy.bool_'>
               >>> is_all
               True  # <-- y u lie, numpy
               >>> bool(is_all)
               True

            Caveats
            ----------
            **This closure is comparatively slower than the passed callable.**
            This closure should *never* be called directly from code snippets
            embedded in wrapper functions dynamically generated by the
            :func:`beartype.beartype` decorator. This closure should *only* be
            called indirectly by exception-handling functionality performed by
            those wrapper functions in the event of a type-checking violation,
            at which time efficiency is no longer a driving force.

            This implies that wrapper functions dynamically generated by the
            :func:`beartype.beartype` decorator *could* implicitly coerce
            non-boolean objects returned by the passed callable into the
            ``True`` singleton. Although non-ideal, debugging such concerns is
            squarely the user's concern; attempting to safeguard users from
            semantic issues like this would destroy runtime performance for *no*
            tangible gain in the general case. The best :mod:`beartype` can (and
            should) do is defer validation until a type-checking violation.

            Parameters
            ----------
            obj : object
                Object to be validated by that validation callable.

            Returns
            ----------
            bool
                :data:`True` only if that object satisfies that validation
                callable.

            Raises
            ----------
            BeartypeValeValidationException
                If that validation callable returns a **non-bool-like**, where
                "non-bool-like" is any object that:

                * Is *not* a **boolean** (i.e., :class:`bool` instance).
                * Is *not* **implicitly convertible** into a boolean (i.e., is
                  an object whose class defines neither the :meth:`__bool__` nor
                  :meth:`__len__` dunder methods).

    * Subscript the :attr:`beartype.vale.Is` factory by a **non-bool-like
      validator** (i.e., tester function returning an object that is neither a
      :class:`bool` *nor* implicitly convertible into a :class:`bool`).
            '''

            # Object returned by validating this object against that callable.
            is_obj_valid = is_valid(obj)

            # If that object is a boolean, return that object as is.
            if isinstance(is_obj_valid, bool):
                return is_obj_valid
            # Else, that object is *NOT* a boolean.

            # "True" *ONLY* if that object is a bool-like (i.e., object whose
            # class defines the __bool__() and/or __len__() dunder methods).
            #
            # Note that we intentionally avoid the Easier to Ask for Permission
            # than Forgiveness (EAFP) approach typically favoured by the Python
            # community for coercing types. Namely, we avoid doing this:
            #    # Attempt to coerce this boolean into a non-boolean.
            #    try:
            #        is_obj_valid_bool = bool(is_obj_valid)
            #    except Exception as exception:
            #        raise SomeBeartypeException(...) from exception
            #
            # Why? Because the bool() constructor is overly permissive to the
            # point of being *FRANKLY BROKEN.* Why? Because that constructor
            # *NEVER* raises an exception (unless the class of that object
            # defines a __bool__() dunder method raising an exception). Why?
            # Because that constructor implicitly coerces *ALL* objects whose
            # classes define *NO* __bool__() dunder method to "True" except for
            # the following, which the bool() constructor explicitly detects
            # and hard-codes to be coerced to "False":
            # * The "None" singleton.
            # * The "False" singleton.
            # * Numeric 0 across all numeric types, including:
            #   * Integer 0.
            #   * Floating-point 0.0.
            # * Empty containers across all container types, including:
            #   * The empty tuple singleton (i.e., "()").
            #   * The empty string singleton (i.e., "''").
            #   * Any empty list (e.g., "[]").
            #
            # The proof is in the gelatinous spaghetti code:
            #     >>> class OhMyGods(object): pass
            #     >>> bool(OhMyGods())
            #     True  # <-- WHAT THE HECK IS THIS, GUIDO. SRSLY, BRO. SRSLY.
            #
            # This is, of course, unbelievable. This is, of course, all true.
            # What is this, Guido? Visual Basic in my Python? *facepalm*
            #
            # Note also that there are several means of testing for booliness.
            # The obvious approach of calling getattr() is also the slowest,
            # because getattr() internally performs the EAFP approach and
            # exception handling in Python is known to be an obvious bottleneck.
            # Ergo, we intentionally avoid doing this:
            #     is_obj_valid_bool_method = getattr(is_obj_valid, '__bool__', None)
            #
            # Ideally, we would instead defer to a beartype-specific fast
            # caching protocol that also internally performs a similar getattr()
            # call wrapped within caching logic that amortizes the cost of that
            # call across all isinstance() calls passed an object of that same
            # type. Since there exists *NO* standard "SupportsBool" protocol,
            # we would then trivially define our own like so:
            #     from beartype.typing import Protocol
            #     class SupportsBool(Protocol):
            #         def __bool__(self) -> bool: ...
            #
            # Surprisingly, that fails. Why? Because the bool() constructor
            # internally coerces objects into booleans like so:
            # * If the passed object defines the __bool__() dunder method, that
            #   constructor defers to that method.
            # * Else if the passed object defines the __len__() dunder method,
            #   that constructor defers to that method.
            # * Else if the passed object is one of several hard-coded objects
            #   evaluating to "False", that constructor returns "False".
            # * Else, that constructor returns "True".
            #
            # To handle the first two cases, we instead:
            # * Define both our own "SupportsBool" and "SupportsLen" protocols.
            # * Decide whether that object is bool-like by deferring to those
            #   protocols.
            is_obj_valid_boollike = isinstance(is_obj_valid, _BoolLike)  # pyright: ignore

            # If that object is *NOT* bool-like, raise an exception.
            if not is_obj_valid_boollike:
                #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                # CAUTION: Synchronize with the exception raised below, please.
                #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                raise BeartypeValeValidationException(
                    f'Validator {get_repr()} '
                    f'return value {repr(is_obj_valid)} not bool-like '
                    f'(i.e., instance of neither "bool" nor '
                    f'class defining __bool__() or __len__() dunder methods) '
                    f'for subject object:\n{represent_object(obj)}'
                )
            # Else, that object is bool-like.

            # Boolean coerced from this non-boolean via the __bool__() or
            # __len__() dunder methods declared by the type of this non-boolean,
            # initialized to "False" for safety.
            is_obj_valid_bool = False

            # Attempt to perform this coercion.
            try:
                is_obj_valid_bool = bool(is_obj_valid)
            # If whichever of the __bool__() or __len__() dunder methods is
            # called by the above bool() constructor raises an exception, wrap
            # that exception in a higher-level @beartype exception.
            #
            # Note that this is *NOT* simply an uncommon edge case. In
            # particular, the Pandas "DataFrame" type defines a __bool__()
            # dunder method that unconditionally raises an exception. *facepalm*
            except Exception as exception:
                #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                # CAUTION: Synchronize with the exception raised above, please.
                #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                raise BeartypeValeValidationException(
                    f'Validator {get_repr()} '
                    f'return value {repr(is_obj_valid)} erroneously bool-like '
                    f'(i.e., instance of class defining __bool__() or __len__() '
                    f'dunder methods raising unexpected exception) '
                    f'for subject object:\n{represent_object(obj)}'
                ) from exception

            # Return this boolean.
            return is_obj_valid_bool

        # ..................{ VALIDATOR                      }..................
        # Dictionary mapping from the name to value of each local attribute
        # referenced in the "is_valid_code" snippet defined below.
        is_valid_code_locals: LexicalScope = {}

        # Name of a new parameter added to the signature of each
        # @beartype-decorated wrapper function whose value is this validator,
        # enabling this validator to be called directly in the body of those
        # functions *WITHOUT* imposing additional stack frames.
        is_valid_attr_name = add_func_scope_attr(
            attr=_is_valid_bool, func_scope=is_valid_code_locals)

        # One one-liner to rule them all and in "pdb" bind them.
        return BeartypeValidator(
            is_valid=_is_valid_bool,
            # Python code snippet calling this validator (via this new
            # parameter), passed an object to be interpolated into this snippet
            # by downstream logic.
            is_valid_code=f'{is_valid_attr_name}({{obj}})',
            is_valid_code_locals=is_valid_code_locals,
            get_repr=get_repr,
        )
