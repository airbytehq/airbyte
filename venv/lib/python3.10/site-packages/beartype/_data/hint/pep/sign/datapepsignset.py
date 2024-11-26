#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **type hint sign sets** (i.e., frozen set globals aggregating
instances of the :class:`beartype._data.hint.pep.sign.datapepsigncls.HintSign`
class, enabling efficient categorization of signs as belonging to various
categories of type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._data.hint.pep.sign.datapepsigns import (
    HintSignAbstractSet,
    HintSignAnnotated,
    HintSignAny,
    HintSignAsyncContextManager,
    HintSignAsyncGenerator,
    HintSignAsyncIterator,
    HintSignAsyncIterable,
    HintSignAwaitable,
    HintSignBinaryIO,
    HintSignByteString,
    HintSignCallable,
    HintSignChainMap,
    HintSignCollection,
    HintSignConcatenate,
    HintSignContainer,
    HintSignContextManager,
    HintSignCoroutine,
    HintSignCounter,
    HintSignDataclassInitVar,
    HintSignDefaultDict,
    HintSignDeque,
    HintSignDict,
    HintSignFinal,
    HintSignForwardRef,
    HintSignFrozenSet,
    HintSignGenerator,
    HintSignGeneric,
    HintSignHashable,
    HintSignIO,
    HintSignItemsView,
    HintSignIterable,
    HintSignIterator,
    HintSignKeysView,
    HintSignList,
    HintSignLiteral,
    HintSignLiteralString,
    HintSignMapping,
    HintSignMappingView,
    HintSignMatch,
    HintSignMutableMapping,
    HintSignMutableSequence,
    HintSignMutableSet,
    HintSignNewType,
    HintSignNumpyArray,
    HintSignNone,
    HintSignOptional,
    HintSignOrderedDict,
    HintSignPanderaAny,
    HintSignParamSpec,
    HintSignPattern,
    HintSignProtocol,
    HintSignReversible,
    HintSignSelf,
    HintSignSequence,
    HintSignSet,
    HintSignSized,
    HintSignTextIO,
    HintSignTuple,
    HintSignType,
    HintSignTypedDict,
    HintSignTypeGuard,
    HintSignTypeVar,
    HintSignUnion,
    HintSignValuesView,
)

# ....................{ SIGNS ~ bare                       }....................
HINT_SIGNS_BARE_IGNORABLE = frozenset((
    # ..................{ PEP 484                            }..................
    # The "Any" singleton is semantically synonymous with the ignorable
    # PEP-noncompliant "beartype.cave.AnyType" and hence "object" types.
    HintSignAny,

    # The "Generic" superclass imposes no constraints and is thus also
    # semantically synonymous with the ignorable PEP-noncompliant
    # "beartype.cave.AnyType" and hence "object" types. Since PEP
    # 484 stipulates that *ANY* unsubscripted subscriptable PEP-compliant
    # singleton including "typing.Generic" semantically expands to that
    # singelton subscripted by an implicit "Any" argument, "Generic"
    # semantically expands to the implicit "Generic[Any]" singleton.
    HintSignGeneric,

    # The unsubscripted "Optional" singleton semantically expands to the
    # implicit "Optional[Any]" singleton by the same argument. Since PEP
    # 484 also stipulates that all "Optional[t]" singletons semantically expand
    #     to "Union[t, type(None)]" singletons for arbitrary arguments "t",
    #     "Optional[Any]" semantically expands to merely "Union[Any,
    #     type(None)]". Since all unions subscripted by "Any" semantically
    #     reduce to merely "Any", the "Optional" singleton also reduces to
    # merely "Any".
    #
    # This intentionally excludes "Optional[type(None)]", which the "typing"
    # module physically reduces to merely "type(None)". *shrug*
    HintSignOptional,

    # The unsubscripted "Union" singleton semantically expands to the implicit
    # "Union[Any]" singleton by the same argument. Since PEP 484 stipulates that
    # a union of one type semantically reduces to only that type, "Union[Any]"
    # semantically reduces to merely "Any". Despite their semantic equivalency,
    # however, these objects remain syntactically distinct with respect to
    # object identification: e.g.,
    #     >>> Union is not Union[Any]
    #     True
    #     >>> Union is not Any
    #     True
    #
    # This intentionally excludes:
    #
    # * The "Union[Any]" and "Union[object]" singletons, since the "typing"
    #   module physically reduces:
    #   * "Union[Any]" to merely "Any" (i.e., "Union[Any] is Any"), which
    #     this frozen set already contains.
    #   * "Union[object]" to merely "object" (i.e., "Union[object] is
    #     object"), which this frozen set also already contains.
    # * "Union" singleton subscripted by one or more ignorable type hints
    #   contained in this set (e.g., "Union[Any, bool, str]"). Since there exist
    #   a countably infinite number of these subscriptions, these subscriptions
    #   *CANNOT* be explicitly listed in this set. Instead, these subscriptions
    #   are dynamically detected by the high-level
    #   beartype._util.hint.pep.utilhinttest.is_hint_ignorable() tester function
    #   and thus referred to as deeply ignorable type hints.
    HintSignUnion,

    # ..................{ PEP 544                            }..................
    # Note that ignoring the "typing.Protocol" superclass is vital here. For
    # unknown and presumably uninteresting reasons, *ALL* possible objects
    # satisfy this superclass. Ergo, this superclass is synonymous with the
    # "object" root superclass: e.g.,
    #     >>> import typing as t
    #     >>> isinstance(object(), t.Protocol)
    #     True
    #     >>> isinstance('wtfbro', t.Protocol)
    #     True
    #     >>> isinstance(0x696969, t.Protocol)
    #     True
    HintSignProtocol,
))
'''
Frozen set of all **bare ignorable signs** (i.e., arbitrary objects uniquely
identifying unsubscripted type hints that are unconditionally ignorable by the
:func:`beartype.beartype` decorator).
'''

