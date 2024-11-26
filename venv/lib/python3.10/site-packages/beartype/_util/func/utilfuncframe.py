#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **call stack frame utilities** (i.e., callables introspecting the
current stack of frame objects, encapsulating the linear chain of calls to
external callables underlying the call to the current callable).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
import sys
from beartype.roar._roarexc import _BeartypeUtilCallFrameException
from beartype.typing import (
    Callable,
    Iterable,
    Optional,
)
from beartype._cave._cavefast import CallableFrameType
from beartype._data.hint.datahinttyping import TypeException

# ....................{ GETTERS                            }....................
#FIXME: Mypy insists this getter can return "None" in certain edge cases. But...
#what are those? Official documentation is seemingly silent on the issue. *sigh*
get_frame: Optional[Callable[[int], Optional[CallableFrameType]]] = getattr(
    sys, '_getframe', None)
'''
Private low-level :func:`sys._getframe` getter if the active Python interpreter
declares this getter *or* :data:`None` otherwise (i.e., if this interpreter does
*not* declare this getter).

All standard Python interpreters supported by this package including both
CPython *and* PyPy declare this getter. Ergo, this attribute should *always* be
a valid callable rather than :data:`None`.

If this getter is *not* :data:`None`, this getter's signature and docstring
under CPython resembles:

::

    _getframe([depth]) -> frameobject

    Return a frame object from the call stack.  If optional integer depth is
    given, return the frame object that many calls below the top of the
    stack. If that is deeper than the call stack, ValueError is raised. The
    default for depth is zero, returning the frame at the top of the call
    stack.

    Frame objects provide these attributes:
        f_back          next outer frame object (this frame's caller)
        f_builtins      built-in namespace seen by this frame
        f_code          code object being executed in this frame
        f_globals       global namespace seen by this frame
        f_lasti         index of last attempted instruction in bytecode
        f_lineno        current line number in Python source code
        f_locals        local namespace seen by this frame
        f_trace         tracing function for this frame, or None

Parameters
----------
depth : int
    0-based index of the stack frame on the current call stack to be returned.
    Defaults to 0, signifying the stack frame encapsulating the lexical scope
    directly calling this getter.

Returns
----------
CallableFrameType
    Stack frame with the passed index on the current call stack.

Raises
----------
ValueError
     If this index exceeds the **height** (i.e., total number of stack frames)
     of the current call stack.
'''

#FIXME: Preserve until we inevitably require this getter, please.
#def get_frame_or_none(ignore_frames: int) -> Optional[FrameType]:
#    try:
#        return get_frame(ignore_frames + 1)
#    except ValueError:
#        return None
#def get_frame_caller_or_none() -> Optional[FrameType]:
#    return get_frame_or_none(ignore_frames=2)

# ....................{ GETTERS ~ name                     }....................
def get_frame_basename(
    # Mandatory parameters.
    frame: CallableFrameType,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilCallFrameException,
) -> str:
    '''
    **Unqualified basename** (e.g., function name, method name excluding parent
    classname) of the callable whose code object is that of the passed **stack
    frame** (i.e., :class:`types.CallableFrameType` instance encapsulating all
    metadata describing a single call on the current call stack).

    Parameters
    ----------
    frame : CallableFrameType
        Stack frame to be inspected.

    Raises
    ----------
    exception_cls
         If that callable has *no* code object and is thus *not* pure-Python.
    '''

    # Avoid circular import dependencies.
    from beartype._util.func.utilfunccodeobj import get_func_codeobj

    # Code object underlying the callable encapsulated by this frame if that
    # callable is pure-Python *OR* raise an exception otherwise (i.e., if that
    # callable is C-based).
    func_codeobj = get_func_codeobj(func=frame, exception_cls=exception_cls)

    # Return the unqualified basename of that callable.
    return func_codeobj.co_name


#FIXME: Unit test us up, please.
def get_frame_package_name(
    # Mandatory parameters.
    frame: CallableFrameType,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilCallFrameException,
) -> str:
    '''
    **Fully-qualified name** (i.e., ``.``-delimited name prefixed by the
    declaring package) of the parent package of the child module declaring the
    callable whose code object is that of the passed **stack frame** (i.e.,
    :class:`types.CallableFrameType` instance encapsulating all metadata
    describing a single call on the current call stack).

    Parameters
    ----------
    frame : CallableFrameType
        Stack frame to be inspected.
    exception_cls : TypeException, optional
        Type of exception to be raised in the event of a fatal error. Defaults
        to :class:`._BeartypeUtilCallFrameException`.

    Returns
    ----------
    str
        Fully-qualified name of the parent package of the child module declaring
        that callable.

    Raises
    ----------
    exception_cls
         If that callable has *no* code object and is thus *not* pure-Python.
    '''

    # Fully-qualified name of the parent package of the child module declaring
    # the callable whose code object is that of this stack frame's if that
    # module declares its name *OR* the empty string otherwise (e.g., if that
    # module is either a top-level module or script residing outside any parent
    # package structure).
    frame_package_name = frame.f_globals.get('__package__')

    #FIXME: Is "pragma: no cover" accurate here? Is this condition untestable?
    # If that module has *NO* parent package...
    if not frame_package_name:  # pragma: no cover
        # Fully-qualified name of that child module.
        frame_module_name = frame.f_globals.get('__name__')

        # Unqualified basename of that callable.
        frame_basename = get_frame_basename(
            frame=frame, exception_cls=exception_cls)

        # Raise an exception.
        raise exception_cls(
            f'Callable "{frame_module_name}.{frame_basename}()" '
            f'package not found '
            f'(i.e., top-level module or script "{frame_module_name}" '
            f'resides outside any parent package).'
        )
    # Else, that module has a parent package.

    # Return the name of this parent package.
    return frame_package_name

