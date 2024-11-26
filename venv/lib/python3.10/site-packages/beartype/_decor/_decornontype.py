#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Unmemoized beartype non-type decorators** (i.e., low-level decorators
decorating *all* types of decoratable objects except classes, which the sibling
:mod:`beartype._decor._decortype` submodule handles, on behalf of the parent
:mod:`beartype._decor.decorcore` submodule).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import (
    BeartypeDecorWrappeeException,
    BeartypeDecorWrapperException,
)
from beartype.typing import no_type_check
from beartype._cave._cavefast import (
    MethodBoundInstanceOrClassType,
    MethodDecoratorClassType,
    MethodDecoratorBuiltinTypes,
    MethodDecoratorPropertyType,
    MethodDecoratorStaticType,
)
from beartype._check.checkcall import make_beartype_call
from beartype._conf.confcls import BeartypeConf
from beartype._conf.confenum import BeartypeStrategy
from beartype._data.hint.datahinttyping import (
    BeartypeableT,
)
from beartype._decor.wrap.wrapmain import generate_code
from beartype._util.cache.pool.utilcachepoolobjecttyped import (
    release_object_typed)
from beartype._util.func.mod.utilbeartypefunc import (
    is_func_unbeartypeable,
    set_func_beartyped,
)
from beartype._util.func.mod.utilfuncmodtest import (
    is_func_contextlib_contextmanager,
    is_func_functools_lru_cache,
)
from beartype._util.func.utilfuncmake import make_func
from beartype._util.func.utilfunctest import is_func_python
from beartype._util.func.utilfuncwrap import unwrap_func_once
from beartype._util.py.utilpyversion import IS_PYTHON_3_8
from contextlib import contextmanager
from functools import lru_cache

