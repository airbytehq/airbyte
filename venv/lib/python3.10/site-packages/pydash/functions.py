"""
Functions that wrap other functions.

.. versionadded:: 1.0.0
"""

from inspect import getfullargspec
import itertools
import time
import typing as t

from typing_extensions import Concatenate, Literal, ParamSpec

import pydash as pyd


__all__ = (
    "after",
    "ary",
    "before",
    "conjoin",
    "curry",
    "curry_right",
    "debounce",
    "delay",
    "disjoin",
    "flip",
    "flow",
    "flow_right",
    "iterated",
    "juxtapose",
    "negate",
    "once",
    "over_args",
    "partial",
    "partial_right",
    "rearg",
    "spread",
    "throttle",
    "unary",
    "wrap",
)

T = t.TypeVar("T")
T1 = t.TypeVar("T1")
T2 = t.TypeVar("T2")
T3 = t.TypeVar("T3")
T4 = t.TypeVar("T4")
T5 = t.TypeVar("T5")
P = ParamSpec("P")


class After(t.Generic[P, T]):
    """Wrap a function in an after context."""

    def __init__(self, func: t.Callable[P, T], n: t.SupportsInt) -> None:
        try:
            n = int(n)
            assert n >= 0
        except (ValueError, TypeError, AssertionError):
            n = 0

        self.n = n
        self.func = func

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> t.Union[T, None]:
        """Return results of :attr:`func` after :attr:`n` calls."""
        self.n -= 1

        if self.n <= 0:
            return self.func(*args, **kwargs)

        return None


class Ary(t.Generic[T]):
    """Wrap a function in an ary context."""

    def __init__(self, func: t.Callable[..., T], n: t.Union[t.SupportsInt, None]) -> None:
        try:
            # Type error would be caught
            n = int(n)  # type: ignore
            assert n >= 0
        except (ValueError, TypeError, AssertionError):
            n = None

        self.n = n
        self.func = func

    def __call__(self, *args: t.Any, **kwargs: t.Any) -> T:
        """
        Return results of :attr:`func` with arguments capped to :attr:`n`.

        Only positional arguments are capped. Any number of keyword arguments are allowed.
        """
        cut_args = args[: self.n] if self.n is not None else args

        return self.func(*cut_args, **kwargs)  # type: ignore


class Before(After, t.Generic[P, T]):
    """Wrap a function in a before context."""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> t.Union[T, None]:
        self.n -= 1

        if self.n > 0:
            return self.func(*args, **kwargs)

        return None


class Flow(t.Generic[P, T]):
    """Wrap a function in a flow context."""

    @t.overload
    def __init__(
        self,
        func1: t.Callable[P, T2],
        func2: t.Callable[[T2], T3],
        func3: t.Callable[[T3], T4],
        func4: t.Callable[[T4], T5],
        func5: t.Callable[[T5], T],
        *,
        from_right: bool = True,
    ) -> None:
        ...

    @t.overload
    def __init__(
        self,
        func1: t.Callable[P, T2],
        func2: t.Callable[[T2], T3],
        func3: t.Callable[[T3], T4],
        func4: t.Callable[[T4], T],
        *,
        from_right: bool = True,
    ) -> None:
        ...

    @t.overload
    def __init__(
        self,
        func1: t.Callable[P, T2],
        func2: t.Callable[[T2], T3],
        func3: t.Callable[[T3], T],
        *,
        from_right: bool = True,
    ) -> None:
        ...

    @t.overload
    def __init__(
        self, func1: t.Callable[P, T2], func2: t.Callable[[T2], T], *, from_right: bool = True
    ) -> None:
        ...

    @t.overload
    def __init__(self, func1: t.Callable[P, T], *, from_right: bool = True) -> None:
        ...

    def __init__(self, *funcs, from_right: bool = True) -> None:  # type: ignore
        self.funcs = funcs
        self.from_right = from_right

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        """Return results of composing :attr:`funcs`."""
        funcs = list(self.funcs)
        from_index = -1 if self.from_right else 0

        result = None

        while funcs:
            result = funcs.pop(from_index)(*args, **kwargs)
            # Incompatible type in assignements but needed here
            # type safety is ensured from the `__init__` signature
            args = (result,)  # type: ignore
            kwargs = {}  # type: ignore

        # type safety is ensured from the `__init__` signature
        return result  # type: ignore


class Conjoin(t.Generic[T]):
    """Wrap a set of functions in a conjoin context."""

    def __init__(self, *funcs: t.Callable[[T], t.Any]) -> None:
        self.funcs = funcs

    def __call__(self, obj: t.Iterable[T]) -> bool:
        """Return result of conjoin `obj` with :attr:`funcs` predicates."""

        def iteratee(item: T) -> bool:
            return pyd.every(self.funcs, lambda func: func(item))

        return pyd.every(obj, iteratee)


