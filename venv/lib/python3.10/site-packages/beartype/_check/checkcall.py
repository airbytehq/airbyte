#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype dataclass** (i.e., class aggregating *all* metadata for the callable
currently being decorated by the :func:`beartype.beartype` decorator).**

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorWrappeeException
from beartype.typing import (
    Callable,
    Dict,
    FrozenSet,
    Optional,
)
from beartype._cave._cavefast import CallableCodeObjectType
from beartype._cave._cavemap import NoneTypeOr
from beartype._check.checkmagic import (
    ARG_NAME_BEARTYPE_CONF,
    ARG_NAME_FUNC,
    ARG_NAME_RAISE_EXCEPTION,
)
from beartype._check.forward.fwdscope import BeartypeForwardScope
from beartype._conf.confcls import BeartypeConf
from beartype._data.hint.datahinttyping import (
    LexicalScope,
    TypeStack,
)
from beartype._util.cache.pool.utilcachepoolobjecttyped import (
    acquire_object_typed)
from beartype._util.func.utilfunccodeobj import get_func_codeobj
from beartype._util.func.utilfuncget import get_func_annotations
from beartype._util.func.utilfunctest import (
    is_func_coro,
    is_func_nested,
)
from beartype._util.func.utilfuncwrap import unwrap_func_all_closures_isomorphic

