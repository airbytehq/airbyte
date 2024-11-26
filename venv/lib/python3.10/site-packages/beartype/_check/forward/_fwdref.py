#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **forward reference** (i.e., classes and callables deferring the
resolution of a stringified type hint referencing an attribute that has yet to
be defined and annotating a class or callable decorated by the
:func:`beartype.beartype` decorator) utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintForwardRefException
from beartype.typing import (
    NoReturn,
    Optional,
    Type,
)
from beartype._data.hint.datahinttyping import (
    LexicalScope,
    TupleTypes,
)
from beartype._check.forward.fwdtype import bear_typistry
from beartype._util.cache.utilcachecall import (
    callable_cached,
    property_cached,
)
from beartype._util.cls.utilclsmake import make_type

# ....................{ METACLASSES                        }....................
#FIXME: Unit test us up, please.
class _BeartypeForwardRefMeta(type):
    '''
    **Forward reference metaclass** (i.e., metaclass of the
    :class:`._BeartypeForwardRefABC` superclass deferring the resolution of a
    stringified type hint referencing an attribute that has yet to be defined
    and annotating a class or callable decorated by the
    :func:`beartype.beartype` decorator).

    This metaclass memoizes each **forward reference** (i.e.,
    :class:`._BeartypeForwardRefABC` instance) according to the fully-qualified
    name of the attribute referenced by that forward reference. Doing so ensures
    that only the first :class:`._BeartypeForwardRefABC` instance referring to a
    unique attribute is required to dynamically resolve that attribute at
    runtime; all subsequent :class:`._BeartypeForwardRefABC` instances referring
    to the same attribute transparently reuse the attribute previously resolved
    by the first such instance, effectively reducing the time cost of resolving
    forward references to a constant-time operation with negligible constants.

    This metaclass dynamically and efficiently resolves each forward reference
    in a just-in-time (JIT) manner on the first :func:`isinstance` call whose
    second argument is that forward reference. Forward references *never* passed
    to the :func:`isinstance` builtin are *never* resolved, which is good.
    '''

    # ....................{ DUNDERS                        }....................
    def __getattr__(  # type: ignore[misc]
        cls, hint_name: str) -> Type['_BeartypeForwardRefIndexableABC']:
        '''
        **Fully-qualified forward reference subclass** (i.e.,
        :class:`._BeartypeForwardRefABC` subclass whose metaclass is this
        metaclass and whose :attr:`._BeartypeForwardRefABC.__beartype_name__` class
        variable is the fully-qualified name of an external class).

        This dunder method creates and returns a new forward reference subclass
        referring to an external class whose name is concatenated from (in
        order):

        #. The fully-qualified name of the external package or module referred
           to by the passed forward reference subclass.
        #. The passed unqualified basename, presumably referring to a
           subpackage, submodule, or class of that external package or module.

        Parameters
        ----------
        cls : Type[_BeartypeForwardRefABC]
            Forward reference subclass to concatenate this basename against.
        hint_name : str
            Unqualified basename to be concatenated against this forward
            reference subclass.

        Returns
        -------
        Type['_BeartypeForwardRefIndexableABC']
            Fully-qualified forward reference subclass concatenated as described
            above.
        '''

        #FIXME: Alternately, we might consider explicitly:
        #* Defining the set of *ALL* known dunder attributes (e.g., methods,
        #  class variables). This is non-trivial and error-prone, due to the
        #  introduction of new dunder attributes across Python versions.
        #* Detecting whether this "hint_name" is in that set.
        #
        #That would have the advantage of supporting forward references
        #containing dunder attributes. Until someone actually wants to do that,
        #however, let's avoid doing that. The increase in fragility is *BRUTAL*.

        # If this unqualified basename is that of a non-existent dunder
        # attribute both prefixed *AND* suffixed by the magic substring "__",
        # raise the standard "AttributeError" exception.
        if (
            hint_name.startswith('__') and
            hint_name.endswith('__')
        ):
            raise AttributeError(
                f'Forward reference proxy dunder attribute '
                f'"{cls.__name__}.{hint_name}" not found.'
            )
        # Else, this unqualified basename is *NOT* that of a non-existent dunder
        # attribute.

        # Return a new fully-qualified forward reference subclass concatenated
        # as described above.
        return make_forwardref_indexable_subtype(
            cls.__beartype_scope_name__,  # type: ignore[arg-type]
            f'{cls.__beartype_name__}.{hint_name}',
        )


    def __instancecheck__(  # type: ignore[misc]
        cls: Type['_BeartypeForwardRefABC'],  # pyright: ignore[reportGeneralTypeIssues]
        obj: object,
    ) -> bool:
        '''
        :data:`True` only if the passed object is an instance of the external
        class referenced by the passed **forward reference subclass** (i.e.,
        :class:`._BeartypeForwardRefABC` subclass whose metaclass is this
        metaclass and whose :attr:`._BeartypeForwardRefABC.__beartype_name__`
        class variable is the fully-qualified name of that external class).

        Parameters
        ----------
        cls : Type[_BeartypeForwardRefABC]
            Forward reference subclass to test this object against.
        obj : object
            Arbitrary object to be tested as an instance of the external class
            referenced by this forward reference subclass.

        Returns
        -------
        bool
            :data:`True` only if this object is an instance of the external
            class referenced by this forward reference subclass.
        '''

        # Return true only if this forward reference subclass insists that this
        # object satisfies the external class referenced by this subclass.
        return cls.__beartype_is_instance__(obj)


    def __subclasscheck__(  # type: ignore[misc]
        cls: Type['_BeartypeForwardRefABC'],  # pyright: ignore[reportGeneralTypeIssues]
        obj: object,
    ) -> bool:
        '''
        :data:`True` only if the passed object is a subclass of the external
        class referenced by the passed **forward reference subclass** (i.e.,
        :class:`._BeartypeForwardRefABC` subclass whose metaclass is this
        metaclass and whose :attr:`._BeartypeForwardRefABC.__beartype_name__`
        class variable is the fully-qualified name of that external class).

        Parameters
        ----------
        cls : Type[_BeartypeForwardRefABC]
            Forward reference subclass to test this object against.
        obj : object
            Arbitrary object to be tested as a subclass of the external class
            referenced by this forward reference subclass.

        Returns
        -------
        bool
            :data:`True` only if this object is a subclass of the external class
            referenced by this forward reference subclass.
        '''

        # Return true only if this forward reference subclass insists that this
        # object is an instance of the external class referenced by this
        # subclass.
        return cls.__beartype_is_subclass__(obj)


    def __repr__(  # type: ignore[misc]
        cls: Type['_BeartypeForwardRefABC'],  # pyright: ignore[reportGeneralTypeIssues]
    ) -> str:
        '''
        Machine-readable string representing this forward reference subclass.
        '''

        # Machine-readable representation to be returned.
        cls_repr = (
            f'{cls.__name__}('
              f'__beartype_scope_name__={repr(cls.__beartype_scope_name__)}'
            f', __beartype_name__={repr(cls.__beartype_name__)}'
        )

        # If this is a subscripted forward reference subclass, append additional
        # metadata representing this subscription.
        #
        # Ideally, we would test whether this is a subclass of the
        # "_BeartypeForwardRefIndexedABC" superclass as follows:
        #     if issubclass(cls, _BeartypeForwardRefIndexedABC):
        #
        # Sadly, doing so invokes the __subclasscheck__() dunder method defined
        # above, which invokes the
        # _BeartypeForwardRefABC.__beartype_is_subclass__() method defined
        # above, which tests the type referred to by this subclass rather than
        # this subclass itself. In short, this is why you play with madness.
        try:
            cls_repr += (
                f', __beartype_args__={repr(cls.__beartype_args__)}'
                f', __beartype_kwargs__={repr(cls.__beartype_kwargs__)}'
            )
        # If doing so fails with the expected "AttributeError", then this is
        # *NOT* a subscripted forward reference subclass. In this avoid,
        # silently ignore this common case. *sigh*
        except AttributeError:
            pass

        # Close this representation.
        cls_repr += ')'

        # Return this representation.
        return cls_repr

    # ....................{ PROPERTIES                     }....................
    @property  # type: ignore[misc]
    @property_cached
    def __beartype_type__(cls) -> type:
        '''
        Type hint referenced by this forward reference subclass.

        This class property is memoized on its first access for efficiency.
        '''

        # Fully-qualified name of that class, defined as either...
        type_name = (
            # If that name already contains one or more "." delimiters and
            # is thus presumably already fully-qualified, that name as is;
            cls.__beartype_name__
            if '.' in cls.__beartype_name__ else  # type: ignore[operator]
            # Else, that name contains *NO* "." delimiters and is thus
            # unqualified. In this case, canonicalize that name into a
            # fully-qualified name relative to the fully-qualified name of
            # the scope presumably declaring that class.
            f'{cls.__beartype_scope_name__}.{cls.__beartype_name__}'
        )

        # Resolve that class by deferring to our existing "bear_typistry"
        # dictionary, which already performs lookup-based resolution and
        # caching of arbitrary forward references at runtime.
        return bear_typistry[type_name]