class Curry(t.Generic[T1, T]):
    """Wrap a function in a curry context."""

    def __init__(self, func, arity, args=None, kwargs=None) -> None:
        self.func = func
        self.arity = len(getfullargspec(func).args) if arity is None else arity
        self.args = () if args is None else args
        self.kwargs = {} if kwargs is None else kwargs

    def __call__(self, *args, **kwargs):
        """Store `args` and `kwargs` and call :attr:`func` if we've reached or exceeded the function
        arity."""
        args = self.compose_args(args)
        kwargs.update(self.kwargs)

        if (len(args) + len(kwargs)) >= self.arity:
            args_arity = self.arity - len(kwargs)
            args = args[: (args_arity if args_arity > 0 else 0)]
            curried = self.func(*args, **kwargs)
        else:
            # NOTE: Use self.__class__ so that subclasses will use their own
            # class to generate next iteration of call.
            curried = self.__class__(self.func, self.arity, args, kwargs)

        return curried

    def compose_args(self, new_args):
        """Combine `self.args` with `new_args` and return."""
        return tuple(list(self.args) + list(new_args))


class CurryOne(Curry[T1, T]):
    def __call__(self, arg_one: T1) -> T:
        return super().__call__(arg_one)  # pragma: no cover


class CurryTwo(Curry[T1, CurryOne[T2, T]]):
    @t.overload
    def __call__(self, arg_one: T1) -> CurryOne[T2, T]:
        ...

    @t.overload
    def __call__(self, arg_one: T1, arg_two: T2) -> T:
        ...

    def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)  # pragma: no cover


class CurryThree(Curry[T1, CurryTwo[T2, T3, T]]):
    @t.overload
    def __call__(self, arg_one: T1) -> CurryTwo[T2, T3, T]:
        ...

    @t.overload
    def __call__(self, arg_one: T1, arg_two: T2) -> CurryOne[T3, T]:
        ...

    @t.overload
    def __call__(self, arg_one: T1, arg_two: T2, arg_three: T3) -> T:
        ...

    def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)  # pragma: no cover


class CurryFour(Curry[T1, CurryThree[T2, T3, T4, T]]):
    @t.overload
    def __call__(self, arg_one: T1) -> CurryThree[T2, T3, T4, T]:
        ...

    @t.overload
    def __call__(self, arg_one: T1, arg_two: T2) -> CurryTwo[T3, T4, T]:
        ...

    @t.overload
    def __call__(self, arg_one: T1, arg_two: T2, arg_three: T3) -> CurryOne[T4, T]:
        ...

    @t.overload
    def __call__(self, arg_one: T1, arg_two: T2, arg_three: T3, arg_four: T4) -> T:
        ...

    def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)  # pragma: no cover


class CurryFive(Curry[T1, CurryFour[T2, T3, T4, T5, T]]):
    @t.overload
    def __call__(self, arg_one: T1) -> CurryFour[T2, T3, T4, T5, T]:
        ...

    @t.overload
    def __call__(self, arg_one: T1, arg_two: T2) -> CurryThree[T3, T4, T5, T]:
        ...

    @t.overload
    def __call__(self, arg_one: T1, arg_two: T2, arg_three: T3) -> CurryTwo[T4, T5, T]:
        ...

    @t.overload
    def __call__(self, arg_one: T1, arg_two: T2, arg_three: T3, arg_four: T4) -> CurryOne[T5, T]:
        ...

    @t.overload
    def __call__(self, arg_one: T1, arg_two: T2, arg_three: T3, arg_four: T4, arg_five: T5) -> T:
        ...

    def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)  # pragma: no cover


class CurryRight(Curry[T5, T]):
    """Wrap a function in a curry-right context."""

    def compose_args(self, new_args):
        return tuple(list(new_args) + list(self.args))


class CurryRightOne(CurryRight[T5, T]):
    def __call__(self, arg_one: T5) -> T:
        return super().__call__(arg_one)  # pragma: no cover


class CurryRightTwo(CurryRight[T5, CurryRightOne[T4, T]]):
    @t.overload
    def __call__(self, arg_one: T5) -> CurryRightOne[T4, T]:
        ...

    @t.overload
    def __call__(self, arg_one: T5, arg_two: T4) -> T:
        ...

    def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)  # pragma: no cover


class CurryRightThree(CurryRight[T5, CurryRightTwo[T4, T3, T]]):
    @t.overload
    def __call__(self, arg_one: T5) -> CurryRightTwo[T4, T3, T]:
        ...

    @t.overload
    def __call__(self, arg_one: T5, arg_two: T4) -> CurryRightOne[T3, T]:
        ...

    @t.overload
    def __call__(self, arg_one: T5, arg_two: T4, arg_three: T3) -> T:
        ...

    def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)  # pragma: no cover


class CurryRightFour(CurryRight[T5, CurryRightThree[T4, T3, T2, T]]):
    @t.overload
    def __call__(self, arg_one: T5) -> CurryRightThree[T4, T3, T2, T]:
        ...

    @t.overload
    def __call__(self, arg_one: T5, arg_two: T4) -> CurryRightTwo[T3, T2, T]:
        ...

    @t.overload
    def __call__(self, arg_one: T5, arg_two: T4, arg_three: T3) -> CurryRightOne[T2, T]:
        ...

    @t.overload
    def __call__(self, arg_one: T5, arg_two: T4, arg_three: T3, arg_four: T2) -> T:
        ...

    def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)  # pragma: no cover