# ....................{ SETS ~ kind                        }....................
HINT_SIGNS_CALLABLE_PARAMS = frozenset((
    # ..................{ PEP 612                            }..................
    HintSignConcatenate,
    HintSignParamSpec,
))
'''
Frozen set of all **callable argument signs** (i.e., arbitrary objects uniquely
identifying PEP-compliant child type hints typing the argument lists of parent
:class:`collections.abc.Callable` type hints).

This set necessarily excludes:

* **Standard callable argument lists** (e.g., ``Callable[[bool, int], str]``),
  which are specified as standard lists and thus identified by *no* signs.
* **Ellipsis callable argument lists** (e.g., ``Callable[..., str]``), which are
  specified as the ellipsis singleton and thus identified by *no* signs.
'''


HINT_SIGNS_SEQUENCE_ARGS_1 = frozenset((
    # ..................{ PEP (484|585)                      }..................
    HintSignByteString,
    HintSignList,
    HintSignMutableSequence,
    HintSignSequence,
))
'''
Frozen set of all **standard sequence signs** (i.e., arbitrary objects uniquely
identifying PEP-compliant type hints accepting exactly one subscripted type
hint argument constraining *all* items of compliant sequences, which
necessarily satisfy the :class:`collections.abc.Sequence` protocol with
guaranteed ``O(1)`` indexation across all sequence items).

This set intentionally excludes the:

* :attr:`typing.AnyStr` sign, which accepts only the :class:`str` and
  :class:`bytes` types as its sole subscripted argument, which does *not*
  unconditionally constrain *all* items (i.e., unencoded and encoded characters
  respectively) of compliant sequences but instead parametrizes this attribute.
* :attr:`typing.ByteString` sign, which accepts *no* subscripted arguments.
  :attr:`typing.ByteString` is simply an alias for the
  :class:`collections.abc.ByteString` abstract base class (ABC) and thus
  already handled by our fallback logic for supported PEP-compliant type hints.
* :attr:`typing.Deque` sign, whose compliant objects (i.e.,
  :class:`collections.deque` instances) only `guarantee O(n) indexation across
  all sequence items <collections.deque_>`__:

     Indexed access is ``O(1)`` at both ends but slows to ``O(n)`` in the
     middle. For fast random access, use lists instead.

* :attr:`typing.NamedTuple` sign, which embeds a variadic number of
  PEP-compliant field type hints and thus requires special-cased handling.
* :attr:`typing.Text` sign, which accepts *no* subscripted arguments.
  :attr:`typing.Text` is simply an alias for the builtin :class:`str` type and
  thus handled elsewhere as a PEP-noncompliant type hint.
* :attr:`typing.Tuple` sign, which accepts a variadic number of subscripted
  arguments and thus requires special-cased handling.

.. _collections.deque:
   https://docs.python.org/3/library/collections.html#collections.deque
'''