# ....................{ CLASSES                            }....................
class BeartypeCall(object):
    '''
    **Beartype call metadata** (i.e., object encapsulating *all* metadata for
    the user-defined callable currently being decorated by the
    :func:`beartype.beartype` decorator).

    Design
    ----------
    This the *only* object instantiated by that decorator for that callable,
    substantially reducing both space and time costs. That decorator then
    passes this object to most lower-level functions, which then:

    #. Access read-only instance variables of this object as input.
    #. Modify writable instance variables of this object as output. In
       particular, these lower-level functions typically accumulate pure-Python
       code comprising the generated wrapper function type-checking the
       decorated callable by setting various instance variables of this object.

    Caveats
    ----------
    **This object cannot be used to communicate state between low-level
    memoized callables** (e.g.,
    :func:`beartype._check.code.codemake.make_func_wrapper_code`) **and
    higher-level callables** (e.g.,
    :func:`beartype._decor.wrap.wrapmain.generate_code`). Instead, memoized
    callables *must* return that state as additional return values up the call
    stack to those higher-level callables. By definition, memoized callables
    are *not* recalled on subsequent calls passed the same parameters. Since
    only the first call to those callables passed those parameters would set
    the appropriate state on this object intended to be communicated to
    higher-level callables, *all* subsequent calls would subtly fail with
    difficult-to-diagnose issues. See also `<issue #5_>`__, which exhibited
    this very complaint.

    .. _issue #5:
       https://github.com/beartype/beartype/issues/5

    Attributes
    ----------
    cls_stack : TypeStack
        **Type stack** (i.e., either tuple of zero or more arbitrary types *or*
        :data:`None`). See also the parameter of the same name accepted by the
        :func:`beartype._decor.decorcore.beartype_object` function for details.
    conf : BeartypeConf
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all flags, options, settings, and other metadata configuring the
        current decoration of the decorated callable).
    func_arg_name_to_hint : dict[str, object]
        Dictionary mapping from the name of each annotated parameter accepted
        by the decorated callable to the type hint annotating that parameter.
    func_arg_name_to_hint_get : Callable[[str, object], object]
        :meth:`dict.get` method bound to the :attr:`func_arg_name_to_hint`
        dictionary, localized as a negligible microoptimization. Blame Guido.
    func_wrappee : Optional[Callable]
        Possibly wrapped **decorated callable** (i.e., high-level callable
        currently being decorated by the :func:`beartype.beartype` decorator)
        if the :meth:`reinit` method has been called *or* ``None`` otherwise.
        Note the lower-level :attr:`func_wrappee_wrappee` callable should
        *usually* be accessed instead; although higher-level, this callable may
        only be a wrapper function and hence yield inaccurate or even erroneous
        metadata (especially the code object) for the callable being wrapped.
    func_wrappee_codeobj : CallableCodeObjectType
        Possibly wrapped **decorated callable wrappee code object** (i.e.,
        code object underlying the high-level :attr:`func_wrappee` callable
        currently being decorated by the :func:`beartype.beartype` decorator).
        For efficiency, this code object should *always* be accessed in lieu of
        inefficiently calling the comparatively slower
        :func:`beartype._util.func.utilfunccodeobj.get_func_codeobj` getter.
    func_wrappee_is_nested : bool
        Either:

        * If this wrappee callable is **nested** (i.e., declared in the body of
          another pure-Python callable or class), :data:`True`.
        * If this wrappee callable is **global** (i.e., declared at module scope
          in its submodule), :data:`False`.
    func_wrappee_scope_forward : Optional[BeartypeForwardScope]
        Either:

        * If this wrappee callable is annotated by at least one **stringified
          type hint** (i.e., declared as a :pep:`484`- or :pep:`563`-compliant
          forward reference referring to an actual type hint that has yet to be
          declared in the local and global scopes declaring this callable) that
          :mod:`beartype` has already resolved to its referent, this wrappee
          callable's **forward scope** (i.e., dictionary mapping from the name
          to value of each locally and globally accessible attribute in the
          local and global scope of this wrappee callable as well as deferring
          the resolution of each currently undeclared attribute in that scope by
          replacing that attribute with a forward reference proxy resolved only
          when that attribute is passed as the second parameter to an
          :func:`isinstance`-based runtime type-check).
        * Else, :data:`None`.

        Note that:

        * The reconstruction of this scope is computationally expensive and thus
          deferred until needed to resolve the first stringified type hint
          annotating this wrappee callable.
        * All callables have local scopes *except* global functions, whose local
          scopes are by definition the empty dictionary.
    func_wrappee_scope_nested_names : Optional[frozenset[str]]
        Either:

        * If this wrappee callable is annotated by at least one stringified type
          hint that :mod:`beartype` has already resolved to its referent,
          either:

          * If this wrappee callable is **nested** (i.e., declared in the body
            of another pure-Python callable or class), the non-empty frozen set
            of the unqualified names of all parent callables lexically
            containing this nested wrappee callable (including this nested
            wrappee callable itself).
          * Else, this wrappee callable is declared at global scope in its
            submodule. In this case, the empty frozen set.

        * Else, :data:`None`.
    func_wrappee_wrappee : Optional[Callable]
        Possibly unwrapped **decorated callable wrappee** (i.e., low-level
        callable wrapped by the high-level :attr:`func_wrappee` callable
        currently being decorated by the :func:`beartype.beartype` decorator)
        if the :meth:`reinit` method has been called *or* ``None`` otherwise.
        If the higher-level :attr:`func_wrappee` callable does *not* actually
        wrap another callable, this callable is identical to that callable.
    func_wrappee_wrappee_codeobj : CallableCodeObjectType
        Possibly unwrapped **decorated callable wrappee code object** (i.e.,
        code object underlying the low-level :attr:`func_wrappee_wrappee`
        callable wrapped by the high-level :attr:`func_wrappee` callable
        currently being decorated by the :func:`beartype.beartype` decorator).
        For efficiency, this code object should *always* be accessed in lieu of
        inefficiently calling the comparatively slower
        :func:`beartype._util.func.utilfunccodeobj.get_func_codeobj` getter.
    func_wrapper_code_call_prefix : Optional[str]
        Code snippet prefixing all calls to the decorated callable in the body
        of the wrapper function wrapping that callable with type checking if
        the :meth:`reinit` method has been called *or* ``None`` otherwise. If
        non-``None``, this string is guaranteed to be either:

        * If the decorated callable is synchronous (i.e., neither a coroutine
          nor asynchronous generator), the empty string.
        * If the decorated callable is asynchronous (i.e., either a coroutine
          nor asynchronous generator), the ``"await "`` keyword.
    func_wrapper_code_signature_prefix : Optional[str]
        Code snippet prefixing the signature declaring the wrapper function
        wrapping the decorated callable with type checking. Specifically, this
        string is guaranteed to be either:

        * If the decorated callable is synchronous (i.e., neither a coroutine
          nor asynchronous generator), the empty string.
        * If the decorated callable is asynchronous (i.e., either a coroutine
          or asynchronous generator), the ``"async "`` keyword.
    func_wrapper_scope : LexicalScope
        **Local scope** (i.e., dictionary mapping from the name to value of
        each attribute referenced in the signature) of this wrapper function.
    func_wrapper_name : Optional[str]
        Machine-readable name of the wrapper function to be generated and
        returned by this decorator.
    '''

    # ..................{ CLASS VARIABLES                    }..................
    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently
    # called @beartype decorations. Slotting has been shown to reduce read and
    # write costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        'cls_stack',
        'conf',
        'func_arg_name_to_hint',
        'func_arg_name_to_hint_get',
        'func_wrappee',
        'func_wrappee_codeobj',
        'func_wrappee_is_nested',
        'func_wrappee_scope_forward',
        'func_wrappee_scope_nested_names',
        'func_wrappee_wrappee',
        'func_wrappee_wrappee_codeobj',
        'func_wrapper_code_call_prefix',
        'func_wrapper_code_signature_prefix',
        'func_wrapper_scope',
        'func_wrapper_name',
    )

    # Coerce instances of this class to be unhashable, preventing spurious
    # issues when accidentally passing these instances to memoized callables by
    # implicitly raising a "TypeError" exception on the first call to those
    # callables. There exists no tangible benefit to permitting these instances
    # to be hashed (and thus also cached), since these instances are:
    # * Specific to the decorated callable and thus *NOT* safely cacheable
    #   across functions applying to different decorated callables.
    # * Already cached via the acquire_object_typed() function called by the
    #   "beartype._decor.decormain" submodule.
    #
    # See also:
    #     https://docs.python.org/3/reference/datamodel.html#object.__hash__
    __hash__ = None  # type: ignore[assignment]

    # ..................{ INITIALIZERS                       }..................
    def __init__(self) -> None:
        '''
        Initialize this metadata by nullifying all instance variables.

        Caveats
        ----------
        **This class is not intended to be explicitly instantiated.** Instead,
        callers are expected to (in order):

        #. Acquire cached instances of this class via the
           :mod:`beartype._util.cache.pool.utilcachepoolobjecttyped` submodule.
        #. Call the :meth:`reinit` method on these instances to properly
           initialize these instances.
        '''

        # Nullify instance variables for safety.
        self.cls_stack: TypeStack = None
        self.conf: BeartypeConf = None  # type: ignore[assignment]
        self.func_arg_name_to_hint: Dict[str, object] = None  # type: ignore[assignment]
        self.func_arg_name_to_hint_get: Callable[[str, object], object] = None  # type: ignore[assignment]
        self.func_wrappee: Callable = None  # type: ignore[assignment]
        self.func_wrappee_codeobj: CallableCodeObjectType = None  # type: ignore[assignment]
        self.func_wrappee_is_nested: bool = None  # type: ignore[assignment]
        self.func_wrappee_scope_forward: Optional[BeartypeForwardScope] = None
        self.func_wrappee_scope_nested_names: Optional[FrozenSet[str]] = None
        self.func_wrappee_wrappee: Callable = None  # type: ignore[assignment]
        self.func_wrappee_wrappee_codeobj: CallableCodeObjectType = None  # type: ignore[assignment]
        self.func_wrapper_code_call_prefix: str = None  # type: ignore[assignment]
        self.func_wrapper_code_signature_prefix: str = None  # type: ignore[assignment]
        self.func_wrapper_scope: LexicalScope = {}
        self.func_wrapper_name: str = None  # type: ignore[assignment]


    def reinit(
        self,

        # Mandatory parameters.
        func: Callable,
        conf: BeartypeConf,

        # Optional parameters.
        cls_stack: TypeStack = None,
    ) -> None:
        '''
        Reinitialize this metadata from the passed callable, typically after
        acquisition of a previously cached instance of this class from the
        :mod:`beartype._util.cache.pool.utilcachepoolobject` submodule.

        If :pep:`563` is conditionally active for this callable, this function
        additionally resolves all postponed annotations on this callable to
        their referents (i.e., the intended annotations to which those
        postponed annotations refer).

        Parameters
        ----------
        func : Callable
            Callable currently being decorated by :func:`beartype.beartype`.
        conf : BeartypeConf
            Beartype configuration configuring :func:`beartype.beartype`
            specific to this callable.
        cls_stack : TypeStack
            **Type stack** (i.e., either tuple of zero or more arbitrary types
            *or* :data:`None`). See also the parameter of the same name accepted
            by the :func:`beartype._decor.decorcore.beartype_object` function.

        Raises
        ----------
        BeartypePep563Exception
            If evaluating a postponed annotation on this callable raises an
            exception (e.g., due to that annotation referring to local state no
            longer accessible from this deferred evaluation).
        BeartypeDecorWrappeeException
            If either:

            * This callable is uncallable.
            * This callable is neither a pure-Python function *nor* method;
              equivalently, if this callable is either C-based *or* a class or
              object defining the ``__call__()`` dunder method.
            * This configuration is *not* actually a configuration.
            * ``cls_owner`` is neither a class *nor* ``None``.
        '''

        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # CAUTION: Note this method intentionally avoids creating and passing an
        # "exception_prefix" substring to callables called below. Why? Because
        # exhaustive profiling has shown that creating that substring consumes a
        # non-trivial slice of decoration time. In other words, efficiency.
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        # Avoid circular import dependencies.
        from beartype._decor.error.errormain import get_beartype_violation

        # If this callable is uncallable, raise an exception.
        if not callable(func):
            raise BeartypeDecorWrappeeException(f'{repr(func)} uncallable.')
        # Else, this callable is callable.
        #
        # If this configuration is *NOT* a configuration, raise an exception.
        elif not isinstance(conf, BeartypeConf):
            raise BeartypeDecorWrappeeException(
                f'"conf" {repr(conf)} not beartype configuration.')
        # Else, this configuration is a configuration.
        #
        # If this class stack is neither a tuple *NOR* "None", raise an
        # exception.
        elif not isinstance(cls_stack, _TypeStackOrNone):
            raise BeartypeDecorWrappeeException(
                f'"cls_stack" {repr(cls_stack)} neither tuple nor "None".')
        # Else, this class stack is either a tuple *OR* "None".

        # If this class stack is *NOT* "None", this class stack is a tuple. In
        # this case, for each item of this class stack tuple...
        if cls_stack:
            for cls_stack_item in cls_stack:
                # If this item is *NOT* a type, raise an exception.
                if not isinstance(cls_stack_item, type):
                    raise BeartypeDecorWrappeeException(
                        f'"cls_stack" item {repr(cls_stack_item)} not type.')
        # Else, this class stack is "None".

        # Classify all passed parameters.
        self.cls_stack = cls_stack
        self.conf = conf

        # Wrappee callable currently being decorated.
        self.func_wrappee = func

        # Possibly unwrapped callable unwrapped from this wrappee callable.
        self.func_wrappee_wrappee = unwrap_func_all_closures_isomorphic(func)
        # self.func_wrappee_wrappee = unwrap_func_all(func)
        # print(f'func_wrappee: {self.func_wrappee}')
        # print(f'func_wrappee_wrappee: {self.func_wrappee_wrappee}')

        # True only if this wrappee callable is nested. As a minor efficiency
        # gain, we can avoid the slightly expensive call to is_func_nested() by
        # noting that:
        # * If the class stack is non-empty, then this wrappee callable is
        #   necessarily nested in one or more classes.
        # * Else, defer to the is_func_nested() tester.
        self.func_wrappee_is_nested = bool(cls_stack) or is_func_nested(func)

        # Defer the resolution of both global and local scopes for this wrappee
        # callable until needed to subsequently resolve stringified type hints.
        self.func_wrappee_scope_forward = None
        self.func_wrappee_scope_nested_names = None

        # Possibly wrapped callable code object.
        self.func_wrappee_codeobj = get_func_codeobj(
            func=func,
            exception_cls=BeartypeDecorWrappeeException,
        )

        # Possibly unwrapped callable code object.
        self.func_wrappee_wrappee_codeobj = get_func_codeobj(
            func=self.func_wrappee_wrappee,
            exception_cls=BeartypeDecorWrappeeException,
        )

        # Efficiently reduce this local scope back to the dictionary of all
        # parameters unconditionally required by *ALL* wrapper functions.
        self.func_wrapper_scope.clear()
        self.func_wrapper_scope[ARG_NAME_FUNC] = func
        self.func_wrapper_scope[ARG_NAME_BEARTYPE_CONF] = conf

        #FIXME: Non-ideal. This should *NOT* be set here but rather in the
        #lower-level code generating factory function that actually embeds the
        #call to this function (e.g.,
        #beartype._check._checkcode.make_func_code()).
        self.func_wrapper_scope[ARG_NAME_RAISE_EXCEPTION] = (
            get_beartype_violation)

        # Machine-readable name of the wrapper function to be generated.
        self.func_wrapper_name = func.__name__

        #FIXME: Globally replace all references to "__annotations__" throughout
        #the "beartype._decor" subpackage with references to this instead.
        #Since doing so is a negligible optimization, this is fine... for now.

        # Annotations dictionary *AFTER* resolving all postponed hints.
        #
        # Note that the functools.update_wrapper() function underlying the
        # @functools.wrap decorator underlying all sane decorators propagates
        # this dictionary from lower-level wrappees to higher-level wrappers by
        # default. We intentionally classify the annotations dictionary of this
        # higher-level wrapper, which *SHOULD* be the superset of that of this
        # lower-level wrappee (and thus more reflective of reality).
        self.func_arg_name_to_hint = get_func_annotations(func)

        # dict.get() method bound to this dictionary.
        self.func_arg_name_to_hint_get = self.func_arg_name_to_hint.get

        # If this callable is an asynchronous coroutine callable (i.e.,
        # callable declared with "async def" rather than merely "def" keywords
        # containing *NO* "yield" expressions)...
        #
        # Note that:
        # * The code object of the higher-level wrapper rather than lower-level
        #   wrappee is passed. Why? Because @beartype directly decorates *ONLY*
        #   the former, whose asynchronicity has *NO* relation to that of the
        #   latter. Notably, it is both feasible and (relatively) commonplace
        #   for third-party decorators to enable:
        #   * Synchronous callables to be called asynchronously by wrapping
        #     synchronous callables with asynchronous closures.
        #   * Asynchronous callables to be called synchronously by wrapping
        #     asynchronous callables with synchronous closures. Indeed, our
        #     top-level "conftest.py" pytest plugin does exactly this --
        #     enabling asynchronous tests to be safely called by pytest's
        #     currently synchronous framework.
        # * The higher-level is_func_async() tester is intentionally *NOT*
        #   called here, as doing so would also implicitly prefix all calls to
        #   asynchronous generator callables (i.e., callables also declared
        #   with the "async def" rather than merely "def" keywords but
        #   containing one or more "yield" expressions) with the "await"
        #   keyword. Whereas asynchronous coroutine objects implicitly returned
        #   by all asynchronous coroutine callables return a single awaitable
        #   value, asynchronous generator objects implicitly returned by all
        #   asynchronous generator callables *NEVER* return any awaitable
        #   value; they instead yield one or more values to external "async
        #   for" loops.
        if is_func_coro(self.func_wrappee_codeobj):
            # Code snippet prefixing all calls to this callable.
            self.func_wrapper_code_call_prefix = 'await '

            # Code snippet prefixing the declaration of the wrapper function
            # wrapping this callable with type-checking.
            self.func_wrapper_code_signature_prefix = 'async '
        # Else, this callable is synchronous (i.e., callable declared with
        # "def" rather than "async def"). In this case, reduce these code
        # snippets to the empty string.
        else:
            self.func_wrapper_code_call_prefix = ''
            self.func_wrapper_code_signature_prefix = ''