# ....................{ SUPERCLASSES                       }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: The names of *ALL* class variables declared below *MUST* be both:
# * Prefixed by "__beartype_".
# * Suffixed by "__".
# If this is *NOT* done, these variables could induce a namespace conflict with
# user-defined subpackages, submodules, and classes of the same names
# concatenated via the _BeartypeForwardRefMeta.__getattr__() dunder method.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

#FIXME: Unit test us up, please.
class _BeartypeForwardRefABC(object, metaclass=_BeartypeForwardRefMeta):
    '''
    Abstract base class (ABC) of all **forward reference subclasses** (i.e.,
    classes whose :class:`._BeartypeForwardRefMeta` metaclass defers the
    resolution of stringified type hints referencing actual type hints that have
    yet to be defined).

    Caveats
    ----------
    **This ABC prohibits instantiation.** This ABC *only* exists to sanitize,
    simplify, and streamline the definition of subclasses passed as the second
    parameter to the :func:`isinstance` builtin, whose
    :class:`._BeartypeForwardRefMeta.__instancecheck__` dunder method then
    implicitly resolves the forward references encapsulated by those subclasses.
    The :func:`.make_forwardref_subtype` function dynamically creates and
    returns one concrete subclass of this ABC for each unique forward reference
    required by the :func:`beartype.beartype` decorator, whose :attr:`hint_name`
    class variable is the name of the attribute referenced by that reference.
    '''

    # ....................{ PRIVATE ~ class vars           }....................
    __beartype_scope_name__: str = None  # type: ignore[assignment]
    '''
    Fully-qualified name of the lexical scope to which the type hint referenced
    by this forward reference subclass is relative if that type hint is relative
    (i.e., if :attr:`__beartype_name__` is relative) *or* ignored otherwise
    (i.e., if :attr:`__beartype_name__` is absolute).
    '''


    __beartype_name__: str = None  # type: ignore[assignment]
    '''
    Absolute (i.e., fully-qualified) or relative (i.e., unqualified) name of the
    type hint referenced by this forward reference subclass.
    '''


    # __beartype_type__: Optional[type] = None
    # '''
    # Type hint referenced by this forward reference subclass if this subclass has
    # already been passed at least once as the second parameter to the
    # :func:`isinstance` builtin (i.e., as the first parameter to the
    # :meth:`._BeartypeForwardRefMeta.__instancecheck__` dunder method and
    # :meth:`is_instance` method) *or* :data:`None` otherwise.
    #
    # Note that this class variable is an optimization reducing space and time
    # complexity for subsequent lookup of this same type hint.
    # '''

    # ....................{ INITIALIZERS                   }....................
    def __new__(cls, *args, **kwargs) -> NoReturn:
        '''
        Prohibit instantiation by unconditionally raising an exception.
        '''

        # Instantiatable. It's a word or my username isn't @UncleBobOnAStick.
        raise BeartypeDecorHintForwardRefException(
            f'{repr(_BeartypeForwardRefABC)} subclass '
            f'{repr(cls)} not instantiatable.'
        )

    # ....................{ PRIVATE ~ testers              }....................
    @classmethod
    def __beartype_is_instance__(cls, obj: object) -> bool:
        '''
        :data:`True` only if the passed object is an instance of the external
        class referred to by this forward reference.

        Parameters
        ----------
        obj : object
            Arbitrary object to be tested.

        Returns
        -------
        bool
            :data:`True` only if this object is an instance of the external
            class referred to by this forward reference subclass.
        '''

        # # Resolve the external class referred to by this forward reference and
        # # permanently store that class in the "__beartype_type__" variable.
        # cls.__beartype_resolve_type__()

        # Return true only if this object is an instance of the external class
        # referenced by this forward reference.
        return isinstance(obj, cls.__beartype_type__)  # type: ignore[arg-type]


    @classmethod
    def __beartype_is_subclass__(cls, obj: object) -> bool:
        '''
        :data:`True` only if the passed object is a subclass of the external
        class referred to by this forward reference.

        Parameters
        ----------
        obj : object
            Arbitrary object to be tested.

        Returns
        -------
        bool
            :data:`True` only if this object is a subclass of the external class
            referred to by this forward reference subclass.
        '''

        # # Resolve the external class referred to by this forward reference and
        # # permanently store that class in the "__beartype_type__" variable.
        # cls.__beartype_resolve_type__()

        # Return true only if this object is a subclass of the external class
        # referenced by this forward reference.
        return issubclass(obj, cls.__beartype_type__)  # type: ignore[arg-type]

    # ....................{ PRIVATE ~ resolvers            }....................
    #FIXME: [SPEED] Optimize this by refactoring this into a cached class
    #property defined on the metaclass of the superclass instead. Since doing so
    #is a bit non-trivial and nobody particularly cares, the current naive
    #approach certainly suffices for now. *sigh*
    #
    #On doing so, note that we'll also need to disable this line below:
    #    forwardref_subtype.__beartype_type__ = None  # pyright: ignore[reportGeneralTypeIssues]
    # @classmethod
    # def __beartype_resolve_type__(cls) -> None:
    #     '''
    #     **Resolve** (i.e., dynamically lookup) the external class referred to by
    #     this forward reference and permanently store that class in the
    #     :attr:`__beartype_type__` class variable for subsequent lookup.
    #
    #     Caveats
    #     -------
    #     This method should *always* be called before accessing the
    #     :attr:`__beartype_type__` class variable, which should *always* be
    #     assumed to be :data:`None` before calling this method.
    #     '''
    #
    #     # If the external class referenced by this forward reference has yet to
    #     # be resolved, do so now.
    #     if cls.__beartype_type__ is None:
    #         # Fully-qualified name of that class, defined as either...
    #         type_name = (
    #             # If that name already contains one or more "." delimiters and
    #             # is thus presumably already fully-qualified, that name as is;
    #             cls.__beartype_name__
    #             if '.' in cls.__beartype_name__ else
    #             # Else, that name contains *NO* "." delimiters and is thus
    #             # unqualified. In this case, canonicalize that name into a
    #             # fully-qualified name relative to the fully-qualified name of
    #             # the scope presumably declaring that class.
    #             f'{cls.__beartype_scope_name__}.{cls.__beartype_name__}'
    #         )
    #
    #         # Resolve that class by deferring to our existing "bear_typistry"
    #         # dictionary, which already performs lookup-based resolution and
    #         # caching of arbitrary forward references at runtime.
    #         cls.__beartype_type__ = bear_typistry[type_name]
    #     # Else, that class has already been resolved.
    #     #
    #     # In either case, that class is now resolved.