class CurryRightFive(CurryRight[T5, CurryRightFour[T4, T3, T2, T1, T]]):
    @t.overload
    def __call__(self, arg_one: T5) -> CurryRightFour[T4, T3, T2, T1, T]:
        ...

    @t.overload
    def __call__(self, arg_one: T5, arg_two: T4) -> CurryRightThree[T3, T2, T1, T]:
        ...

    @t.overload
    def __call__(self, arg_one: T5, arg_two: T4, arg_three: T3) -> CurryRightTwo[T2, T1, T]:
        ...

    @t.overload
    def __call__(
        self, arg_one: T5, arg_two: T4, arg_three: T3, arg_four: T2
    ) -> CurryRightOne[T1, T]:
        ...

    @t.overload
    def __call__(self, arg_one: T5, arg_two: T4, arg_three: T3, arg_four: T2, arg_five: T1) -> T:
        ...

    def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)  # pragma: no cover


class Debounce(t.Generic[P, T]):
    """Wrap a function in a debounce context."""

    def __init__(
        self, func: t.Callable[P, T], wait: int, max_wait: t.Union[int, Literal[False]] = False
    ) -> None:
        self.func = func
        self.wait = wait
        self.max_wait = max_wait

        self.last_result: t.Union[T, None] = None

        # Initialize last_* times to be prior to the wait periods so that func
        # is primed to be executed on first call.
        self.last_call = pyd.now() - self.wait
        self.last_execution = pyd.now() - max_wait if pyd.is_number(max_wait) else None

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        """
        Execute :attr:`func` if function hasn't been called within last :attr:`wait` milliseconds or
        in last :attr:`max_wait` milliseconds.

        Return results of last successful call.
        """
        present = pyd.now()

        if (present - self.last_call) >= self.wait or (
            self.max_wait and (present - self.last_execution) >= self.max_wait  # type: ignore
        ):
            self.last_result = self.func(*args, **kwargs)
            self.last_execution = present

        self.last_call = present

        # It will be set after first call, cannot be `None` anymore
        return self.last_result  # type: ignore


class Disjoin(t.Generic[T]):
    """Wrap a set of functions in a disjoin context."""

    def __init__(self, *funcs: t.Callable[[T], t.Any]) -> None:
        self.funcs = funcs

    def __call__(self, obj: t.Iterable[T]) -> bool:
        """Return result of disjoin `obj` with :attr:`funcs` predicates."""

        def iteratee(item: T) -> bool:
            return pyd.some(self.funcs, lambda func: func(item))

        return pyd.some(obj, iteratee)


class Flip(object):
    """Wrap a function in a flip context."""

    def __init__(self, func: t.Callable) -> None:
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.func(*reversed(args), **kwargs)


class Iterated(t.Generic[T]):
    """Wrap a function in an iterated context."""

    def __init__(self, func: t.Callable[[T], T]) -> None:
        self.func = func

    def _iteration(self, initial: T) -> t.Iterator[T]:
        """Iterator that composing :attr:`func` with itself."""
        value = initial
        while True:
            value = self.func(value)
            yield value

    def __call__(self, initial: T, n: int) -> T:
        """Return value of calling :attr:`func` `n` times using `initial` as seed value."""
        value = initial
        iteration = self._iteration(value)

        for _ in range(n):
            value = next(iteration)

        return value


class Juxtapose(t.Generic[P, T]):
    """Wrap a function in a juxtapose context."""

    def __init__(self, *funcs: t.Callable[P, T]) -> None:
        self.funcs = funcs

    def __call__(self, *objs: P.args, **kwargs: P.kwargs) -> t.List[T]:
        return [func(*objs, **kwargs) for func in self.funcs]


class OverArgs(object):
    """Wrap a function in an over_args context."""

    def __init__(self, func: t.Callable, *transforms: t.Callable) -> None:
        self.func = func
        self.transforms = pyd.flatten(transforms)

    def __call__(self, *args):
        args = (self.transforms[idx](args) for idx, args in enumerate(args))
        return self.func(*args)


class Negate(t.Generic[P]):
    """Wrap a function in a negate context."""

    def __init__(self, func: t.Callable[P, t.Any]) -> None:
        self.func = func

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> bool:
        """Return negated results of calling :attr:`func`."""
        return not self.func(*args, **kwargs)


class Once(t.Generic[P, T]):
    """Wrap a function in a once context."""

    def __init__(self, func: t.Callable[P, T]) -> None:
        self.func = func
        self.result: t.Union[T, None] = None
        self.called = False

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        """Return results from the first call of :attr:`func`."""
        if not self.called:
            self.result = self.func(*args, **kwargs)
            self.called = True

        # At this point the result will be set, cannot be `None` anymore
        return self.result  # type: ignore


class Partial(t.Generic[T]):
    """Wrap a function in a partial context."""

    def __init__(
        self, func: t.Callable[..., T], args: t.Any, kwargs: t.Any = None, from_right: bool = False
    ) -> None:
        self.func = func
        self.args = args
        self.kwargs = kwargs or {}
        self.from_right = from_right

    def __call__(self, *args: t.Any, **kwargs: t.Any) -> T:
        """
        Return results from :attr:`func` with :attr:`args` + `args`.

        Apply arguments from left or right depending on :attr:`from_right`.
        """
        if self.from_right:
            args = itertools.chain(args, self.args)  # type: ignore
        else:
            args = itertools.chain(self.args, args)  # type: ignore

        kwargs = {**self.kwargs, **kwargs}

        return self.func(*args, **kwargs)