HINT_SIGNS_UNION = frozenset((
    # ..................{ PEP 484                            }..................
    HintSignOptional,
    HintSignUnion,
))
'''
Frozen set of all **union signs** (i.e., arbitrary objects uniquely identifying
:pep:`484`-compliant type hints unifying one or more subscripted type hint
arguments into a disjunctive set union of these arguments).

If the active Python interpreter targets:

* Python >= 3.9, the :attr:`typing.Optional` and :attr:`typing.Union`
  attributes are distinct.
* Python < 3.9, the :attr:`typing.Optional` attribute reduces to the
  :attr:`typing.Union` attribute, in which case this set is technically
  semantically redundant. Since tests of both object identity and set
  membership are ``O(1)``, this set incurs no significant performance penalty
  versus direct usage of the :attr:`typing.Union` attribute and is thus
  unconditionally used as is irrespective of Python version.
'''

# ....................{ SIGNS ~ origin                     }....................
HINT_SIGNS_ORIGIN_ISINSTANCEABLE = frozenset((
    # ..................{ PEP (484|585)                      }..................
    HintSignAbstractSet,
    HintSignAsyncContextManager,
    HintSignAsyncGenerator,
    HintSignAsyncIterable,
    HintSignAsyncIterator,
    HintSignAwaitable,
    HintSignByteString,
    HintSignCallable,
    HintSignChainMap,
    HintSignCollection,
    HintSignContainer,
    HintSignContextManager,
    HintSignCoroutine,
    HintSignCounter,
    HintSignDefaultDict,
    HintSignDeque,
    HintSignDict,
    HintSignFrozenSet,
    HintSignGenerator,
    HintSignHashable,
    HintSignItemsView,
    HintSignIterable,
    HintSignIterator,
    HintSignKeysView,
    HintSignList,
    HintSignMapping,
    HintSignMappingView,
    HintSignMatch,
    HintSignMutableMapping,
    HintSignMutableSequence,
    HintSignMutableSet,
    HintSignOrderedDict,
    HintSignPattern,
    HintSignReversible,
    HintSignSequence,
    HintSignSet,
    HintSignSized,
    HintSignTuple,
    HintSignType,
    HintSignValuesView,
))
'''
Frozen set of all signs uniquely identifying PEP-compliant type hints
originating from an **isinstanceable origin type** (i.e., isinstanceable class
such that *all* objects satisfying this hint are instances of this class).

All hints identified by signs in this set are guaranteed to define
``__origin__`` dunder instance variables whose values are the standard origin
types they originate from. Since any object is trivially type-checkable against
such a type by passing that object and type to the :func:`isinstance` builtin,
*all* objects annotated by hints identified by signs in this set are at least
shallowly type-checkable from wrapper functions generated by the
:func:`beartype.beartype` decorator.
'''

# ....................{ SIGNS ~ origin : args              }....................
HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_1 = frozenset((
    HintSignAbstractSet,
    HintSignAsyncContextManager,
    HintSignAsyncIterable,
    HintSignAsyncIterator,
    HintSignAwaitable,
    HintSignCollection,
    HintSignContainer,
    HintSignContextManager,
    HintSignCounter,
    HintSignDeque,
    HintSignFrozenSet,
    HintSignIterable,
    HintSignIterator,
    HintSignKeysView,
    HintSignList,
    HintSignMatch,
    HintSignMappingView,
    HintSignMutableSequence,
    HintSignMutableSet,
    HintSignPattern,
    HintSignReversible,
    HintSignSequence,
    HintSignSet,
    HintSignType,
    HintSignValuesView,
))
'''
Frozen set of all signs uniquely identifying **single-argument PEP-compliant
type hints** (i.e., type hints subscriptable by only one child type hint)
originating from an **isinstanceable origin type** (i.e., isinstanceable class
such that *all* objects satisfying this hint are instances of this class).

Note that the corresponding types in the typing module will have an ``_nparams``
instance variable with a value equal to 1.
'''


HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_2 = frozenset((
    HintSignAsyncGenerator,
    # HintSignCallable,  # defined explicitly below
    HintSignChainMap,
    HintSignDefaultDict,
    HintSignDict,
    HintSignItemsView,
    HintSignMapping,
    HintSignMutableMapping,
    HintSignOrderedDict,
))
'''
Frozen set of all signs uniquely identifying **two-argument PEP-compliant
type hints** (i.e., type hints subscriptable by exactly two child type hints)

Note that the corresponding types in the typing module will have an ``_nparams``
instance variable with a value equal to 2.
'''


HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_3 = frozenset((
    HintSignCoroutine,
    HintSignGenerator,
))
'''
Frozen set of all signs uniquely identifying **three-argument PEP-compliant
type hints** (i.e., type hints subscriptable by exactly three child type hints)

Note that the corresponding types in the typing module will have an ``_nparams``
instance variable with a value equal to 3.
'''

# ....................{ SIGNS ~ return                     }....................
HINT_SIGNS_RETURN_GENERATOR_ASYNC = frozenset((
    # ..................{ PEP (484|585)                      }..................
    HintSignAsyncGenerator,
    HintSignAsyncIterable,
    HintSignAsyncIterator,
))
'''
Frozen set of all signs uniquely identifying **PEP-compliant asynchronous
generator return type hints** (i.e., hints permissible as the return
annotations of asynchronous generators).

See Also
----------
:data:`HINT_SIGNS_RETURN_GENERATOR_SYNC`
    Further discussion.
'''


HINT_SIGNS_RETURN_GENERATOR_SYNC = frozenset((
    # ..................{ PEP (484|585)                      }..................
    HintSignGenerator,
    HintSignIterable,
    HintSignIterator,
))
'''
Frozen set of all signs uniquely identifying **PEP-compliant synchronous
generator return type hints** (i.e., hints permissible as the return
annotations of synchronous generators).

Generator callables are simply syntactic sugar for non-generator callables
returning generator objects. For this reason, generator callables *must* be
annotated as returning a type compatible with generator objects -- including:

* :data:`HintSignGenerator`, the narrowest abstract base class (ABC) to which
  all generator objects necessarily conform.
* :data:`HintSignIterator`, the immediate superclass of
  :data:`HintSignGenerator`.
* :data:`HintSignIterable`, the immediate superclass of
  :data:`HintSignIterator`.

Technically, :pep:`484` states that generator callables may only be annotated
as only returning a subscription of the :attr:`typing.Generator` factory:

    The return type of generator functions can be annotated by the generic type
    ``Generator[yield_type, send_type, return_type]`` provided by ``typing.py``
    module:

Pragmatically, official documentation for the :mod:`typing` module seemingly
*never* standardized by an existing PEP additionally states that generator
callables may be annotated as also returning a subscription of either the
:attr:`typing.Iterable` or :attr:`typing.Iterator` factories:

    Alternatively, annotate your generator as having a return type of either
    ``Iterable[YieldType]`` or ``Iterator[YieldType]``:

See Also
----------
https://github.com/beartype/beartype/issues/65#issuecomment-954468111
    Further discussion.
'''

# ....................{ SIGNS ~ type                       }....................
HINT_SIGNS_TYPE_MIMIC = frozenset((
    # ..................{ PEP 484                            }..................
    HintSignNewType,

    # ..................{ PEP 593                            }..................
    HintSignAnnotated,
))
'''
Frozen set of all signs uniquely identifying **PEP-compliant type hint mimics**
(i.e., hints maliciously masquerading as another type by explicitly overriding
their ``__module__`` dunder instance variable to that of that type).

Notably, this set contains the signs of:

* :pep:`484`-compliant :attr:`typing.NewType` type hints under Python >= 3.10,
  which badly masquerade as their first passed argument to such an extreme
  degree that they even intentionally prefix their machine-readable
  representation by the fully-qualified name of the caller's module: e.g.,

  .. code-block:: python

     # Under Python >= 3.10:
     >>> import typing
     >>> new_type = typing.NewType('List', bool)
     >>> repr(new_type)
     __main__.List   # <---- this is genuine bollocks

* :pep:`593`-compliant :attr:`typing.Annotated` type hints, which badly
  masquerade as their first subscripted argument (e.g., the :class:`int` in
  ``typing.Annotated[int, 63]``) such that the value of the ``__module__``
  attributes of these hints is that of that argument rather than their own.
  Oddly, their machine-readable representation remains prefixed by
  ``"typing."``, enabling an efficient test that also generalizes to all other
  outlier edge cases that are probably lurking about.

I have no code and I must scream.
'''