# ....................{ SUPERCLASSES ~ index               }....................
#FIXME: Unit test us up, please.
class _BeartypeForwardRefIndexedABC(_BeartypeForwardRefABC):
    '''
    Abstract base class (ABC) of all **subscripted forward reference
    subclasses** (i.e., classes whose :class:`._BeartypeForwardRefMeta`
    metaclass defers the resolution of stringified type hints referencing actual
    type hints that have yet to be defined, subscripted by any arbitrary
    positional and keyword parameters).

    Subclasses of this ABC typically encapsulate user-defined generics that have
    yet to be declared (e.g., ``"MuhGeneric[int]"``).

    Caveats
    ----------
    **This ABC currently ignores subscription.** Technically, this ABC *does*
    store all positional and keyword parameters subscripting this forward
    reference. Pragmatically, this ABC otherwise silently ignores these
    parameters by deferring to the superclass :meth:`.is_instance` method (which
    reduces to the trivial :func:`isinstance` call). Why? Because **generics**
    (i.e., :class:`typing.Generic` subclasses) themselves behave in the exact
    same way at runtime.
    '''

    # ....................{ PRIVATE ~ class vars           }....................
    __beartype_args__: tuple = None  # type: ignore[assignment]
    '''
    Tuple of all positional arguments subscripting this forward reference.
    '''


    __beartype_kwargs__: LexicalScope = None  # type: ignore[assignment]
    '''
    Dictionary of all keyword arguments subscripting this forward reference.
    '''