class Rearg(t.Generic[P, T]):
    """Wrap a function in a rearg context."""

    def __init__(self, func: t.Callable[P, T], *indexes: int) -> None:
        self.func = func

        # Index `indexes` by the index value, so we can do a lookup mapping by walking the function
        # arguments.
        self.indexes = {
            src_index: dest_index for dest_index, src_index in enumerate(pyd.flatten(indexes))
        }

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        """Return results from :attr:`func` using rearranged arguments."""
        reargs = {}
        rest = []

        # Walk arguments to ensure each one is added to the final argument list.
        for src_index, arg in enumerate(args):
            # NOTE: dest_index will range from 0 to len(indexes).
            dest_index = self.indexes.get(src_index)

            if dest_index is not None:
                # Remap argument index.
                reargs[dest_index] = arg
            else:
                # Argumnet index is not contained in `indexes` so stick in the back.
                rest.append(arg)

        args = itertools.chain((reargs[key] for key in sorted(reargs)), rest)  # type: ignore

        return self.func(*args, **kwargs)


class Spread(t.Generic[T]):
    """Wrap a function in a spread context."""

    def __init__(self, func: t.Callable[..., T]) -> None:
        self.func = func

    def __call__(self, args: t.Iterable) -> T:
        """Return results from :attr:`func` using array of `args` provided."""
        return self.func(*args)


class Throttle(t.Generic[P, T]):
    """Wrap a function in a throttle context."""

    def __init__(self, func: t.Callable[P, T], wait: int) -> None:
        self.func = func
        self.wait = wait

        self.last_result: t.Union[T, None] = None
        self.last_execution = pyd.now() - self.wait

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        """
        Execute :attr:`func` if function hasn't been called within last :attr:`wait` milliseconds.

        Return results of last successful call.
        """
        present = pyd.now()

        if (present - self.last_execution) >= self.wait:
            self.last_result = self.func(*args, **kwargs)
            self.last_execution = present

        # The last result will be filled on first execution, so it is always `T`
        return self.last_result  # type: ignore


def after(func: t.Callable[P, T], n: t.SupportsInt) -> After[P, T]:
    """
    Creates a function that executes `func`, with the arguments of the created function, only after
    being called `n` times.

    Args:
        func: Function to execute.
        n: Number of times `func` must be called before it is executed.

    Returns:
        Function wrapped in an :class:`After` context.

    Example:

        >>> func = lambda a, b, c: (a, b, c)
        >>> after_func = after(func, 3)
        >>> after_func(1, 2, 3)
        >>> after_func(1, 2, 3)
        >>> after_func(1, 2, 3)
        (1, 2, 3)
        >>> after_func(4, 5, 6)
        (4, 5, 6)

    .. versionadded:: 1.0.0

    .. versionchanged:: 3.0.0
        Reordered arguments to make `func` first.
    """
    return After(func, n)


def ary(func: t.Callable[..., T], n: t.Union[t.SupportsInt, None]) -> Ary[T]:
    """
    Creates a function that accepts up to `n` arguments ignoring any additional arguments. Only
    positional arguments are capped. All keyword arguments are allowed through.

    Args:
        func: Function to cap arguments for.
        n: Number of arguments to accept.

    Returns:
        Function wrapped in an :class:`Ary` context.

    Example:

        >>> func = lambda a, b, c=0, d=5: (a, b, c, d)
        >>> ary_func = ary(func, 2)
        >>> ary_func(1, 2, 3, 4, 5, 6)
        (1, 2, 0, 5)
        >>> ary_func(1, 2, 3, 4, 5, 6, c=10, d=20)
        (1, 2, 10, 20)

    .. versionadded:: 3.0.0
    """
    return Ary(func, n)


def before(func: t.Callable[P, T], n: t.SupportsInt) -> Before[P, T]:
    """
    Creates a function that executes `func`, with the arguments of the created function, until it
    has been called `n` times.

    Args:
        func: Function to execute.
        n: Number of times `func` may be executed.

    Returns:
        Function wrapped in an :class:`Before` context.

    Example:

        >>> func = lambda a, b, c: (a, b, c)
        >>> before_func = before(func, 3)
        >>> before_func(1, 2, 3)
        (1, 2, 3)
        >>> before_func(1, 2, 3)
        (1, 2, 3)
        >>> before_func(1, 2, 3)
        >>> before_func(1, 2, 3)

    .. versionadded:: 1.1.0

    .. versionchanged:: 3.0.0
        Reordered arguments to make `func` first.
    """
    return Before(func, n)


