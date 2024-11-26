"""
Method chaining interface.

.. versionadded:: 1.0.0
"""

import typing as t

import pydash as pyd
from pydash.exceptions import InvalidMethod

from ..helpers import UNSET, Unset
from .all_funcs import AllFuncs


__all__ = (
    "chain",
    "tap",
    "thru",
)

Value_coT = t.TypeVar("Value_coT", covariant=True)
T = t.TypeVar("T")
T2 = t.TypeVar("T2")


class Chain(AllFuncs, t.Generic[Value_coT]):
    """Enables chaining of :attr:`module` functions."""

    #: Object that contains attribute references to available methods.
    module = pyd
    invalid_method_exception = InvalidMethod

    def __init__(self, value: t.Union[Value_coT, Unset] = UNSET) -> None:
        self._value = value

    def _wrap(self, func) -> "ChainWrapper":
        """Implement `AllFuncs` interface."""
        return ChainWrapper(self._value, func)

    def value(self) -> Value_coT:
        """
        Return current value of the chain operations.

        Returns:
            Current value of chain operations.
        """
        return self(self._value)

    def to_string(self) -> str:
        """
        Return current value as string.

        Returns:
            Current value of chain operations casted to ``str``.
        """
        return self.module.to_string(self.value())

    def commit(self) -> "Chain[Value_coT]":
        """
        Executes the chained sequence and returns the wrapped result.

        Returns:
            New instance of :class:`Chain` with resolved value from
                previous :class:`Class`.
        """
        return Chain(self.value())

    def plant(self, value: t.Any) -> "Chain[Value_coT]":
        """
        Return a clone of the chained sequence planting `value` as the wrapped value.

        Args:
            value: Value to plant as the initial chain value.
        """
        # pylint: disable=no-member,maybe-no-member
        wrapper = self._value
        wrappers = []

        if hasattr(wrapper, "_value"):
            wrappers = [wrapper]

            while isinstance(wrapper._value, ChainWrapper):
                wrapper = wrapper._value  # type: ignore
                wrappers.insert(0, wrapper)

        clone: Chain[t.Any] = Chain(value)

        for wrap in wrappers:
            clone = ChainWrapper(clone._value, wrap.method)(  # type: ignore
                *wrap.args, **wrap.kwargs  # type: ignore
            )

        return clone

    def __call__(self, value) -> Value_coT:
        """
        Return result of passing `value` through chained methods.

        Args:
            value: Initial value to pass through chained methods.

        Returns:
            Result of method chain evaluation of `value`.
        """
        if isinstance(self._value, ChainWrapper):
            # pylint: disable=maybe-no-member
            value = self._value.unwrap(value)
        return value


class ChainWrapper(t.Generic[Value_coT]):
    """Wrap :class:`Chain` method call within a :class:`ChainWrapper` context."""

    def __init__(self, value: Value_coT, method) -> None:
        self._value = value
        self.method = method
        self.args = ()
        self.kwargs: t.Dict = {}

    def _generate(self):
        """Generate a copy of this instance."""
        # pylint: disable=attribute-defined-outside-init
        new = self.__class__.__new__(self.__class__)
        new.__dict__ = self.__dict__.copy()
        return new

    def unwrap(self, value=UNSET):
        """
        Execute :meth:`method` with :attr:`_value`, :attr:`args`, and :attr:`kwargs`.

        If :attr:`_value` is an instance of :class:`ChainWrapper`, then unwrap it before calling
        :attr:`method`.
        """
        # Generate a copy of ourself so that we don't modify the chain wrapper
        # _value directly. This way if we are late passing a value, we don't
        # "freeze" the chain wrapper value when a value is first passed.
        # Otherwise, we'd locked the chain wrapper value permanently and not be
        # able to reuse it.
        wrapper = self._generate()

        if isinstance(wrapper._value, ChainWrapper):
            # pylint: disable=no-member,maybe-no-member
            wrapper._value = wrapper._value.unwrap(value)
        elif not isinstance(value, ChainWrapper) and value is not UNSET:
            # Override wrapper's initial value.
            wrapper._value = value

        if wrapper._value is not UNSET:
            value = wrapper._value

        return wrapper.method(value, *wrapper.args, **wrapper.kwargs)

    def __call__(self, *args, **kwargs):
        """
        Invoke the :attr:`method` with :attr:`value` as the first argument and return a new
        :class:`Chain` object with the return value.

        Returns:
            New instance of :class:`Chain` with the results of :attr:`method` passed in as
                value.
        """
        self.args = args
        self.kwargs = kwargs
        return Chain(self)