# ....................{ DECORATORS ~ non-func              }....................
def beartype_nontype(obj: BeartypeableT, **kwargs) -> BeartypeableT:
    '''
    Decorate the passed **non-class beartypeable** (i.e., caller-defined object
    that may be decorated by the :func:`beartype.beartype` decorator but is
    *not* a class) with dynamically generated type-checking.

    Parameters
    ----------
    obj : BeartypeableT
        Non-class beartypeable to be decorated.

    All remaining keyword parameters are passed as is to a lower-level decorator
    defined by this submodule (e.g., :func:`.beartype_func`).

    Returns
    ----------
    BeartypeableT
        New pure-Python callable wrapping this beartypeable with type-checking.
    '''

    # Validate that the passed object is *NOT* a class.
    assert not isinstance(obj, type), f'{repr(obj)} is class.'
    # print(f'Decorating non-type {repr(obj)}...')

    # Type of this object.
    obj_type = type(obj)

    # If this object is an uncallable builtin method descriptor (i.e., either a
    # property, class method, instance method, or static method object),
    # @beartype was listed above rather than below the builtin decorator
    # generating this descriptor in the chain of decorators decorating this
    # decorated callable. Although @beartype typically *MUST* decorate a
    # callable directly, this edge case is sufficiently common *AND* trivial to
    # resolve to warrant doing so. To do so, this conditional branch effectively
    # reorders @beartype to be the first decorator decorating the pure-Python
    # function underlying this method descriptor: e.g.,
    #
    #     # This branch detects and reorders this edge case...
    #     class MuhClass(object):
    #         @beartype
    #         @classmethod
    #         def muh_classmethod(cls) -> None: pass
    #
    #     # ...to resemble this direct decoration instead.
    #     class MuhClass(object):
    #         @classmethod
    #         @beartype
    #         def muh_classmethod(cls) -> None: pass
    #
    # Note that most but *NOT* all of these objects are uncallable. Regardless,
    # *ALL* of these objects are unsuitable for direct decoration. Specifically:
    # * Under Python < 3.10, *ALL* of these objects are uncallable.
    # * Under Python >= 3.10:
    #   * Descriptors created by @classmethod and @property are uncallable.
    #   * Descriptors created by @staticmethod are technically callable but
    #     C-based and thus unsuitable for decoration.
    if obj_type in MethodDecoratorBuiltinTypes:
        return beartype_descriptor_decorator_builtin(obj, **kwargs)  # type: ignore[return-value]
    # Else, this object is *NOT* an uncallable builtin method descriptor.
    #
    # If this object is uncallable, raise an exception.
    elif not callable(obj):
        raise BeartypeDecorWrappeeException(
            f'Uncallable {repr(obj)} not decoratable by @beartype.')
    # Else, this object is callable.
    #
    # If this object is *NOT* a pure-Python function, this object is a
    # pseudo-callable (i.e., arbitrary pure-Python *OR* C-based object whose
    # class defines the __call__() dunder method enabling this object to be
    # called like a standard callable). In this case, attempt to monkey-patch
    # runtime type-checking into this pure-Python callable by replacing the
    # bound method descriptor of the type of this object implementing the
    # __call__() dunder method with a comparable descriptor calling a
    # @beartype-generated runtime type-checking wrapper function.
    elif not is_func_python(obj):
        return beartype_pseudofunc(obj, **kwargs)  # type: ignore[return-value]
    # Else, this object is a pure-Python function.
    #
    # If this function is a @contextlib.contextmanager-based isomorphic
    # decorator closure (i.e., closure both created and returned by the standard
    # @contextlib.contextmanager decorator where that closure isomorphically
    # preserves both the number and types of all passed parameters and returns
    # by accepting only a variadic positional argument and variadic keyword
    # argument), @beartype was listed above rather than below the
    # @contextlib.contextmanager decorator creating and returning this closure
    # in the chain of decorators decorating this decorated callable. This is
    # non-ideal, as the type of *ALL* objects created and returned by
    # @contextlib.contextmanager-decorated context managers is a private class
    # of the "contextlib" module rather than the types implied by the type hints
    # originally annotating the returns of those context managers. If @beartype
    # did *not* actively detect and intervene in this edge case, then runtime
    # type-checkers dynamically generated by @beartype for those managers would
    # erroneously raise type-checking violations after calling those managers
    # and detecting the apparent type violation: e.g.,
    #
    #     >>> from beartype.typing import Iterator
    #     >>> from contextlib import contextmanager
    #     >>> @contextmanager
    #     ... def muh_context_manager() -> Iterator[None]: yield
    #     >>> type(muh_context_manager())
    #     <class 'contextlib._GeneratorContextManager'>  # <-- not an "Iterator"
    #
    # This conditional branch effectively reorders @beartype to be the first
    # decorator decorating the callable underlying this context manager,
    # preserving consistency between return types *AND* return type hints: e.g.,
    #
    #     from beartype.typing import Iterator
    #     from contextlib import contextmanager
    #
    #     # This branch detects and reorders this edge case...
    #     @beartype
    #     @contextmanager
    #     def muh_contextmanager(cls) -> Iterator[None]: yield
    #
    #     # ...to resemble this direct decoration instead.
    #     @contextmanager
    #     @beartype
    #     def muh_contextmanager(cls) -> Iterator[None]: yield
    elif is_func_contextlib_contextmanager(obj):
        return beartype_func_contextlib_contextmanager(obj, **kwargs)  # type: ignore[return-value]
    # Else, this function is *NOT* a @contextlib.contextmanager-based isomorphic
    # decorator closure.

    # Return a new callable decorating that callable with type-checking.
    return beartype_func(obj, **kwargs)  # type: ignore[return-value]

