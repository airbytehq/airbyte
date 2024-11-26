#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype** :pep:`544` **optimization layer.**

This private submodule implements a :func:`beartype.beartype``-compatible
(i.e., decorated by the :func:`typing.runtime_checkable` decorator) drop-in
replacement for :class:`typing.Protocol` that can lead to significant
performance improvements.
'''

# ....................{ TODO                               }....................
#FIXME: *YIKES.* Our "beartype.typing.Protocol" implementation is broken yet
#again -- but this time for @classmethod-decorated callables. Consider this:
#    from beartype.typing import Protocol
#    class BrokenProtocol(Protocol):
#        @classmethod
#        def broken_classmethod(cls) -> object:
#            pass
#
#Now define an arbitrary class violating that protocol:
#    class BrokenClass(object): pass
#
#Now attempt to demonstrate that this class violates that protocol:
#    >>> isinstance(BrokenClass, BrokenProtocol)
#    True  # <----- WAAAAAAAAAT
#
#This issue is almost certainly related to classmethods. We clearly never tested
#that. Classmethods clearly require explicit handling and caching. *sigh*

# ....................{ IMPORTS                            }....................
from beartype.typing._typingcache import callable_cached_minimal
from beartype._util.py.utilpyversion import (
    IS_PYTHON_AT_LEAST_3_12,
    IS_PYTHON_AT_LEAST_3_9,
)
from typing import (  # type: ignore[attr-defined]
    EXCLUDED_ATTRIBUTES,  # pyright: ignore[reportGeneralTypeIssues]
    TYPE_CHECKING,
    Any,
    Generic,
    Protocol as _ProtocolSlow,
    SupportsAbs as _SupportsAbsSlow,
    SupportsBytes as _SupportsBytesSlow,
    SupportsComplex as _SupportsComplexSlow,
    SupportsFloat as _SupportsFloatSlow,
    SupportsIndex as _SupportsIndexSlow,  # pyright: ignore[reportGeneralTypeIssues]
    SupportsInt as _SupportsIntSlow,
    SupportsRound as _SupportsRoundSlow,
    TypeVar,
    runtime_checkable,
)

# Note that we intentionally:
# * Avoid importing these type hint factories from "beartype.typing", as that
#   would induce a circular import dependency. Instead, we manually import the
#   relevant type hint factories conditionally depending on the version of the
#   active Python interpreter. *sigh*
# * Test the negation of this condition first. Why? Because mypy quietly
#   defecates all over itself if the order of these two branches is reversed.
#   Yeah. It's as bad as it sounds.
if not IS_PYTHON_AT_LEAST_3_9:
    from typing import Dict, Tuple, Type  # type: ignore[misc]
# Else, the active Python interpreter targets Python >= 3.9 and thus supports
# PEP 585. In this case, embrace non-deprecated PEP 585-compliant type hints.
else:
    Dict = dict  # type: ignore[misc]
    Tuple = tuple  # type: ignore[assignment]
    Type = type  # type: ignore[assignment]

# If the active Python interpreter was invoked by a static type checker (e.g.,
# mypy), violate privacy encapsulation. Doing so invites breakage under newer
# Python releases. Confining any potential breakage to this technically optional
# static type-checking phase minimizes the fallout by ensuring that this API
# continues to behave as expected at runtime.
#
# See also this deep typing voodoo:
#     https://github.com/python/mypy/issues/11614
if TYPE_CHECKING:
    from abc import ABCMeta as _ProtocolMeta
# Else, this interpreter was *NOT* invoked by a static type checker and is thus
# subject to looser runtime constraints. In this case, access the same metaclass
# *WITHOUT* violating privacy encapsulation.
else:
    _ProtocolMeta = type(_ProtocolSlow)

# ....................{ PRIVATE ~ constants                }....................
_PROTOCOL_ATTR_NAMES_IGNORABLE = frozenset(EXCLUDED_ATTRIBUTES)
'''
Frozen set of the names all **ignorable non-protocol attributes** (i.e.,
attributes *not* considered part of the protocol of a
:class:`beartype.typing.Protocol` subclass when passing that protocol to
the :func:`isinstance` builtin in structural subtyping checks).
'''


_T_co = TypeVar("_T_co", covariant=True)
'''
Arbitrary covariant type variable.
'''


_TT = TypeVar("_TT", bound="_CachingProtocolMeta")
'''
Arbitrary type variable bound (i.e., confined) to classes.
'''

# ....................{ PRIVATE ~ metaclasses              }....................
class _CachingProtocolMeta(_ProtocolMeta):
    '''
    **Caching protocol metaclass** (i.e., drop-in replacement for the
    private metaclass of the public :class:`typing.Protocol` superclass
    that additionally caches :meth:`class.__instancecheck__` results).

    This metaclass amortizes the `non-trivial time complexity of protocol
    validation <protocol cost_>`__ to a trivial constant-time lookup.

    .. _protocol cost:
       https://github.com/python/mypy/issues/3186#issuecomment-885718629

    Caveats
    ----------
    **This metaclass will yield unpredictable results for any object with
    one or more methods not declared by the class of that object,**
    including objects whose methods are dynamically assembled at runtime.
    This metaclass is ill-suited for such "types."

    Motivation
    ----------
    By default, :class:`typing.Protocol` subclasses are constrained to only
    be checkable by static type checkers (e.g., :mod:`mypy`). Checking a
    protocol with a runtime type checker (e.g., :mod:`beartype`) requires
    explicitly decorating that protocol with the
    :func:`typing.runtime_checkable` decorator. Why? We have no idea.

    For unknown (but probably indefensible) reasons, :pep:`544` authors
    enforced this constraint with a trivial private
    :class:`typing.Protocol` boolean instance variable imposing *no* space
    or time burden set only by the optional
    :func:`typing.runtime_checkable` decorator. Since that's demonstrably
    insane, we pretend :pep:`544` authors chose wisely by unconditionally
    decorating *all* :class:`beartype.typing.Protocol` subclasses by that
    decorator.

    Technically, any non-caching :class:`typing.Protocol` subclass can be
    effectively coerced into a caching :class:`beartype.typing.Protocol`
    protocol through inheritance: e.g.,

    .. code-block:: python

      >>> from abc import abstractmethod
      >>> from typing import Protocol
      >>> from beartype.typing import _CachingProtocolMeta, runtime_checkable
      >>> @runtime_checkable
      ... class _MyProtocol(Protocol):  # plain vanilla protocol
      ...     @abstractmethod
      ...     def myfunc(self, arg: int) -> str:
      ...         pass
      >>> @runtime_checkable  # redundant, but useful for documentation
      ... class MyProtocol(
      ...     _MyProtocol,
      ...     Protocol,
      ...     metaclass=_CachingProtocolMeta,  # caching version
      ... ):
      ...     pass
      >>> class MyImplementation:
      ...     def myfunc(self, arg: int) -> str:
      ...         return str(arg * -2 + 5)
      >>> my_thing: MyProtocol = MyImplementation()
      >>> isinstance(my_thing, MyProtocol)
      True

    Pragmatically, :class:`beartype.typing.Protocol` trivially eliminates
    *all* of the above fragile boilerplate: e.g.,

    .. code-block:: python

      >>> from beartype.typing import Protocol
      >>> class MyBearProtocol(Protocol):
      ...     @abstractmethod
      ...     def myfunc(self, arg: int) -> str:
      ...         pass
      >>> my_thing: MyBearProtocol = MyImplementation()
      >>> isinstance(my_thing, MyBearProtocol)
      True
    '''

    # ................{ CLASS VARIABLES                        }................
    _abc_inst_check_cache: Dict[type, bool]
    '''
    :func:`isinstance` **cache** (i.e., dictionary mapping from each type of any
    object previously passed as the first parameter to the :func:`isinstance`
    builtin whose second parameter was this protocol onto each boolean returned
    by that call to that builtin).
    '''

    # ................{ DUNDERS                                }................
    def __new__(
        mcls: Type[_TT],  # pyright: ignore[reportSelfClsParameterName]
        name: str,
        bases: Tuple[type, ...],
        namespace: Dict[str, Any],
        **kw: Any,
    ) -> _TT:

        # See <https://github.com/python/mypy/issues/9282>
        cls = super().__new__(mcls, name, bases, namespace, **kw)

        # If this class is *NOT* the abstract "beartype.typing.Protocol"
        # superclass defined below...
        if name != 'Protocol':
            #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # CAUTION: Synchronize this "if" conditional against the standard
            # "typing" module, which defines the exact same logic in the
            # Protocol.__init_subclass__() class method.
            #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # If it is unknown whether this class is an abstract protocol
            # directly subclassing the "Protocol" superclass *OR* a concrete
            # subclass of an abstract protocol, decide which applies now. Why?
            # Because upstream performs the same logic. Since this logic tests
            # the non-transitive dunder tuple "__bases__" of all *DIRECT*
            # superclasses of this class rather than the transitive dunder tuple
            # "__mro__" of all direct and indirect superclasses of this class,
            # upstream logic erroneously detects abstract fast @beartype
            # protocols as concrete by unconditionally reducing to:
            #     cls._is_protocol = False
            #
            # Why? Because "beartype.typing.Protocol" subclasses
            # "typing.Protocol", subclasses of "beartype.typing.Protocol" list
            # "beartype.typing.Protocol" rather than "typing.Protocol" in their
            # "__bases__" dunder tuple. Disaster, thy name is "typing"!
            if not cls.__dict__.get('_is_protocol'):
                # print(f'Protocol {cls} bases: {cls.__bases__}')
                cls._is_protocol = any(b is Protocol for b in cls.__bases__)  # type: ignore[attr-defined]

            # If this protocol is concrete rather than abstract, monkey-patch
            # this concrete protocol to be implicitly type-checkable at runtime.
            # By default, protocols are *NOT* type-checkable at runtime unless
            # explicitly decorated by this nonsensical decorator.
            #
            # Note that the abstract "beartype.typing.Protocol" superclass
            # *MUST* be explicitly excluded from consideration. Why? For unknown
            # reasons, monkey-patching that superclass as implicitly
            # type-checkable at runtime has extreme consequences throughout the
            # typing ecosystem. In particular, doing so causes *ALL*
            # non-protocol classes to be subsequently erroneously detected as
            # being PEP 544-compliant protocols: e.g.,
            #     # If we monkey-patched the "Protocol" superclass as well, then
            #     # the following snippet would insanely hold true... wat!?!?!?!
            #     >>> from typing import Protocol
            #     >>> class OhBoy(object): pass
            #     >>> issubclass(OhBoy, Protocol)
            #     True  # <-- we have now destroyed the world, folks.
            if cls._is_protocol:  # type: ignore[attr-defined]
                # print(f'Protocol {cls} mro: {cls.__mro__}')
                runtime_checkable(cls)  # pyright: ignore[reportGeneralTypeIssues]
        # Else, this class is the abstract "beartype.typing.Protocol"
        # superclass defined below. In this case, avoid dangerously
        # monkey-patching this superclass.

        # Prefixing this class member with "_abc_" is necessary to prevent
        # it from being considered part of the Protocol. See also:
        #     https://github.com/python/cpython/blob/main/Lib/typing.py
        cls._abc_inst_check_cache = {}

        # Return this caching protocol.
        return cls


    def __instancecheck__(cls, inst: Any) -> bool:
        '''
        :data:`True` only if the passed object is a **structural subtype**
        (i.e., satisfies the protocol defined by) the passed protocol.

        Parameters
        ----------
        cls : type
            :pep:`544`-compliant protocol to check this object against.
        inst : Any
            Arbitrary object to check against this protocol.

        Returns
        ----------
        bool
            :data:`True` only if this object satisfies this protocol.
        '''

        # Attempt to...
        try:
            #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # CAUTION: This *MUST* remain *SUPER* tight!! Even adding a
            # mere assertion here can add ~50% to our best-case runtime.
            #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # Return a pre-cached boolean indicating whether an object of
            # the same arbitrary type as the object passed to this call
            # satisfied the same protocol in a prior call of this method.
            return cls._abc_inst_check_cache[type(inst)]
        # If this method has yet to be passed the same protocol *AND* an
        # object of the same type as the object passed to this call...
        except KeyError:
            # If you're going to do *anything*, do it here. Try not to
            # expand the rest of this method if you can avoid it.
            inst_t = type(inst)
            bases_pass_muster = True

            for base in cls.__bases__:
                #FIXME: This branch probably erroneously matches unrelated
                #user-defined types whose names just happen to be "Generic"
                #or "Protocol". Ideally, we should tighten that up to only
                #match the actual "{beartype,}.typing.{Generic,Protocol}"
                #superclasses. Of course, note that
                #"beartype.typing.Protocol" is *NOT* "typing.Protocol', so
                #we'll want to explicitly test against both.
                if base is cls or base.__name__ in (
                    'Protocol',
                    'Generic',
                    'object',
                ):
                    continue
                if not isinstance(inst, base):
                    bases_pass_muster = False
                    break

            cls._abc_inst_check_cache[inst_t] = bases_pass_muster and (
                _check_only_my_attrs(cls, inst))

            return cls._abc_inst_check_cache[inst_t]

# ....................{ PRIVATE ~ functions                }....................
#FIXME: Docstring us up, please.
#FIXME: Comment us up, please.
def _check_only_my_attrs(cls, inst: Any, _EMPTY_DICT = {}) -> bool:

    cls_attr_name_to_value = cls.__dict__
    cls_attr_name_to_hint = cls_attr_name_to_value.get(
        '__annotations__', _EMPTY_DICT)
    cls_attr_names = (
        cls_attr_name_to_value | cls_attr_name_to_hint
        if IS_PYTHON_AT_LEAST_3_9 else
        dict(cls_attr_name_to_value, **cls_attr_name_to_hint)
    )

    # For the name of each attribute declared by this protocol class...
    for cls_attr_name in cls_attr_names:
        # If...
        if (
            # This name implies this attribute to be unignorable *AND*...
            #
            # Specifically, if this name is neither...
            not (
                # A private attribute defined by dark machinery in the
                # "ABCMeta" metaclass for abstract base classes *OR*...
                cls_attr_name.startswith('_abc_') or
                # That of an ignorable non-protocol attribute...
                cls_attr_name in _PROTOCOL_ATTR_NAMES_IGNORABLE
            # This attribute is either...
            ) and (
                # Undefined by the passed object *OR*...
                not hasattr(inst, cls_attr_name) or
                # Defined by the passed object as a "blocked" (i.e., omitted
                # from being type-checked as part of this protocol) method.
                # For unknown and indefensible reasons, PEP 544 explicitly
                # supports this fragile, unreadable, and error-prone idiom
                # enabling objects to leave methods "undefined." What this!?
                (
                    #FIXME: Unit test this up, please.
                    # A callable *AND*...
                    callable(getattr(cls, cls_attr_name, None)) and
                    # The passed object nullified this method. *facepalm*
                    getattr(inst, cls_attr_name) is None
                )
            )
        ):
            # Then the passed object violates this protocol. In this case,
            # return false.
            return False

    # Else, the passed object satisfies this protocol. In this case, return
    # true.
    return True

# ....................{ CLASSES                            }....................
# @runtime_checkable
class Protocol(
    _ProtocolSlow,
    # Force protocols to be generics. Although the standard
    # "typing.Protocol" superclass already implicitly subclasses from the
    # "typing.Generic" superclass, the non-standard
    # "typing_extensions.Protocol" superclass does *NOT*. Ergo, we force
    # this to be the case.
    Generic,  # pyright: ignore
    metaclass=_CachingProtocolMeta,
):
    '''
    :func:`beartype.beartype`-compatible (i.e., decorated by
    :func:`typing.runtime_checkable`) drop-in replacement for
    :class:`typing.Protocol` that can lead to significant performance
    improvements.

    Uses :class:`_CachingProtocolMeta` to cache :func:`isinstance` check
    results.

    Examples
    ----------
    .. code-block:: python

       >>> from abc import abstractmethod
       >>> from beartype import beartype
       >>> from beartype.typing import Protocol

       >>> class MyBearProtocol(Protocol):  # <-- runtime-checkable through inheritance
       ...   @abstractmethod
       ...   def myfunc(self, arg: int) -> str:
       ...     pass

       >>> my_thing: MyBearProtocol = MyImplementation()
       >>> isinstance(my_thing, MyBearProtocol)
       True

       >>> @beartype
       ... def do_somthing(thing: MyBearProtocol) -> None:
       ...   thing.myfunc(0)
    '''

    # ..................{ CLASS VARIABLES                    }..................
    __slots__: Any = ()

    # ..................{ DUNDERS                            }..................
    @callable_cached_minimal
    def __class_getitem__(cls, item):

        # We have to redefine this method because typing.Protocol's version
        # is very persnickety about only working for typing.Generic and
        # typing.Protocol. That's an exclusive club, and we ain't in it.
        # (RIP, GC.) Let's see if we can sneak in, shall we?

        # FIXME: Once <https://bugs.python.org/issue46581> is addressed,
        # consider replacing the madness below with something like:
        #   cached_gen_alias = _ProtocolSlow.__class_getitem__(_ProtocolSlow, params)
        #   our_gen_alias = cached_gen_alias.copy_with(params)
        #   our_gen_alias.__origin__ = cls
        #   return our_gen_alias

        # Superclass __class_getitem__() dunder method, localized for
        # brevity, efficiency, and (most importantly) to squelch false
        # positive "errors" from pyright with a single pragma comment.
        super_class_getitem = super().__class_getitem__  # pyright: ignore[reportGeneralTypeIssues]

        # If the superclass typing.Protocol.__class_getitem__() dunder
        # method has been wrapped as expected with caching by the private
        # (and thus *NOT* guaranteed to exist) @typing._tp_cache decorator,
        # call that unwrapped method directly to obtain the expected
        # generic alias.
        #
        # Note that:
        # * We intentionally call the unwrapped method rather than the
        #   decorated closure wrapping that method with memoization. Why?
        #   Because subsequent logic monkey-patches this generic alias to
        #   refer to this class rather than the standard "typing.Protocol".
        #   However, doing so violates internal expectations of the
        #   @typing._tp_cache decorator performing this memoization.
        # * This method is already memoized by our own @callable_cached
        #   decorator. Calling the decorated closure wrapping that
        #   unwrapped method with memoization would needlessly consume
        #   excess space and time for *NO* additional benefit.
        if hasattr(super_class_getitem, '__wrapped__'):
            # Protocol class to be passed as the "cls" parameter to the
            # unwrapped superclass typing.Protocol.__class_getitem__()
            # dunder method. There exist two unique cases corresponding to
            # two unique branches of an "if" conditional in that method,
            # depending on whether either this "Protocol" superclass or a
            # user-defined subclass of this superclass is being
            # subscripted. Specifically, this class is...
            protocol_cls = (
                # If this "Protocol" superclass is being directly
                # subclassed by one or more type variables (e.g.,
                # "Protocol[S, T]"), the non-caching "typing.Protocol"
                # superclass underlying this caching protocol superclass.
                # Since the aforementioned "if" conditional performs an
                # explicit object identity test for the "typing.Protocol"
                # superclass, we *MUST* pass that rather than this
                # superclass to trigger that conditional appropriately.
                _ProtocolSlow
                if cls is Protocol else
                # Else, a user-defined subclass of this "Protocol"
                # superclass is being subclassed by one or more type
                # variables *OR* types satisfying the type variables
                # subscripting the superclass (e.g.,
                # "UserDefinedProtocol[str]" for a user-defined subclass
                # class UserDefinedProtocol(Protocol[AnyStr]). In this
                # case, this subclass as is.
                cls
            )

            gen_alias = super_class_getitem.__wrapped__(protocol_cls, item)
        # We shouldn't ever be here, but if we are, we're making the
        # assumption that typing.Protocol.__class_getitem__() no longer
        # caches. Heaven help us if that ever uses some proprietary
        # memoization implementation we can't see anymore because it's not
        # based on the standard @functools.wraps decorator.
        else:
            gen_alias = super_class_getitem(item)

        # Switch the origin of this generic alias from its default of
        # "typing.Protocol" to this caching protocol class. If *NOT* done,
        # CPython incorrectly sets the metaclass of subclasses to the
        # non-caching "type(typing.Protocol)" metaclass rather than our
        # caching "_CachingProtocolMeta" metaclass.
        #
        # Luddite alert: we don't fully understand the mechanics here. We
        # suspect no one does.
        gen_alias.__origin__ = cls

        # We're done! Time for a honey brewskie break. We earned it.
        return gen_alias

#FIXME: Ensure that the main @beartype codebase handles protocols whose
#repr() starts with "beartype.typing" as well, please.

# Replace the unexpected (and thus non-compliant) fully-qualified name of
# the module declaring this caching protocol superclass (e.g.,
# "beartype.typing._typingpep544") with the expected (and thus compliant)
# fully-qualified name of the standard "typing" module declaring the
# non-caching "typing.Protocol" superclass.
#
# If this is *NOT* done, then the machine-readable representation of this
# caching protocol superclass when subscripted by one or more type
# variables (e.g., "beartype.typing.Protocol[S, T]") will be differ
# significantly from that of the non-caching "typing.Protocol" superclass
# (e.g., beartype.typing._typingpep544.Protocol[S, T]"). Because
# @beartype (and possibly other third-party packages) expect the two
# representations to comply, this awkward monkey-patch preserves sanity.
Protocol.__module__ = 'beartype.typing'

# ....................{ PROTOCOLS                          }....................
class SupportsAbs(_SupportsAbsSlow[_T_co], Protocol, Generic[_T_co]):
    '''
    Caching variant of :class:`typing.SupportsAbs`.
    '''
    __module__: str = 'beartype.typing'
    __slots__: Any = ()


class SupportsBytes(_SupportsBytesSlow, Protocol):
    '''
    Caching variant of :class:`typing.SupportsBytes`.
    '''
    __module__: str = 'beartype.typing'
    __slots__: Any = ()


class SupportsComplex(_SupportsComplexSlow, Protocol):
    '''
    Caching variant of :class:`typing.SupportsComplex`.
    '''
    __module__: str = 'beartype.typing'
    __slots__: Any = ()


class SupportsFloat(_SupportsFloatSlow, Protocol):
    '''
    Caching variant of :class:`typing.SupportsFloat`."
    '''
    __module__: str = 'beartype.typing'
    __slots__: Any = ()


class SupportsInt(_SupportsIntSlow, Protocol):
    '''
    Caching variant of :class:`typing.SupportsInt`.
    '''
    __module__: str = 'beartype.typing'
    __slots__: Any = ()


class SupportsIndex(_SupportsIndexSlow, Protocol):
    '''
    Caching variant of :class:`typing.SupportsIndex`.
    '''
    __module__: str = 'beartype.typing'
    __slots__: Any = ()


class SupportsRound(_SupportsRoundSlow[_T_co], Protocol, Generic[_T_co]):
    '''
    Caching variant of :class:`typing.SupportsRound`.
    '''
    __module__: str = 'beartype.typing'
    __slots__: Any = ()

# ....................{ MONKEY-PATCHES                     }....................
# If the active Python interpreter targets Python >= 3.12, monkey-patch the
# standard "typing" module to support our "Protocol" superclass.
if IS_PYTHON_AT_LEAST_3_12:
    import typing
    from typing import _generic_class_getitem as _generic_class_getitem_old  # type: ignore[attr-defined]

    def _generic_class_getitem_new(cls, params):
        '''
        Beartype-specific wrapper for the private
        :func:`typing._generic_class_getitem` utility function, enabling that
        function to transparently support our beartype-specific
        :class:`beartype.typing.Protocol` superclass equivalent to the standard
        :class:`typing.Protocol` superclass.
        '''

        # If the passed class is our "beartype.typing.Protocol" superclass,
        # silently replace that with "typing.Protocol" *BEFORE* calling the
        # standard typing._generic_class_getitem() utility function -- which
        # explicitly only supports the latter.
        if cls is Protocol:
            cls = _ProtocolSlow
        # Else, the passed class is *NOT* our "beartype.typing.Protocol"
        # superclass. In this case, preserve that class as is.

        # Defer to the standard typing._generic_class_getitem() implementation.
        return _generic_class_getitem_old(cls, params)

    # Replace the standard typing._generic_class_getitem() implementation with
    # the wrapper defined above. *gulp*
    typing._generic_class_getitem = _generic_class_getitem_new  # type: ignore[attr-defined]