def conjoin(*funcs: t.Callable[[T], t.Any]) -> t.Callable[[t.Iterable[T]], bool]:
    """
    Creates a function that composes multiple predicate functions into a single predicate that tests
    whether **all** elements of an object pass each predicate.

    Args:
        *funcs: Function(s) to conjoin.

    Returns:
        Function(s) wrapped in a :class:`Conjoin` context.

    Example:

        >>> conjoiner = conjoin(lambda x: isinstance(x, int), lambda x: x > 3)
        >>> conjoiner([1, 2, 3])
        False
        >>> conjoiner([1.0, 2, 1])
        False
        >>> conjoiner([4.0, 5, 6])
        False
        >>> conjoiner([4, 5, 6])
        True

    .. versionadded:: 2.0.0
    """
    return Conjoin(*funcs)


@t.overload
def curry(func: t.Callable[[T1], T], arity: t.Union[int, None] = None) -> CurryOne[T1, T]:
    ...


@t.overload
def curry(func: t.Callable[[T1, T2], T], arity: t.Union[int, None] = None) -> CurryTwo[T1, T2, T]:
    ...


@t.overload
def curry(
    func: t.Callable[[T1, T2, T3], T], arity: t.Union[int, None] = None
) -> CurryThree[T1, T2, T3, T]:
    ...


@t.overload
def curry(
    func: t.Callable[[T1, T2, T3, T4], T], arity: t.Union[int, None] = None
) -> CurryFour[T1, T2, T3, T4, T]:
    ...


@t.overload
def curry(
    func: t.Callable[[T1, T2, T3, T4, T5], T], arity: t.Union[int, None] = None
) -> CurryFive[T1, T2, T3, T4, T5, T]:
    ...


def curry(func, arity=None):
    """
    Creates a function that accepts one or more arguments of `func` that when invoked either
    executes `func` returning its result (if all `func` arguments have been provided) or returns a
    function that accepts one or more of the remaining `func` arguments, and so on.

    Args:
        func: Function to curry.
        arity: Number of function arguments that can be accepted by curried
            function. Default is to use the number of arguments that are accepted by `func`.

    Returns:
        Function wrapped in a :class:`Curry` context.

    Example:

        >>> func = lambda a, b, c: (a, b, c)
        >>> currier = curry(func)
        >>> currier = currier(1)
        >>> assert isinstance(currier, Curry)
        >>> currier = currier(2)
        >>> assert isinstance(currier, Curry)
        >>> currier = currier(3)
        >>> currier
        (1, 2, 3)

    .. versionadded:: 1.0.0
    """
    return Curry(func, arity)


@t.overload
def curry_right(
    func: t.Callable[[T1], T], arity: t.Union[int, None] = None
) -> CurryRightOne[T1, T]:
    ...


@t.overload
def curry_right(
    func: t.Callable[[T1, T2], T], arity: t.Union[int, None] = None
) -> CurryRightTwo[T2, T1, T]:
    ...


@t.overload
def curry_right(
    func: t.Callable[[T1, T2, T3], T], arity: t.Union[int, None] = None
) -> CurryRightThree[T3, T2, T1, T]:
    ...


@t.overload
def curry_right(
    func: t.Callable[[T1, T2, T3, T4], T], arity: t.Union[int, None] = None
) -> CurryRightFour[T4, T3, T2, T1, T]:
    ...


@t.overload
def curry_right(func: t.Callable[[T1, T2, T3, T4, T5], T]) -> CurryRightFive[T5, T4, T3, T2, T1, T]:
    ...


def curry_right(func, arity=None):
    """
    This method is like :func:`curry` except that arguments are applied to `func` in the manner of
    :func:`partial_right` instead of :func:`partial`.

    Args:
        func: Function to curry.
        arity: Number of function arguments that can be accepted by curried
            function. Default is to use the number of arguments that are accepted by `func`.

    Returns:
        Function wrapped in a :class:`CurryRight` context.

    Example:

        >>> func = lambda a, b, c: (a, b, c)
        >>> currier = curry_right(func)
        >>> currier = currier(1)
        >>> assert isinstance(currier, CurryRight)
        >>> currier = currier(2)
        >>> assert isinstance(currier, CurryRight)
        >>> currier = currier(3)
        >>> currier
        (3, 2, 1)

    .. versionadded:: 1.1.0
    """
    return CurryRight(func, arity)


def debounce(
    func: t.Callable[P, T], wait: int, max_wait: t.Union[int, Literal[False]] = False
) -> Debounce[P, T]:
    """
    Creates a function that will delay the execution of `func` until after `wait` milliseconds have
    elapsed since the last time it was invoked. Subsequent calls to the debounced function will
    return the result of the last `func` call.

    Args:
        func: Function to execute.
        wait: Milliseconds to wait before executing `func`.
        max_wait (optional): Maximum time to wait before executing `func`.

    Returns:
        Function wrapped in a :class:`Debounce` context.

    .. versionadded:: 1.0.0
    """
    return Debounce(func, wait, max_wait=max_wait)


def delay(func: t.Callable[P, T], wait: int, *args: "P.args", **kwargs: "P.kwargs") -> T:
    """
    Executes the `func` function after `wait` milliseconds. Additional arguments will be provided to
    `func` when it is invoked.

    Args:
        func: Function to execute.
        wait: Milliseconds to wait before executing `func`.
        *args: Arguments to pass to `func`.
        **kwargs: Keyword arguments to pass to `func`.

    Returns:
        Return from `func`.

    .. versionadded:: 1.0.0
    """
    time.sleep(wait / 1000.0)
    return func(*args, **kwargs)