# ....................{ DECORATORS ~ func                  }....................
def beartype_func(
    # Mandatory parameters.
    func: BeartypeableT,
    conf: BeartypeConf,

    # Variadic keyword parameters.
    **kwargs
) -> BeartypeableT:
    '''
    Decorate the passed callable with dynamically generated type-checking.

    Parameters
    ----------
    func : BeartypeableT
        Callable to be decorated by :func:`beartype.beartype`.
    conf : BeartypeConf
        Beartype configuration configuring :func:`beartype.beartype` uniquely
        specific to this callable.

    All remaining keyword parameters are passed as is to the
    :meth:`beartype._check.checkcall.BeartypeCall.reinit` method.

    Returns
    ----------
    BeartypeableT
        New pure-Python callable wrapping this callable with type-checking.
    '''
    assert callable(func), f'{repr(func)} uncallable.'
    # assert isinstance(conf, BeartypeConf), f'{repr(conf)} not configuration.'
    # assert isinstance(cls_root, NoneTypeOr[type]), (
    #     f'{repr(cls_root)} neither type nor "None".')
    # assert isinstance(cls_curr, NoneTypeOr[type]), (
    #     f'{repr(cls_curr)} neither type nor "None".')

    #FIXME: Uncomment to display all annotations in "pytest" tracebacks.
    # func_hints = func.__annotations__

    # If this configuration enables the no-time strategy performing *NO*
    # type-checking, monkey-patch that callable with the standard
    # @typing.no_type_check decorator detected above by the call to the
    # is_func_unbeartypeable() tester on all subsequent decorations passed the
    # same callable... Doing so prevents all subsequent decorations from
    # erroneously ignoring this previously applied no-time strategy.
    if conf.strategy is BeartypeStrategy.O0:
        no_type_check(func)
    # Else, this configuration enables a positive-time strategy performing at
    # least the minimal amount of type-checking.

    # If that callable is unbeartypeable (i.e., if this decorator should
    # preserve that callable as is rather than wrap that callable with
    # constant-time type-checking), silently reduce to the identity decorator.
    #
    # Note that this conditional implicitly handles the prior conditional! :O
    if is_func_unbeartypeable(func):  # type: ignore[arg-type]
        # print(f'Ignoring unbeartypeable callable {repr(func)}...')
        return func  # type: ignore[return-value]
    # Else, that callable is beartypeable. Let's do this, folks.

    # Beartype call metadata describing that callable.
    bear_call = make_beartype_call(func, conf, **kwargs)

    # Generate the raw string of Python statements implementing this wrapper.
    func_wrapper_code = generate_code(bear_call)

    # If that callable requires *NO* type-checking, silently reduce to a noop
    # and thus the identity decorator by returning that callable as is.
    if not func_wrapper_code:
        return func  # type: ignore[return-value]
    # Else, that callable requires type-checking. Let's *REALLY* do this, fam.

    # Function wrapping that callable with type-checking to be returned.
    #
    # For efficiency, this wrapper accesses *ONLY* local rather than global
    # attributes. The latter incur a minor performance penalty, since local
    # attributes take precedence over global attributes, implying all global
    # attributes are *ALWAYS* first looked up as local attributes before falling
    # back to being looked up as global attributes.
    func_wrapper = make_func(
        func_name=bear_call.func_wrapper_name,
        func_code=func_wrapper_code,
        func_locals=bear_call.func_wrapper_scope,

        #FIXME: String formatting is infamously slow. As an optimization, it'd
        #be strongly preferable to instead pass a lambda function accepting *NO*
        #parameters and returning the desired string, which make_func() should
        #then internally call on an as-needed basis to make this string: e.g.,
        #    func_label_factory=lambda: f'@beartyped {bear_call.func_wrapper_name}() wrapper',
        #
        #This is trivial. The only question then is: "Which is actually faster?"
        #Before finalizing this refactoring, let's profile both, adopt whichever
        #outperforms the other, and then document this choice in make_func().
        #FIXME: *WAIT.* We don't need a lambda at all. All we need is to:
        #* Define a new BeartypeCall.label_func_wrapper() method resembling:
        #      def label_func_wrapper(self) -> str:
        #          return f'@beartyped {self.func_wrapper_name}() wrapper'
        #* Refactor make_func() to accept a new optional keyword-only
        #  "func_label_factory" parameter, passed here as:
        #      func_label_factory=bear_call.label_func_wrapper,
        #
        #That's absolutely guaranteed to be the fastest approach.
        func_label=f'@beartyped {bear_call.func_wrapper_name}() wrapper',

        func_wrapped=func,
        is_debug=conf.is_debug,
        exception_cls=BeartypeDecorWrapperException,
    )

    # Declare this wrapper to be generated by @beartype, which tests for the
    # existence of this attribute above to avoid re-decorating callables
    # already decorated by @beartype by efficiently reducing to a noop.
    set_func_beartyped(func_wrapper)

    # Release this beartype call metadata back to its object pool.
    release_object_typed(bear_call)

    # Return this wrapper.
    return func_wrapper  # type: ignore[return-value]