class _Dash(object):
    """Class that provides attribute access to valid :mod:`pydash` methods and callable access to
    :mod:`pydash` method chaining."""

    def __getattr__(self, attr):
        """Proxy to :meth:`Chain.get_method`."""
        return Chain.get_method(attr)

    def __call__(self, value: t.Union[Value_coT, Unset] = UNSET) -> Chain[Value_coT]:
        """Return a new instance of :class:`Chain` with `value` as the seed."""
        return Chain(value)


def chain(value: t.Union[T, Unset] = UNSET) -> Chain[T]:
    """
    Creates a :class:`Chain` object which wraps the given value to enable intuitive method chaining.
    Chaining is lazy and won't compute a final value until :meth:`Chain.value` is called.

    Args:
        value: Value to initialize chain operations with.

    Returns:
        Instance of :class:`Chain` initialized with `value`.

    Example:

        >>> chain([1, 2, 3, 4]).map(lambda x: x * 2).sum().value()
        20
        >>> chain().map(lambda x: x * 2).sum()([1, 2, 3, 4])
        20

        >>> summer = chain([1, 2, 3, 4]).sum()
        >>> new_summer = summer.plant([1, 2])
        >>> new_summer.value()
        3
        >>> summer.value()
        10

        >>> def echo(item): print(item)
        >>> summer = chain([1, 2, 3, 4]).for_each(echo).sum()
        >>> committed = summer.commit()
        1
        2
        3
        4
        >>> committed.value()
        10
        >>> summer.value()
        1
        2
        3
        4
        10

    .. versionadded:: 1.0.0

    .. versionchanged:: 2.0.0
        Made chaining lazy.

    .. versionchanged:: 3.0.0

        - Added support for late passing of `value`.
        - Added :meth:`Chain.plant` for replacing initial chain value.
        - Added :meth:`Chain.commit` for returning a new :class:`Chain` instance initialized with
          the results from calling :meth:`Chain.value`.
    """
    return Chain(value)


def tap(value: T, interceptor: t.Callable[[T], t.Any]) -> T:
    """
    Invokes `interceptor` with the `value` as the first argument and then returns `value`. The
    purpose of this method is to "tap into" a method chain in order to perform operations on
    intermediate results within the chain.

    Args:
        value: Current value of chain operation.
        interceptor: Function called on `value`.

    Returns:
        `value` after `interceptor` call.

    Example:

        >>> data = []
        >>> def log(value): data.append(value)
        >>> chain([1, 2, 3, 4]).map(lambda x: x * 2).tap(log).value()
        [2, 4, 6, 8]
        >>> data
        [[2, 4, 6, 8]]

    .. versionadded:: 1.0.0
    """
    interceptor(value)
    return value


def thru(value: T, interceptor: t.Callable[[T], T2]) -> T2:
    """
    Returns the result of calling `interceptor` on `value`. The purpose of this method is to pass
    `value` through a function during a method chain.

    Args:
        value: Current value of chain operation.
        interceptor: Function called with `value`.

    Returns:
        Results of ``interceptor(value)``.

    Example:

        >>> chain([1, 2, 3, 4]).thru(lambda x: x * 2).value()
        [1, 2, 3, 4, 1, 2, 3, 4]

    .. versionadded:: 2.0.0
    """
    return interceptor(value)