def disjoin(*funcs: t.Callable[[T], t.Any]) -> Disjoin[T]:
    """
    Creates a function that composes multiple predicate functions into a single predicate that tests
    whether **any** elements of an object pass each predicate.

    Args:
        *funcs: Function(s) to disjoin.

    Returns:
        Function(s) wrapped in a :class:`Disjoin` context.

    Example:

        >>> disjoiner = disjoin(lambda x: isinstance(x, float),\
                                lambda x: isinstance(x, int))
        >>> disjoiner([1, '2', '3'])
        True
        >>> disjoiner([1.0, '2', '3'])
        True
        >>> disjoiner(['1', '2', '3'])
        False

    .. versionadded:: 2.0.0
    """
    return Disjoin(*funcs)


@t.overload
def flip(func: t.Callable[[T1, T2, T3, T4, T5], T]) -> t.Callable[[T5, T4, T3, T2, T1], T]:
    ...


@t.overload
def flip(func: t.Callable[[T1, T2, T3, T4], T]) -> t.Callable[[T4, T3, T2, T1], T]:
    ...


@t.overload
def flip(func: t.Callable[[T1, T2, T3], T]) -> t.Callable[[T3, T2, T1], T]:
    ...


@t.overload
def flip(func: t.Callable[[T1, T2], T]) -> t.Callable[[T2, T1], T]:
    ...


@t.overload
def flip(func: t.Callable[[T1], T]) -> t.Callable[[T1], T]:
    ...


def flip(func: t.Callable) -> t.Callable:
    """
    Creates a function that invokes the method with arguments reversed.

    Args:
        func: Function to flip arguments for.

    Returns:
        Function wrapped in a :class:`Flip` context.

    Example:

        >>> flipped = flip(lambda *args: args)
        >>> flipped(1, 2, 3, 4)
        (4, 3, 2, 1)
        >>> flipped = flip(lambda *args: [i * 2 for i in args])
        >>> flipped(1, 2, 3, 4)
        [8, 6, 4, 2]

    .. versionadded:: 4.0.0
    """
    return Flip(func)


@t.overload
def flow(
    func1: t.Callable[P, T2],
    func2: t.Callable[[T2], T3],
    func3: t.Callable[[T3], T4],
    func4: t.Callable[[T4], T5],
    func5: t.Callable[[T5], T],
) -> Flow[P, T]:
    ...


@t.overload
def flow(
    func1: t.Callable[P, T2],
    func2: t.Callable[[T2], T3],
    func3: t.Callable[[T3], T4],
    func4: t.Callable[[T4], T],
) -> Flow[P, T]:
    ...


@t.overload
def flow(
    func1: t.Callable[P, T2],
    func2: t.Callable[[T2], T3],
    func3: t.Callable[[T3], T],
) -> Flow[P, T]:
    ...


@t.overload
def flow(func1: t.Callable[P, T2], func2: t.Callable[[T2], T]) -> Flow[P, T]:
    ...


@t.overload
def flow(func1: t.Callable[P, T]) -> Flow[P, T]:
    ...


def flow(*funcs):
    """
    Creates a function that is the composition of the provided functions, where each successive
    invocation is supplied the return value of the previous. For example, composing the functions
    ``f()``, ``g()``, and ``h()`` produces ``h(g(f()))``.

    Args:
        *funcs: Function(s) to compose.

    Returns:
        Function(s) wrapped in a :class:`Flow` context.

    Example:

        >>> mult_5 = lambda x: x * 5
        >>> div_10 = lambda x: x / 10.0
        >>> pow_2 = lambda x: x ** 2
        >>> ops = flow(sum, mult_5, div_10, pow_2)
        >>> ops([1, 2, 3, 4])
        25.0

    .. versionadded:: 2.0.0

    .. versionchanged:: 2.3.1
        Added :func:`pipe` as alias.

    .. versionchanged:: 4.0.0
        Removed alias ``pipe``.
    """
    return Flow(*funcs, from_right=False)


@t.overload
def flow_right(
    func5: t.Callable[[T4], T],
    func4: t.Callable[[T3], T4],
    func3: t.Callable[[T2], T3],
    func2: t.Callable[[T1], T2],
    func1: t.Callable[P, T1],
) -> Flow[P, T]:
    ...


@t.overload
def flow_right(
    func4: t.Callable[[T3], T],
    func3: t.Callable[[T2], T3],
    func2: t.Callable[[T1], T2],
    func1: t.Callable[P, T1],
) -> Flow[P, T]:
    ...


@t.overload
def flow_right(
    func3: t.Callable[[T2], T],
    func2: t.Callable[[T1], T2],
    func1: t.Callable[P, T1],
) -> Flow[P, T]:
    ...


@t.overload
def flow_right(func2: t.Callable[[T1], T], func1: t.Callable[P, T1]) -> Flow[P, T]:
    ...


@t.overload
def flow_right(func1: t.Callable[P, T]) -> Flow[P, T]:
    ...