#FIXME: Unit test us up, please.
class _BeartypeForwardRefIndexableABC(_BeartypeForwardRefABC):
    '''
    Abstract base class (ABC) of all **subscriptable forward reference
    subclasses** (i.e., classes whose :class:`._BeartypeForwardRefMeta`
    metaclass defers the resolution of stringified type hints referencing actual
    type hints that have yet to be defined, transparently permitting these type
    hints to be subscripted by any arbitrary positional and keyword parameters).
    '''

    # ....................{ DUNDERS                        }....................
    @classmethod
    def __class_getitem__(cls, *args, **kwargs) -> (
        Type[_BeartypeForwardRefIndexedABC]):
        '''
        Create and return a new **subscripted forward reference subclass**
        (i.e., concrete subclass of the :class:`._BeartypeForwardRefIndexedABC`
        abstract base class (ABC) deferring the resolution of the type hint with
        the passed name, subscripted by the passed positional and keyword
        arguments).

        This dunder method enables this forward reference subclass to
        transparently masquerade as any subscriptable type hint factory,
        including subscriptable user-defined generics that have yet to be
        declared (e.g., ``"MuhGeneric[int]"``).

        This dunder method is intentionally *not* memoized (e.g., by the
        :func:`callable_cached` decorator). Ideally, this dunder method *would*
        be memoized. Sadly, there exists no means of efficiently caching either
        non-variadic or variadic keyword arguments. Although technically
        feasible, doing so imposes practical costs defeating the entire point of
        memoization.
        '''

        # Subscripted forward reference to be returned.
        #
        # Note that parameters *MUST* be passed positionally to the memoized
        # _make_forwardref_subtype() factory function.
        forwardref_indexed_subtype: Type[_BeartypeForwardRefIndexedABC] = (
            _make_forwardref_subtype(  # type: ignore[assignment]
                scope_name=cls.__beartype_scope_name__,
                hint_name=cls.__beartype_name__,
                type_bases=_BeartypeForwardRefIndexedABC_BASES,
            ))

        # Classify the arguments subscripting this forward reference.
        forwardref_indexed_subtype.__beartype_args__ = args  # pyright: ignore[reportGeneralTypeIssues]
        forwardref_indexed_subtype.__beartype_kwargs__ = kwargs  # pyright: ignore[reportGeneralTypeIssues]

        # Return this subscripted forward reference.
        return forwardref_indexed_subtype

