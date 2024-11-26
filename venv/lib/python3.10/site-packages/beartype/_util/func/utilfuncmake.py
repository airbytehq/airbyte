#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **callable factories** (i.e., low-level functions dynamically
creating and returning new in-memory callables).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeUtilCallableException
from beartype.typing import (
    Optional,
    Type,
)
from beartype._data.hint.datahinttyping import (
    LexicalScope,
    TypeException,
)
from beartype._util.text.utiltextlabel import label_exception
from beartype._util.text.utiltextmunge import number_str_lines
from beartype._util.utilobject import get_object_name
from collections.abc import Callable
from functools import update_wrapper
from linecache import cache as linecache_cache  # type: ignore[attr-defined]
from weakref import finalize

# ....................{ MAKERS                             }....................
def make_func(
    # Mandatory arguments.
    func_name: str,
    func_code: str,

    # Optional arguments.
    func_globals: Optional[LexicalScope] = None,
    func_locals:  Optional[LexicalScope] = None,
    func_doc: Optional[str] = None,
    func_label:   Optional[str] = None,
    func_wrapped: Optional[Callable] = None,
    is_debug: bool = False,
    exception_cls: TypeException = _BeartypeUtilCallableException,
) -> Callable:
    '''
    Dynamically create and return a new function with the passed name declared
    by the passed code snippet and internally accessing the passed dictionaries
    of globally and locally scoped variables.

    Parameters
    ----------
    func_name : str
        Name of the function to be created.
    func_code : str
        Code snippet defining this function, including both this function's
        signature prefixed by zero or more decorations *and* body. **This
        snippet must be unindented.** If this snippet is indented, this factory
        raises a syntax error.
    func_globals : Optional[Dict[str, Any]]
        Dictionary mapping from the name to value of each **globally scoped
        attribute** (i.e., internally referenced in the body of the function
        declared by this code snippet). Defaults to the empty dictionary.
    func_locals : Optional[Dict[str, Any]]
        Dictionary mapping from the name to value of each **locally scoped
        attribute** (i.e., internally referenced either in the signature of
        the function declared by this code snippet *or* as decorators
        decorating that function). **Note that this factory necessarily
        modifies the contents of this dictionary.** Defaults to the empty
        dictionary.
    func_doc : Optional[str]
        Human-readable docstring documenting this function. Defaults to
        :data:`None`, in which case this function remains undocumented.
    func_label : str, optional
        Human-readable label describing this function for error-handling
        purposes. Defaults to ``"{func_name}()"``.
    func_wrapped : Callable, optional
        Callable wrapped by the function to be created. If non-:data:`None`,
        special dunder attributes will be propagated (i.e., copied) from this
        wrapped callable into this created function; these include:

        * ``__name__``, this function's unqualified name.
        * ``__doc__``, this function's docstring.
        * ``__module__``, the fully-qualified name of this function's module.

        Defaults to :data:`None`.
    is_debug : bool, optional
        :data:`True` only if this function is being debugged. If :data:`True`,
        then the definition (including signature and body) of this function is:

        * Printed to standard output.
        * Cached with the standard :mod:`linecache` module under a fake
          filename uniquely synthesized by this factory for this function.
          External callers may then subsequently access the definition of this
          function from that module as:

          .. code-block:: python

             from linecache import cache as linecache_cache
             func_source = linecache_cache[func.__code__.co_filename]

        Defaults to :data:`False`.
    exception_cls : Type[Exception], optional
        Type of exception to raise in the event of a fatal error. Defaults to
        :exc:`._BeartypeUtilCallableException`.

    Returns
    ----------
    Callable
        Function with this name declared by this snippet.

    Raises
    ----------
    :exc:`exception_cls`
        If either:

        * ``func_locals`` contains a key whose value is that of ``func_name``,
          implying the caller already declared a local attribute whose name
          collides with that of this function.
        * This code snippet is syntactically invalid.
        * This code snippet is syntactically valid but fails to declare a
          function with this name.
    '''

    # ..................{ VALIDATION ~ pre                   }..................
    assert isinstance(func_name, str), f'{repr(func_name)} not string.'
    assert isinstance(func_code, str), f'{repr(func_code)} not string.'
    assert isinstance(is_debug, bool), f'{repr(is_debug)} not bool.'
    assert func_name, 'Parameter "func_name" empty.'
    assert func_code, 'Parameter "func_code" empty.'

    # Default all unpassed parameters.
    if func_globals is None:
        func_globals = {}
    if func_locals is None:
        func_locals = {}
    if func_label is None:
        func_label = f'{func_name}()'
    assert isinstance(func_globals, dict), (
        f'{repr(func_globals)} not dictionary.')
    assert isinstance(func_locals, dict), (
        f'{repr(func_locals)} not dictionary.')
    assert isinstance(func_label, str), f'{repr(func_label)} not string.'

    # If that function's name is already in this local scope, the caller
    # already declared a local attribute whose name collides with that
    # function's. In this case, raise an exception for safety.
    if func_name in func_locals:
        raise exception_cls(
            f'{func_label} already defined by caller locals:\n'
            f'{repr(func_locals)}'
        )
    # Else, that function's name is *NOT* already in this local scope.

    # ..................{ STARTUP ~ filename                 }..................
    # Note that this logic is intentionally performed *BEFORE* munging the
    # "func_code" string in-place below, as this logic depends upon the unique
    # ID of that string. Reassignment obliterates that uniqueness.

    # Arbitrary object uniquely associated with this function.
    func_filename_object: object = None

    # Possibly fully-qualified name of an arbitrary object uniquely associated
    # with this function.
    func_filename_name: str = None  # type: ignore[assignment]

    # If this function is a high-level wrapper wrapping a lower-level
    # wrappee, uniquify the subsequent filename against this wrappee. This
    # wrappee's fully-qualified name guarantees the uniqueness of this
    # filename. Ergo, this is the ideal case.
    if func_wrapped:
        func_filename_name = get_object_name(func_wrapped)
        func_filename_object = func_wrapped
    # Else, this function is *NOT* such a wrapper. In this less ideal case,
    # fallback to a poor man's uniquification against the unqualified name and
    # code string underlying this function.
    else:
        func_filename_name = func_name
        func_filename_object = func_code

    # Fake in-memory filename hopefully unique to this function.
    # Optimistically, a fully-qualified object name and ID *SHOULD* be unique
    # for the lifetime of the active Python process.
    #
    # Specifically, this filename guarantees the uniqueness of the 3-tuple
    # ``({func_filename}, {func_file_line_number}, {func_name})`` commonly
    # leveraged by profilers (e.g., "cProfile") to identify arbitrary callables,
    # where:
    # * `{func_filename}` is this filename (e.g.,
    #   `"</home/leycec/py/betse/betse/lib/libs.py:beartype({func_name})>"`).
    # * `{func_file_line_number}`, is *ALWAYS* 0 and thus *NEVER* unique.
    # * `{func_name}`, is identical to that of the decorated callable and also
    #   thus *NEVER* unique.
    #
    # Ergo, uniquifying this filename is the *ONLY* means of uniquifying
    # metadata identifying this wrapper function via runtime inspection. Failure
    # to do so reduces tracebacks induced by exceptions raised by this wrapper
    # to non-human-readability, which is less than ideal: e.g.,
    #
    #    Traceback (most recent call last):
    #      File "/home/leycec/py/betsee/betsee/gui/simconf/stack/widget/mixin/guisimconfwdgeditscalar.py", line 313, in _set_alias_to_widget_value_if_sim_conf_open
    #        widget=self, value_old=self._widget_value_last)
    #      File "<string>", line 25, in func_beartyped
    #      File "/home/leycec/py/betsee/betsee/gui/simconf/stack/widget/mixin/guisimconfwdgeditscalar.py", line 409, in __init__
    #        *args, widget=widget, synopsis=widget.undo_synopsis, **kwargs)
    #      File "<string>", line 13, in func_beartyped
    #
    # See the final traceback line, which is effectively useless.
    func_filename = (
        f'<@beartype({func_filename_name}) at {id(func_filename_object):#x}>')

    # ..................{ STARTUP ~ code                     }..................
    # Code snippet defining this function, stripped of all leading and trailing
    # whitespace to improve both readability and disambiguity. Since this
    # whitespace is safely ignorable, the original snippet is safely
    # replaceable by this stripped snippet.
    func_code = func_code.strip()

    # If debugging this function, print the definition of this function.
    if is_debug:
        print(f'{number_str_lines(func_code)}')
    # else:
    #     print('!!!!!!!!!PRINTING NOTHING!!!!!!!!!!!')
    # Else, leave that definition obscured by the voracious bitbuckets of time.

    # ..................{ CREATION                           }..................
    # Attempt to...
    try:
        # Call the more verbose and obfuscatory compile() builtin instead of
        # simply calling "exec(func_code, func_globals, func_locals)". Why?
        # Because the exec() builtin does *NOT* provide a means to set this
        # function's "__code__.co_filename" read-only attribute.
        #
        # Note that we could pass "single" instead of "exec" here if we were
        # willing to constrain the passed "func_code" to a single statement. In
        # casual testing, there is very little performance difference between
        # the two (with an imperceptibly slight edge going to "single").
        func_code_compiled = compile(func_code, func_filename, 'exec')
        assert func_name not in func_locals

        # Define that function. For obscure and likely uninteresting reasons,
        # Python fails to capture that function (i.e., expose that function to
        # this factory) when the locals() dictionary is passed; instead, a
        # unique local dictionary *MUST* be passed.
        exec(func_code_compiled, func_globals, func_locals)
    # If doing so fails for *ANY* reason whatsoever, wrap that low-level
    # exception with a higher-level exception exhibiting the exact issue. Doing
    # so enables users to submit meaningful issues to our tracker.
    except Exception as exception:
        # Raise an exception suffixed by that function's declaration such that
        # each line of that declaration is prefixed by that line's number. This
        # renders "SyntaxError" exceptions referencing arbitrary line numbers
        # human-readable: e.g.,
        #       File "<string>", line 56
        #         if not (
        #          ^
        #     SyntaxError: invalid syntax
        raise exception_cls(
            f'{func_label} unparseable, as @beartype generated '
            f'invalid code raising "{label_exception(exception)}":\n\n'
            f'{number_str_lines(func_code)}'
        ) from exception

    # ..................{ VALIDATION ~ post                  }..................
    # If that function's name is *NOT* in this local scope, this code snippet
    # failed to declare that function. In this case, raise an exception.
    if func_name not in func_locals:
        raise exception_cls(
            f'{func_label} undefined by code snippet:\n\n'
            f'{number_str_lines(func_code)}'
        )
    # Else, that function's name is in this local scope.

    # Function declared by this code snippet.
    func: Callable = func_locals[func_name]  # type: ignore[assignment]

    # If that function is uncallable, raise an exception.
    if not callable(func):
        raise exception_cls(
            f'{func_label} defined by code snippet uncallable:\n\n'
            f'{number_str_lines(func_code)}'
        )
    # Else, that function is callable.

    # If that function is a wrapper wrapping a wrappee callable, propagate
    # dunder attributes from that wrappee onto this wrapper.
    if func_wrapped is not None:
        assert callable(func_wrapped), f'{repr(func_wrapped)} uncallable.'
        update_wrapper(wrapper=func, wrapped=func_wrapped)
    # Else, that function is *NOT* such a wrapper.

    # ..................{ CLEANUP                            }..................
    # If that function is documented...
    #
    # Note that function is intentionally documented *AFTER* propagating dunder
    # attributes to enable callers to explicitly overwrite documentation
    # propagated from that wrappee onto this wrapper.
    if func_doc is not None:
        assert isinstance(func_doc, str), f'{repr(func_doc)} not string.'
        assert func_doc, '"func_doc" empty.'

        # Document that function.
        func.__doc__ = func_doc
    # Else, that function is undocumented.

    # If debugging this function...
    if is_debug:
        # Render this function debuggable (e.g., via the standard "pdb" module)
        # by exposing this function's definition to the standard "linecache"
        # module under the fake filename synthesized above.
        #
        # Technically, we *COULD* slightly improve the uniquification of this
        # filename for the uncommon edge case when this function does *NOT*
        # wrap a lower-level wrappee (e.g., by embedding the ID of this
        # function that now exists rather than an arbitrary string object).
        # Pragmatically, doing so would prevent external callers from trivially
        # retrieving this function's definition from "linecache". Why? Because
        # reusing the "func_filename" string embedded in this function as
        # "func.__code__.co_filename" trivializes this lookup for callers.
        # Ultimately, sane lookup >>> slightly uniquer filename.
        linecache_cache[func_filename] = (  # type: ignore[assignment]
            len(func_code),  # type: ignore[assignment]  # Y u gotta b diff'rnt Python 3.7? WHY?!
            None,  # usually mtime for determining when to discard files, but
                   # providing None instructs linecache to no-op (never discard)
            func_code.splitlines(keepends=True),
            func_filename,
        )

        # Define and register a cleanup callback removing that function's
        # linecache entry called if and when that function is
        # garbage-collected.
        def _remove_func_linecache_entry():
            linecache_cache.pop(func_filename, None)
        finalize(func, _remove_func_linecache_entry)

    # Return that function.
    return func