def flow_right(*funcs):
    """
    This function is like :func:`flow` except that it creates a function that invokes the provided
    functions from right to left. For example, composing the functions ``f()``, ``g()``, and ``h()``
    produces ``f(g(h()))``.

    Args:
        *funcs: Function(s) to compose.

    Returns:
        Function(s) wrapped in a :class:`Flow` context.

    Example:

        >>> mult_5 = lambda x: x * 5
        >>> div_10 = lambda x: x / 10.0
        >>> pow_2 = lambda x: x ** 2
        >>> ops = flow_right(mult_5, div_10, pow_2, sum)
        >>> ops([1, 2, 3, 4])
        50.0

    .. versionadded:: 1.0.0

    .. versionchanged:: 2.0.0
        Added :func:`flow_right` and made :func:`compose` an alias.

    .. versionchanged:: 2.3.1
        Added :func:`pipe_right` as alias.

    .. versionchanged:: 4.0.0
        Removed aliases ``pipe_right`` and ``compose``.
    """
    return Flow(*funcs, from_right=True)


def iterated(func: t.Callable[[T], T]) -> Iterated[T]:
    """
    Creates a function that is composed with itself. Each call to the iterated function uses the
    previous function call's result as input. Returned :class:`Iterated` instance can be called with
    ``(initial, n)`` where `initial` is the initial value to seed `func` with and `n` is the number
    of times to call `func`.

    Args:
        func: Function to iterate.

    Returns:
        Function wrapped in a :class:`Iterated` context.

    Example:

        >>> doubler = iterated(lambda x: x * 2)
        >>> doubler(4, 5)
        128
        >>> doubler(3, 9)
        1536

    .. versionadded:: 2.0.0
    """
    return Iterated(func)


def juxtapose(*funcs: t.Callable[P, T]) -> Juxtapose[P, T]:
    """
    Creates a function whose return value is a list of the results of calling each `funcs` with the
    supplied arguments.

    Args:
        *funcs: Function(s) to juxtapose.

    Returns:
        Function wrapped in a :class:`Juxtapose` context.

    Example:

        >>> double = lambda x: x * 2
        >>> triple = lambda x: x * 3
        >>> quadruple = lambda x: x * 4
        >>> juxtapose(double, triple, quadruple)(5)
        [10, 15, 20]


    .. versionadded:: 2.0.0
    """
    return Juxtapose(*funcs)


def negate(func: t.Callable[P, t.Any]) -> Negate[P]:
    """
    Creates a function that negates the result of the predicate `func`. The `func` function is
    executed with the arguments of the created function.

    Args:
        func: Function to negate execute.

    Returns:
        Function wrapped in a :class:`Negate` context.

    Example:

        >>> not_is_number = negate(lambda x: isinstance(x, (int, float)))
        >>> not_is_number(1)
        False
        >>> not_is_number('1')
        True

    .. versionadded:: 1.1.0
    """
    return Negate(func)


def once(func: t.Callable[P, T]) -> Once[P, T]:
    """
    Creates a function that is restricted to execute `func` once. Repeat calls to the function will
    return the value of the first call.

    Args:
        func: Function to execute.

    Returns:
        Function wrapped in a :class:`Once` context.

    Example:

        >>> oncer = once(lambda *args: args[0])
        >>> oncer(5)
        5
        >>> oncer(6)
        5

    .. versionadded:: 1.0.0
    """
    return Once(func)


@t.overload
def over_args(
    func: t.Callable[[T1, T2, T3, T4, T5], T],
    transform_one: t.Callable[[T1], T1],
    transform_two: t.Callable[[T2], T2],
    transform_three: t.Callable[[T3], T3],
    transform_four: t.Callable[[T4], T4],
    transform_five: t.Callable[[T5], T5],
) -> t.Callable[[T1, T2, T3, T4, T5], T]:
    ...


@t.overload
def over_args(
    func: t.Callable[[T1, T2, T3, T4], T],
    transform_one: t.Callable[[T1], T1],
    transform_two: t.Callable[[T2], T2],
    transform_three: t.Callable[[T3], T3],
    transform_four: t.Callable[[T4], T4],
) -> t.Callable[[T1, T2, T3, T4], T]:
    ...


@t.overload
def over_args(
    func: t.Callable[[T1, T2, T3], T],
    transform_one: t.Callable[[T1], T1],
    transform_two: t.Callable[[T2], T2],
    transform_three: t.Callable[[T3], T3],
) -> t.Callable[[T1, T2, T3], T]:
    ...


@t.overload
def over_args(
    func: t.Callable[[T1, T2], T],
    transform_one: t.Callable[[T1], T1],
    transform_two: t.Callable[[T2], T2],
) -> t.Callable[[T1, T2], T]:
    ...


@t.overload
def over_args(
    func: t.Callable[[T1], T],
    transform_one: t.Callable[[T1], T1],
) -> t.Callable[[T1], T]:
    ...