# ....................{ SETS ~ supported                   }....................
_HINT_SIGNS_SUPPORTED_SHALLOW = frozenset((
    # ..................{ PEP 484                            }..................
    HintSignTypeVar,

    # ..................{ PEP 589                            }..................
    #FIXME: Shift into "HINT_SIGNS_SUPPORTED_DEEP" *AFTER* deeply type-checking
    #typed dictionaries.
    HintSignTypedDict,

    # ..................{ PEP 591                            }..................
    HintSignFinal,

    # ..................{ PEP 647                            }..................
    HintSignTypeGuard,

    # ..................{ PEP 673                            }..................
    HintSignSelf,

    # ..................{ PEP 675                            }..................
    HintSignLiteralString,

    #FIXME: Excise us up, please. This should *NOT* be required.
    # ..................{ NON-PEP ~ lib : pandera            }..................
    # All PEP-noncompliant pandera type hints are subsequently reduced to
    # isinstanceable pandas types at hint reduction time.
    # HintSignPanderaAny,
))
'''
Frozen set of all **shallowly supported non-originative signs** (i.e., arbitrary
objects uniquely identifying PEP-compliant type hints *not* originating from an
isinstanceable type for which the :func:`beartype.beartype` decorator generates
shallow type-checking code).
'''


HINT_SIGNS_SUPPORTED_DEEP = frozenset((
    # ..................{ PEP 484                            }..................
    # Note that the "NoReturn" type hint is invalid in almost all possible
    # syntactic contexts and thus intentionally omitted here. See the
    # "datapepsigns" submodule for further commentary.
    HintSignAny,
    HintSignBinaryIO,
    HintSignForwardRef,
    HintSignIO,
    HintSignNewType,
    HintSignNone,
    HintSignTextIO,

    # Note that "typing.Union" implicitly subsumes "typing.Optional" *ONLY*
    # under Python <= 3.9. The implementations of the "typing" module under
    # those older Python versions transparently reduced "typing.Optional" to
    # "typing.Union" at runtime. Since this reduction is no longer the case,
    # both *MUST* now be explicitly listed here.
    HintSignOptional,
    HintSignUnion,

    # ..................{ PEP (484|585)                      }..................
    HintSignByteString,
    HintSignGeneric,
    HintSignList,
    HintSignMutableSequence,
    HintSignSequence,
    HintSignTuple,
    HintSignType,

    # ..................{ PEP 544                            }..................
    HintSignProtocol,

    # ..................{ PEP 557                            }..................
    HintSignDataclassInitVar,

    # ..................{ PEP 586                            }..................
    HintSignLiteral,

    # ..................{ PEP 593                            }..................
    HintSignAnnotated,

    # ..................{ NON-PEP ~ package : numpy          }..................
    HintSignNumpyArray,
))
'''
Frozen set of all **deeply supported signs** (i.e., arbitrary objects uniquely
identifying PEP-compliant type hints for which the :func:`beartype.beartype`
decorator generates deeply type-checking code).

This set contains *every* sign explicitly supported by one or more conditional
branches in the body of the
:func:`beartype._check.code.codemake.make_func_wrapper_code` function
generating code deeply type-checking the current pith against the PEP-compliant
type hint annotated by a subscription of that attribute.
'''


HINT_SIGNS_SUPPORTED = frozenset((
    # Set of all deeply supported signs.
    HINT_SIGNS_SUPPORTED_DEEP |
    # Set of all shallowly supported signs *NOT* originating from a class.
    _HINT_SIGNS_SUPPORTED_SHALLOW |
    # Set of all shallowly supported signs originating from a class.
    HINT_SIGNS_ORIGIN_ISINSTANCEABLE
))
'''
Frozen set of all **supported signs** (i.e., arbitrary objects uniquely
identifying PEP-compliant type hints).
'''