# ....................{ ITERATORS                          }....................
def iter_frames(
    # Optional parameters.
    func_stack_frames_ignore: int = 0,
) -> Iterable[CallableFrameType]:
    '''
    Generator yielding one **frame** (i.e., :class:`types.CallableFrameType` instance)
    for each call on the current **call stack** (i.e., stack of frame objects,
    encapsulating the linear chain of calls to external callables underlying
    the current call to this callable).

    Notably, for each:

    * **C-based callable call** (i.e., call of a C-based rather than
      pure-Python callable), this generator yields one frame encapsulating *no*
      code object. Only pure-Python frame objects have code objects.
    * **Class-scoped callable call** (i.e., call of an arbitrary callable
      occurring at class scope rather than from within the body of a callable
      or class, typically due to a method being decorated), this generator
      yields one frame ``func_frame`` for that class ``cls`` such that
      ``func_frame.f_code.co_name == cls.__name__`` (i.e., the name of the code
      object encapsulated by that frame is the unqualified name of the class
      encapsulating the lexical scope of this call). Actually, we just made all
      of that up. That is *probably* (but *not* necessarily) the case. Research
      is warranted.
    * **Module-scoped callable call** (i.e., call of an arbitrary callable
      occurring at module scope rather than from within the body of a callable
      or class, typically due to a function or class being decorated), this
      generator yields one frame ``func_frame`` such that
      ``func_frame.f_code.co_name == '<module>'`` (i.e., the name of the code
      object encapsulated by that frame is the placeholder string assigned by
      the active Python interpreter to all scopes encapsulating the top-most
      lexical scope of a module in the current call stack).

    The above constraints imply that frames yielded by this generator *cannot*
    be assumed to encapsulate code objects. See the "Examples" subsection for
    standard logic handling this edge case.

    Caveats
    ----------
    **This high-level iterator requires the private low-level**
    :func:`sys._getframe` **getter.** If that getter is undefined, this iterator
    reduces to the empty generator yielding nothing rather than raising an
    exception. Since all standard Python implementations (e.g., CPython, PyPy)
    define that getter, this should typically *not* be a real-world concern.

    Parameters
    ----------
    func_stack_frames_ignore : int, optional
        Number of frames on the call stack to be ignored (i.e., silently
        incremented past). Defaults to 0.

    Returns
    ----------
    Iterable[CallableFrameType]
        Generator yielding one frame for each call on the current call stack.

    See Also
    ----------
    :func:`get_frame`
        Further details on stack frame objects.

    Examples
    ----------
        >>> from beartype._util.func.utilfunccodeobj import (
        ...     get_func_codeobj_or_none)
        >>> from beartype._util.func.utilfuncframe import iter_frames

        # For each stack frame on the call stack...
        >>> for func_frame in iter_frames():
        ...     # Code object underlying this frame's scope if this scope is
        ...     # pure-Python *OR* "None" otherwise.
        ...     func_frame_codeobj = get_func_codeobj_or_none(func_frame)
        ...
        ...     # If this code object does *NOT* exist, this scope is C-based.
        ...     # In this case, silently ignore this scope and proceed to the
        ...     # next frame in the call stack.
        ...     if func_frame_codeobj is None:
        ...         continue
        ...     # Else, this code object exists, implying this scope to be
        ...     # pure-Python.
        ...
        ...     # Fully-qualified name of this scope's module.
        ...     func_frame_module_name = func_frame.f_globals['__name__']
        ...
        ...     # Unqualified name of this scope.
        ...     func_frame_name = func_frame_codeobj.co_name
        ...
        ...     # Print the fully-qualified name of this scope.
        ...     print(f'On {func_frame_module_name}.{func_frame_name}()!')
    '''
    assert isinstance(func_stack_frames_ignore, int), (
        f'{func_stack_frames_ignore} not integer.')
    assert func_stack_frames_ignore >= 0, (
        f'{func_stack_frames_ignore} negative.')

    # If the active Python interpreter fails to declare the private
    # sys._getframe() getter, reduce to the empty generator (i.e., noop).
    if get_frame is None:  # pragma: no cover
        yield from ()
        return
    # Else, the active Python interpreter declares the sys._getframe() getter.

    # Attempt to obtain the...
    try:
        # Next non-ignored frame following the last ignored frame, ignoring an
        # additional frame embodying the current call to this iterator.
        func_frame = get_frame(func_stack_frames_ignore + 1)  # type: ignore[misc]
    # If doing so raises a "ValueError" exception...
    except ValueError as value_error:
        # Whose message matches this standard boilerplate, the caller requested
        # that this generator ignore more stack frames than currently exist on
        # the call stack. Permitting this exception to unwind the call stack
        # would only needlessly increase the fragility of this already fragile
        # mission-critical generator. Instead, swallow this exception and
        # silently reduce to the empty generator (i.e., noop).
        if str(value_error) == 'call stack is not deep enough':
            yield from ()
            return
        # Whose message does *NOT* match this standard boilerplate, an
        # unexpected exception occurred. In this case, re-raise this exception.

        raise
    # Else, doing so raised *NO* "ValueError" exception.
    # print(f'start frame: {repr(func_frame)}')

    # While at least one frame remains on the call stack...
    while func_frame:
        # print(f'current frame: {repr(func_frame)}')

        # Yield this frame to the caller.
        yield func_frame

        # Iterate to the next frame on the call stack.
        func_frame = func_frame.f_back