def beartype_func_contextlib_contextmanager(
    func: BeartypeableT, **kwargs) -> BeartypeableT:
    '''
    Decorate the passed :func:`contextlib.contextmanager`-based **isomorphic
    decorator closure** (i.e., closure both defined and returned by the standard
    :func:`contextlib.contextmanager` decorator where that closure
    isomorphically preserves both the number and types of all passed parameters
    and returns by accepting only a variadic positional argument and variadic
    keyword argument) with dynamically generated type-checking.

    Parameters
    ----------
    descriptor : BeartypeableT
        Context manager to be decorated by :func:`beartype.beartype`.

    All remaining keyword parameters are passed as is to the lower-level
    :func:`.beartype_func` decorator internally called by this higher-level
    decorator on the pure-Python function encapsulated in this descriptor.

    Returns
    ----------
    BeartypeableT
        New pure-Python callable wrapping this context manager with
        type-checking.
    '''

    # Original pure-Python generator factory function decorated by
    # @contextlib.contextmanager.
    generator = unwrap_func_once(func)

    # Decorate this generator factory function with type-checking.
    generator_checked = beartype_func(func=generator, **kwargs)

    # Re-decorate this generator factory function by @contextlib.contextmanager.
    generator_checked_contextmanager = contextmanager(generator_checked)

    # Return this context manager.
    return generator_checked_contextmanager  # type: ignore[return-value]