# ....................{ COPIERS                            }....................
#FIXME: Consider excising. Although awesome, this is no longer needed.
# from beartype._util.func.utilfunctest import die_unless_func_python
# from types import FunctionType
# def copy_func_shallow(
#     # Mandatory arguments.
#     func: Callable,
#
#     # Optional arguments.
#     exception_cls: Type[Exception] = _BeartypeUtilCallableException,
# ) -> Callable:
#     '''
#     Create and return a new shallow copy of the passed callable.
#
#     Specifically, this function creates and returns a new function sharing with
#     the passed callable the same:
#
#     * Underlying code object (i.e., ``func.__code__``).
#     * Unqualified and fully-qualified names (i.e., ``func.__name__`` and
#       ``func.__qualname__``).
#     * Docstring (i.e., ``func.__doc__``).
#     * Type hints (i.e., ``func.__annotations__``).
#     * Global scope (i.e., ``func.__globals__``).
#     * Fully-qualified module name (i.e., ``func.__module__``).
#     * Default values of optional parameters (i.e., ``f.__defaults__`` and
#       ``f.__kwdefaults__``).
#     * Closure-specific cell variables (i.e., ``f.__closure__``).
#     * Custom public and private attributes.
#
#     Parameters
#     ----------
#     func : Callable
#         Callable to be copied.
#     exception_cls : type, optional
#         Type of exception to raise in the event of a fatal error. Defaults to
#         :exc:`_BeartypeUtilCallableException`.
#
#     Returns
#     ----------
#     Callable
#         Function shallowly copied from the passed callable.
#
#     Raises
#     ----------
#     exception_cls
#         If the passed callable is *not* pure-Python.
#
#     See Also
#     ----------
#     https://stackoverflow.com/a/30714299/2809027
#         StackOverflow answer strongly inspiring this implementation.
#     '''
#
#     # If the passed callable is *NOT* pure-Python, raise an exception.
#     die_unless_func_python(func=func, exception_cls=exception_cls)
#
#     # Function shallowly copied from the passed callable.
#     #
#     # Note that *ALL* pure-Python callables are guaranteed to define the
#     # following dunder attributes.
#     func_copy = FunctionType(
#         func.__code__,
#         func.__globals__,  # type: ignore[attr-defined]
#         func.__name__,
#         func.__defaults__,  # type: ignore[attr-defined]
#         func.__closure__,  # type: ignore[attr-defined]
#     )
#
#     # Shallowly copy all remaining dunder attributes from the original callable
#     # onto this copy *NOT* already copied by the FunctionType.__init__() method
#     # called above.
#     #
#     # Note that *ALL* pure-Python callables are guaranteed to define the
#     # following dunder attributes.
#     func_copy.__annotations__ = func.__annotations__
#     func_copy.__doc__ = func.__doc__
#     func_copy.__kwdefaults__ = func.__kwdefaults__  # type: ignore[attr-defined]
#     func_copy.__module__ = func.__module__
#     func_copy.__qualname__ = func.__qualname__
#
#     # Shallowly copy all custom attributes (i.e., non-dunder attributes
#     # explicitly set by the caller) from the original callable onto this copy.
#     func_copy.__dict__.update(func.__dict__)
#     # print(f'func.__dict__: {func.__dict__}')
#     # print(f'func_copy.__dict__: {func_copy.__dict__}')
#
#     # Return this copy.
#     return func_copy