# ....................{ PRIVATE ~ tuples                   }....................
_BeartypeForwardRefIndexableABC_BASES = (_BeartypeForwardRefIndexableABC,)
'''
1-tuple containing *only* the :class:`._BeartypeForwardRefIndexableABC`
superclass to reduce space and time consumption.
'''


_BeartypeForwardRefIndexedABC_BASES = (_BeartypeForwardRefIndexedABC,)
'''
1-tuple containing *only* the :class:`._BeartypeForwardRefIndexedABC`
superclass to reduce space and time consumption.
'''

# ....................{ FACTORIES                          }....................
@callable_cached
def make_forwardref_indexable_subtype(
    scope_name: str, hint_name: str) -> Type[_BeartypeForwardRefIndexableABC]:
    '''
    Create and return a new **subscriptable forward reference subclass** (i.e.,
    concrete subclass of the :class:`._BeartypeForwardRefIndexableABC`
    abstract base class (ABC) deferring the resolution of the type hint with the
    passed name transparently permitting this type hint to be subscripted by any
    arbitrary positional and keyword parameters).

    Parameters
    ----------
    scope_name : str
        Absolute (i.e., fully-qualified) name of the lexical scope to which this
        type hint is relative.
    hint_name : str
        Fully-qualified name of the type hint to be referenced.

    This factory is memoized for efficiency.

    Returns
    ----------
    Type[_BeartypeForwardRefIndexableABC]
        Subscriptable forward reference subclass referencing this type hint.
    '''

    # Subscriptable forward reference to be returned.
    #
    # Note that parameters *MUST* be passed positionally to the memoized
    # _make_forwardref_subtype() factory function.
    return _make_forwardref_subtype(  # type: ignore[return-value]
        scope_name=scope_name,
        hint_name=hint_name,
        type_bases=_BeartypeForwardRefIndexableABC_BASES,
    )