# ....................{ DECORATORS ~ descriptor            }....................
def beartype_descriptor_decorator_builtin(
    descriptor: BeartypeableT, **kwargs) -> BeartypeableT:
    '''
    Decorate the passed **builtin decorator object** (i.e., C-based unbound
    method descriptor produced by the builtin :class:`classmethod`,
    :class:`property`, or :class:`staticmethod` decorators) with dynamically
    generated type-checking.

    Parameters
    ----------
    descriptor : BeartypeableT
        Descriptor to be decorated by :func:`beartype.beartype`.

    All remaining keyword parameters are passed as is to the lower-level
    :func:`.beartype_func` decorator internally called by this higher-level
    decorator on the pure-Python function encapsulated in this descriptor.

    Returns
    ----------
    BeartypeableT
        New pure-Python callable wrapping this descriptor with type-checking.

    Raises
    ----------
    BeartypeDecorWrappeeException
        If this descriptor is neither a class, property, or static method
        descriptor.
    '''
    # assert isinstance(descriptor, MethodDecoratorBuiltinTypes), (
    #     f'{repr(descriptor)} not builtin method descriptor.')
    # assert isinstance(conf, BeartypeConf), f'{repr(conf)} not configuration.'

    # Type of this descriptor.
    descriptor_type = type(descriptor)

    # If this descriptor is a property method...
    #
    # Note that property method descriptors are intentionally tested next, due
    # to their ubiquity "in the wild." Class and static method descriptors are
    # comparatively rarefied by comparison.
    if descriptor_type is MethodDecoratorPropertyType:
        # Pure-Python unbound getter, setter, and deleter functions wrapped by
        # this descriptor if any *OR* "None" otherwise (i.e., for each such
        # function currently unwrapped by this descriptor).
        descriptor_getter  = descriptor.fget  # type: ignore[assignment,union-attr]
        descriptor_setter  = descriptor.fset  # type: ignore[assignment,union-attr]
        descriptor_deleter = descriptor.fdel  # type: ignore[assignment,union-attr]

        # Decorate this getter function with type-checking.
        #
        # Note that *ALL* property method descriptors wrap at least a getter
        # function (but *NOT* necessarily a setter or deleter function). This
        # function is thus guaranteed to be non-"None".
        descriptor_getter = beartype_func(  # type: ignore[type-var]
            func=descriptor_getter,  # pyright: ignore[reportGeneralTypeIssues]
            **kwargs
        )

        # If this property method descriptor additionally wraps a setter and/or
        # deleter function, type-check those functions as well.
        if descriptor_setter is not None:
            descriptor_setter = beartype_func(descriptor_setter, **kwargs)
        if descriptor_deleter is not None:
            descriptor_deleter = beartype_func(descriptor_deleter, **kwargs)

        # Return a new property method descriptor decorating all of these
        # functions, implicitly destroying the prior descriptor.
        #
        # Note that the "property" class interestingly has this signature:
        #     class property(fget=None, fset=None, fdel=None, doc=None): ...
        return property(  # type: ignore[return-value]
            fget=descriptor_getter,
            fset=descriptor_setter,
            fdel=descriptor_deleter,
            doc=descriptor.__doc__,
        )
    # Else, this descriptor is *NOT* a property method.
    #
    # If this descriptor is a class method...
    elif descriptor_type is MethodDecoratorClassType:
        # Pure-Python unbound function type-checking this class method.
        #
        # Note that:
        # * Python 3.8, 3.9, and 3.10 explicitly permit the @classmethod
        #   decorator to be chained into the @property decorator: e.g.,
        #       class MuhClass(object):
        #           @classmethod  # <-- this is fine under Python < 3.11
        #           @property
        #           def muh_property(self) -> ...: ...
        # * Python ≥ 3.11 explicitly prohibits that by emitting a non-fatal
        #   "DeprecationWarning" on each attempt to do so. Under Python ≥ 3.11,
        #   users *MUST* instead refactor the above simplistic decorator
        #   chaining use case as follows:
        #   * Define a metaclass for each class requiring a class property.
        #   * Define each class property on that metaclass rather than on that
        #     class instead.
        #
        #   In other words:
        #       class MuhClassMeta(type):  # <-- Python ≥ 3.11 demands sacrifice
        #          '''
        #          Metaclass of the :class`.MuhClass` class, defining class
        #          properties for that class.
        #          '''
        #
        #          @property
        #          def muh_property(cls) -> ...: ...
        #
        #      class MuhClass(object, metaclass=MuhClassMeta):
        #          pass
        # * Technically, all Python versions currently supported by @beartype
        #   permit this. Ergo, @beartype currently defers to:
        #   * The high-level beartype_nontype() decorator (which permits the
        #     passed object to be the descriptor created and returned by the
        #     @property decorator and thus implicitly allows @classmethod to be
        #     chained into @property) rather than...
        #   * The low-level beartype_func() decorator (which requires the passed
        #     object to be callable, which the descriptor created and returned
        #     by the @property decorator is *NOT*).
        func_checked = beartype_nontype(descriptor.__func__,  **kwargs)  # type: ignore[union-attr]

        # Return a new class method descriptor decorating the pure-Python
        # unbound function wrapped by this descriptor with type-checking,
        # implicitly destroying the prior descriptor.
        return classmethod(func_checked)  # type: ignore[return-value]
    # Else, this descriptor is *NOT* a class method.
    #
    # If this descriptor is a static method...
    elif descriptor_type is MethodDecoratorStaticType:
        # Pure-Python unbound function type-checking this static method.
        func_checked = beartype_func(descriptor.__func__, **kwargs) # type: ignore[union-attr]

        # Return a new static method descriptor decorating the pure-Python
        # unbound function wrapped by this descriptor with type-checking,
        # implicitly destroying the prior descriptor.
        return staticmethod(func_checked)  # type: ignore[return-value]
    # Else, this descriptor is *NOT* a static method.

    # Raise a fallback exception. This should *NEVER happen. This *WILL* happen.
    raise BeartypeDecorWrappeeException(
        f'Builtin method descriptor {repr(descriptor)} '
        f'not decoratable by @beartype '
        f'(i.e., neither property, class method, nor static method descriptor).'
    )