def over_args(func: t.Callable, *transforms: t.Callable) -> t.Callable:  # type: ignore
    """
    Creates a function that runs each argument through a corresponding transform function.

    Args:
        func: Function to wrap.
        *transforms: Functions to transform arguments, specified as individual functions
            or lists of functions.

    Returns:
        Function wrapped in a :class:`OverArgs` context.

    Example:

        >>> squared = lambda x: x ** 2
        >>> double = lambda x: x * 2
        >>> modder = over_args(lambda x, y: [x, y], squared, double)
        >>> modder(5, 10)
        [25, 20]

    .. versionadded:: 3.3.0

    .. versionchanged:: 4.0.0
        Renamed from ``mod_args`` to ``over_args``.
    """
    return OverArgs(func, *transforms)


def partial(func: t.Callable[..., T], *args: t.Any, **kwargs: t.Any) -> Partial[T]:
    """
    Creates a function that, when called, invokes `func` with any additional partial arguments
    prepended to those provided to the new function.

    Args:
        func: Function to execute.
        *args: Partial arguments to prepend to function call.
        **kwargs: Partial keyword arguments to bind to function call.

    Returns:
        Function wrapped in a :class:`Partial` context.

    Example:

        >>> dropper = partial(lambda array, n: array[n:], [1, 2, 3, 4])
        >>> dropper(2)
        [3, 4]
        >>> dropper(1)
        [2, 3, 4]
        >>> myrest = partial(lambda array, n: array[n:], n=1)
        >>> myrest([1, 2, 3, 4])
        [2, 3, 4]

    .. versionadded:: 1.0.0
    """
    return Partial(func, args, kwargs)


def partial_right(func: t.Callable[..., T], *args: t.Any, **kwargs: t.Any) -> Partial[T]:
    """
    This method is like :func:`partial` except that partial arguments are appended to those provided
    to the new function.

    Args:
        func: Function to execute.
        *args: Partial arguments to append to function call.
        **kwargs: Partial keyword arguments to bind to function call.

    Returns:
        Function wrapped in a :class:`Partial` context.

    Example:

        >>> myrest = partial_right(lambda array, n: array[n:], 1)
        >>> myrest([1, 2, 3, 4])
        [2, 3, 4]

    .. versionadded:: 1.0.0
    """
    return Partial(func, args, kwargs, from_right=True)


def rearg(func: t.Callable[P, T], *indexes: int) -> Rearg[P, T]:
    """
    Creates a function that invokes `func` with arguments arranged according to the specified
    indexes where the argument value at the first index is provided as the first argument, the
    argument value at the second index is provided as the second argument, and so on.

    Args:
        func: Function to rearrange arguments for.
        *indexes: The arranged argument indexes.

    Returns:
        Function wrapped in a :class:`Rearg` context.

    Example:

        >>> jumble = rearg(lambda *args: args, 1, 2, 3)
        >>> jumble(1, 2, 3)
        (2, 3, 1)
        >>> jumble('a', 'b', 'c', 'd', 'e')
        ('b', 'c', 'd', 'a', 'e')

    .. versionadded:: 3.0.0
    """
    return Rearg(func, *indexes)


def spread(func: t.Callable[..., T]) -> Spread[T]:
    """
    Creates a function that invokes `func` with the array of arguments provided to the created
    function.

    Args:
        func: Function to spread.

    Returns:
        Function wrapped in a :class:`Spread` context.

    Example:

        >>> greet = spread(lambda *people: 'Hello ' + ', '.join(people) + '!')
        >>> greet(['Mike', 'Don', 'Leo'])
        'Hello Mike, Don, Leo!'

    .. versionadded:: 3.1.0
    """
    return Spread(func)


def throttle(func: t.Callable[P, T], wait: int) -> Throttle[P, T]:
    """
    Creates a function that, when executed, will only call the `func` function at most once per
    every `wait` milliseconds. Subsequent calls to the throttled function will return the result of
    the last `func` call.

    Args:
        func: Function to throttle.
        wait: Milliseconds to wait before calling `func` again.

    Returns:
        Results of last `func` call.

    .. versionadded:: 1.0.0
    """
    return Throttle(func, wait)


def unary(func: t.Callable[..., T]) -> Ary[T]:
    """
    Creates a function that accepts up to one argument, ignoring any additional arguments.

    Args:
        func: Function to cap arguments for.

    Returns:
        Function wrapped in an :class:`Ary` context.

    Example:

        >>> func = lambda a, b=1, c=0, d=5: (a, b, c, d)
        >>> unary_func = unary(func)
        >>> unary_func(1, 2, 3, 4, 5, 6)
        (1, 1, 0, 5)
        >>> unary_func(1, 2, 3, 4, 5, 6, b=0, c=10, d=20)
        (1, 0, 10, 20)

    .. versionadded:: 4.0.0
    """
    return Ary(func, 1)


def wrap(value: T1, func: t.Callable[Concatenate[T1, P], T]) -> Partial[T]:
    """
    Creates a function that provides value to the wrapper function as its first argument. Additional
    arguments provided to the function are appended to those provided to the wrapper function.

    Args:
        value: Value provided as first argument to function call.
        func: Function to execute.

    Returns:
        Function wrapped in a :class:`Partial` context.

    Example:

        >>> wrapper = wrap('hello', lambda *args: args)
        >>> wrapper(1, 2)
        ('hello', 1, 2)

    .. versionadded:: 1.0.0
    """
    return Partial(func, (value,))