# ....................{ PRIVATE ~ factories                }....................
def _make_forwardref_subtype(
    scope_name: str, hint_name: str, type_bases: TupleTypes) -> Type[
    _BeartypeForwardRefABC]:
    '''
    Create and return a new **forward reference subclass** (i.e., concrete
    subclass of the passed abstract base class (ABC) deferring the resolution of
    the type hint with the passed name transparently).

    This factory is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as *all* higher-level public factories
    calling this private factory are themselves already memoized.

    Parameters
    ----------
    scope_name : str
        Absolute (i.e., fully-qualified) name of the lexical scope to which this
        type hint is relative.
    hint_name : str
        Absolute (i.e., fully-qualified) or relative (i.e., unqualified) name of
        the type hint referenced by this forward reference subclass.
    type_bases : Tuple[type, ...]
        Tuple of all base classes to be inherited by this forward reference
        subclass. For simplicity, this *must* be a 1-tuple
        ``(type_base,)`` where ``type_base`` is a
        :class:`._BeartypeForwardRefIndexableABC` subclass.

    Returns
    ----------
    Type[_BeartypeForwardRefIndexableABC]
        Forward reference subclass referencing this type hint.
    '''
    assert isinstance(hint_name, str), f'{repr(hint_name)} not string.'
    assert isinstance(scope_name, str), f'{repr(scope_name)} not string.'
    assert len(type_bases) == 1, (
        f'{repr(type_bases)} not 1-tuple of a single superclass.')

    # Fully-qualified module name *AND* unqualified basename of the type hint
    # referenced by this forward reference subclass. Specifically, if the name
    # of this type hint is:
    # * Fully-qualified:
    #   * This module name is the substring of this name preceding the last "."
    #     delimiter in this name.
    #   * This basename is the substring of this name following the last "."
    #     delimiter in this name.
    # * Unqualified:
    #   * This module name is the empty string and thus ignorable.
    #   * This basename is this name as is.
    type_module_name, _, type_name = hint_name.rpartition('.')

    # If this module name is the empty string, this type hint is a relative
    # forward reference relative to the passed fully-qualified name of the
    # lexical scope. In this case, that scope should be the desired module.
    if not type_module_name:
        type_module_name = scope_name
    # Else, this module name is non-empty.

    # Forward reference subclass to be returned.
    forwardref_subtype: Type[_BeartypeForwardRefIndexableABC] = make_type(
        type_name=type_name,
        type_module_name=type_module_name,
        type_bases=type_bases,
    )

    # Classify passed parameters with this subclass.
    forwardref_subtype.__beartype_name__ = hint_name  # pyright: ignore[reportGeneralTypeIssues]
    forwardref_subtype.__beartype_scope_name__ = scope_name  # pyright: ignore[reportGeneralTypeIssues]

    # Nullify all remaining class variables of this subclass for safety.
    # forwardref_subtype.__beartype_type__ = None  # pyright: ignore[reportGeneralTypeIssues]

    # Return this subclass.
    return forwardref_subtype