# ....................{ PRIVATE ~ decorators               }....................
def _beartype_descriptor_method_bound(
    descriptor: BeartypeableT, **kwargs) -> BeartypeableT:
    '''
    Decorate the passed **builtin bound method object** (i.e., C-based bound
    method descriptor produced by Python on instantiation for each instance and
    class method defined by the class being instantiated) with dynamically
    generated type-checking.

    Parameters
    ----------
    descriptor : BeartypeableT
        Descriptor to be decorated by :func:`beartype.beartype`.

    All remaining keyword parameters are passed as is to the lower-level
    :func:`.beartype_func` decorator internally called by this higher-level
    decorator on the pure-Python function encapsulated in this descriptor.

    Returns
    ----------
    BeartypeableT
        New pure-Python callable wrapping this descriptor with type-checking.
    '''
    assert isinstance(descriptor, MethodBoundInstanceOrClassType), (
        f'{repr(descriptor)} not builtin bound method descriptor.')

    # Pure-Python unbound function encapsulated by this descriptor.
    descriptor_func_old = descriptor.__func__

    # Pure-Python unbound function decorating the similarly pure-Python unbound
    # function encapsulated by this descriptor with type-checking.
    #
    # Note that doing so:
    # * Implicitly propagates dunder attributes (e.g., "__annotations__",
    #   "__doc__") from the original function onto this new function. Good.
    # * Does *NOT* implicitly propagate the same dunder attributes from the
    #   original descriptor encapsulating the original function to the new
    #   descriptor (created below) encapsulating this wrapper function. Bad!
    #   Thankfully, only one such attribute exists as of this time: "__doc__".
    #   We propagate this attribute manually below.
    descriptor_func_new = beartype_func(func=descriptor_func_old, **kwargs)  # pyright: ignore[reportGeneralTypeIssues]

    # New instance method descriptor rebinding this function to the instance of
    # the class bound to the prior descriptor.
    #
    # Note that:
    # * This is required, as the "__func__" attribute of method descriptors is
    #   read-only. Attempting to do so raises this non-human-readable exception:
    #     AttributeError: readonly attribute
    #   This implies that the passed descriptor *CANNOT* be meaningfully
    #   modified. Our only recourse is to define an entirely new descriptor,
    #   effectively discarding the passed descriptor, which will then be
    #   subsequently garbage-collected. This is wasteful. This is Python.
    # * This can also be implemented by abusing the descriptor protocol:
    #       descriptor_new = descriptor_func_new.__get__(descriptor.__self__)
    #   That said, there exist *NO* benefits to doing so. Indeed, doing so only
    #   reduces the legibility and maintainability of this operation.
    descriptor_new = MethodBoundInstanceOrClassType(
        descriptor_func_new, descriptor.__self__)  # type: ignore[return-value]

    #FIXME: Actually, Python doesn't appear to support this at the moment.
    #Attempting to do so raises this exception:
    #    AttributeError: attribute '__doc__' of 'method' objects is not writable
    #
    #See also this open issue on the Python bug tracker requesting this be
    #resolved. Sadly, Python has yet to resolve this:
    #    https://bugs.python.org/issue47153
    # # Propagate the docstring from the prior to the new descriptor.
    # #
    # # Note that Python guarantees this attribute to exist. If the original
    # # function had a docstring, this attribute is non-"None"; else, this
    # # attribute is "None". In either case, this attribute exists. Ergo,
    # # additional validation is neither required nor desired.
    # descriptor_new.__doc__ = descriptor.__doc__

    # Return this new descriptor, implicitly destroying the prior descriptor.
    return descriptor_new  # type: ignore[return-value]