# ....................{ FACTORIES                          }....................
#FIXME: Unit test us up, please.
def make_beartype_call(
    # Mandatory parameters.
    func: Callable,
    conf: BeartypeConf,

    # Variadic keyword parameters.
    **kwargs
) -> BeartypeCall:
    '''
    **Beartype call metadata** (i.e., object encapsulating *all* metadata for
    the passed user-defined callable, typically currently being decorated by the
    :func:`beartype.beartype` decorator).

    Caveats
    ----------
    **This higher-level factory function should always be called in lieu of
    instantiating the** :class:`.BeartypeCall` **class directly.** Why?
    Brute-force efficiency. This factory efficiently reuses previously
    instantiated :class:`.BeartypeCall` objects rather than inefficiently
    instantiating new :class:`.BeartypeCall` objects.

    **The caller must pass the metadata returned by this factory back to the**
    :func:`beartype._util.cache.pool.utilcachepoolobjecttyped.release_object_typed`
    **function.** If accidentally omitted, this metadata will simply be
    garbage-collected rather than available for efficient reuse by this factory.
    Although hardly a worst-case outcome, omitting that explicit call largely
    defeats the purpose of calling this factory in the first place.

    Parameters
    ----------
    func : Callable
        Callable to be described.
    conf : BeartypeConf
        Beartype configuration configuring :func:`beartype.beartype` uniquely
        specific to this callable.

    All remaining keyword parameters are passed as is to the
    :meth:`.BeartypeCall.reinit` method.

    Returns
    ----------
    BeartypeCall
        Beartype call metadata describing this callable.

    '''

    # Previously cached callable metadata reinitialized from that callable.
    bear_call = acquire_object_typed(BeartypeCall)
    bear_call.reinit(func, conf, **kwargs)

    # Return this metadata.
    return bear_call

# ....................{ GLOBALS ~ private                  }....................
_TypeStackOrNone = NoneTypeOr[tuple]
'''
2-tuple ``(type, type(None)``, globally cached for negligible space and time
efficiency gains on validating passed parameters below.
'''