# ....................{ DECORATORS ~ pseudo-callable       }....................
def beartype_pseudofunc(pseudofunc: BeartypeableT, **kwargs) -> BeartypeableT:
    '''
    Monkey-patch the passed **pseudo-callable** (i.e., arbitrary pure-Python
    *or* C-based object whose class defines the ``__call__``) dunder method
    enabling this object to be called like a standard callable) with dynamically
    generated type-checking.

    For each bound method descriptor encapsulating a method bound to this
    object, this function monkey-patches (i.e., replaces) that descriptor with a
    comparable descriptor calling a new :func:`beartype.beartype`-generated
    runtime type-checking wrapper function wrapping the original method.

    Parameters
    ----------
    pseudofunc : BeartypeableT
        Pseudo-callable to be monkey-patched by :func:`beartype.beartype`.

    All remaining keyword parameters are passed as is to the lower-level
    :func:`.beartype_func` decorator internally called by this higher-level
    decorator on the pure-Python function encapsulated in this descriptor.

    Returns
    ----------
    BeartypeableT
        The object monkey-patched by :func:`beartype.beartype`.
    '''
    # print(f'@beartyping pseudo-callable {repr(obj)}...')

    # __call__() dunder method defined by this object if this object defines
    # this method *OR* "None" otherwise.
    pseudofunc_call_method = getattr(pseudofunc, '__call__')

    # If this object does *NOT* define this method, this object is *NOT* a
    # pseudo-callable. In this case, raise an exception.
    #
    # Note this edge case should *NEVER* occur. By definition, this object has
    # already been validated to be callable. But this object is *NOT* a
    # pure-Python function. Since the only other category of callable in Python
    # is a pseudo-callable, this object *MUST* be a pseudo-callable. That said,
    # languages change; it's not inconceivable that Python could introduce yet
    # another kind of callable object under future versions.
    if pseudofunc_call_method is None:
        raise BeartypeDecorWrappeeException(  # pragma: no cover
            f'Callable {repr(pseudofunc)} not pseudo-callable '
            f'(i.e., callable object defining __call__() dunder method).'
        )
    # Else, this object is a pseudo-callable.

    # If this method is *NOT* pure-Python, this method is C-based. In this
    # case...
    #
    # Note that this is non-ideal. Whereas logic below safely monkey-patches
    # pure-Python pseudo-callables in a general-purpose manner, that same logic
    # does *NOT* apply to C-based pseudo-callables; indeed, there exists *NO*
    # general-purpose means of safely monkey-patching the latter. Instead,
    # specific instances of the latter *MUST* be manually detected and handled.
    if not is_func_python(pseudofunc_call_method):
        # If this is a C-based @functools.lru_cache-memoized callable (i.e.,
        # low-level C-based callable object both created and returned by the
        # standard @functools.lru_cache decorator), @beartype was listed above
        # rather than below the @functools.lru_cache decorator creating and
        # returning this callable in the chain of decorators decorating this
        # decorated callable.
        #
        # This conditional branch effectively reorders @beartype to be the first
        # decorator decorating the pure-Python callable underlying this C-based
        # pseudo-callable: e.g.,
        #
        #     from functools import lru_cache
        #
        #     # This branch detects and reorders this edge case...
        #     @beartype
        #     @lru_cache
        #     def muh_lru_cache() -> None: pass
        #
        #     # ...to resemble this direct decoration instead.
        #     @lru_cache
        #     @beartype
        #     def muh_lru_cache() -> None: pass
        if is_func_functools_lru_cache(pseudofunc):
            # Return a new callable decorating that callable with type-checking.
            return beartype_pseudofunc_functools_lru_cache(  # type: ignore[return-value]
                pseudofunc=pseudofunc, **kwargs)
        # Else, this is *NOT* a C-based @functools.lru_cache-memoized callable.

    # Replace the existing bound method descriptor to this __call__() dunder
    # method with a new bound method descriptor to a new __call__() dunder
    # method wrapping the old method with runtime type-checking.
    #
    # Note that:
    # * This is a monkey-patch. Since the caller is intentionally decorating
    #   this pseudo-callable with @beartype, this is exactly what the caller
    #   wanted. Probably. Hopefully. Okay! We're crossing our fingers here.
    # * This monkey-patches the *CLASS* of this object rather than this object
    #   itself. Why? Because Python. For unknown reasons (so, speed is what
    #   we're saying), Python accesses the __call__() dunder method on the
    #   *CLASS* of an object rather than on the object itself. Of course, this
    #   implies that *ALL* instances of this pseudo-callable (rather than merely
    #   the passed instance) will be monkey-patched. This may *NOT* necessarily
    #   be what the caller wanted. Unfortunately, the only alternative would be
    #   for @beartype to raise an exception when passed a pseudo-callable. Since
    #   doing something beneficial is generally preferable to doing something
    #   harmful, @beartype prefers the former. See also official documentation
    #   on the subject:
    #       https://docs.python.org/3/reference/datamodel.html#special-method-names
    pseudofunc.__class__.__call__ = _beartype_descriptor_method_bound(  # type: ignore[assignment,method-assign]
        descriptor=pseudofunc_call_method, **kwargs)

    # Return this monkey-patched object.
    return pseudofunc  # type: ignore[return-value]


def beartype_pseudofunc_functools_lru_cache(
    pseudofunc: BeartypeableT, **kwargs) -> BeartypeableT:
    '''
    Monkey-patch the passed :func:`functools.lru_cache`-memoized
    **pseudo-callable** (i.e., low-level C-based callable object both created
    and returned by the standard :func:`functools.lru_cache` decorator) with
    dynamically generated type-checking.

    Parameters
    ----------
    pseudofunc : BeartypeableT
        Pseudo-callable to be monkey-patched by :func:`beartype.beartype`.

    All remaining keyword parameters are passed as is to the lower-level
    :func:`.beartype_func` decorator internally called by this higher-level
    decorator on the pure-Python function encapsulated in this descriptor.

    Returns
    ----------
    BeartypeableT
        New pseudo-callable monkey-patched by :func:`beartype.beartype`.
    '''

    # If this pseudo-callable is *NOT* actually a @functools.lru_cache-memoized
    # callable, raise an exception.
    if not is_func_functools_lru_cache(pseudofunc):
        raise BeartypeDecorWrappeeException(  # pragma: no cover
            f'@functools.lru_cache-memoized callable {repr(pseudofunc)} not  '
            f'decorated by @functools.lru_cache.'
        )
    # Else, this pseudo-callable is a @functools.lru_cache-memoized callable.

    # Original pure-Python callable decorated by @functools.lru_cache.
    func = unwrap_func_once(pseudofunc)

    # If the active Python interpreter targets Python 3.8, then this
    # pseudo-callable fails to declare the cache_parameters() lambda function
    # called below to recover the keyword parameters originally passed by the
    # caller to that decorator. In this case, we have *NO* recourse but to
    # explicitly inform the caller of this edge case by raising a human-readable
    # exception providing a pragmatic workaround.
    if IS_PYTHON_3_8:
        raise BeartypeDecorWrappeeException(  # pragma: no cover
            f'@functools.lru_cache-memoized callable {repr(func)} not '
            f'decoratable by @beartype under Python 3.8. '
            f'Consider manually decorating this callable by '
            f'@beartype first and then by @functools.lru_cache to preserve '
            f'Python 3.8 compatibility: e.g.,\n'
            f'    # Do this...\n'
            f'    @lru_cache(maxsize=42)\n'
            f'    @beartype\n'
            f'    def muh_func(...) -> ...: ...\n'
            f'\n'
            f'    # Rather than either this...\n'
            f'    @beartype\n'
            f'    @lru_cache(maxsize=42)\n'
            f'    def muh_func(...) -> ...: ...\n'
            f'\n'
            f'    # Or this (if you use "beartype.claw", which you really should).\n'
            f'    @lru_cache(maxsize=42)\n'
            f'    def muh_func(...) -> ...: ...\n'
        )
    # Else, the active Python interpreter targets Python >= 3.9.

    # Decorate that callable with type-checking.
    func_checked = beartype_func(func=func, **kwargs)

    # Dictionary mapping from the names of all keyword parameters originally
    # passed by the caller to that decorator, enabling the re-decoration of that
    # callable. Thankfully, that decorator preserves these parameters via the
    # decorator-specific "cache_parameters" instance variable whose value is a
    # bizarre argumentless lambda function (...for unknown reasons that are
    # probably indefensible) creating and returning this dictionary: e.g.,
    #     >>> from functools import lru_cache
    #     >>> @lru_cache(maxsize=3)
    #     ... def plus_one(n: int) -> int: return n +1
    #     >>> plus_one.cache_parameters()
    #     {'maxsize': 3, 'typed': False}
    lru_cache_kwargs = pseudofunc.cache_parameters()  # type: ignore[attr-defined]

    # Closure defined and returned by the @functools.lru_cache decorator when
    # passed these keyword parameters.
    lru_cache_configured = lru_cache(**lru_cache_kwargs)

    # Re-decorate that callable by @functools.lru_cache by the same parameters
    # originally passed by the caller to that decorator.
    pseudofunc_checked = lru_cache_configured(func_checked)

    # Return that new pseudo-callable.
    return pseudofunc_checked
