from functools import lru_cache, partial, singledispatch
from typing import Any, Callable, Dict, Generic, List, Optional, Tuple, TypeVar, Union

from attrs import Factory, define, field

from cattrs._compat import TypeAlias

T = TypeVar("T")

TargetType: TypeAlias = Any
UnstructuredValue: TypeAlias = Any
StructuredValue: TypeAlias = Any

StructureHook: TypeAlias = Callable[[UnstructuredValue, TargetType], StructuredValue]
UnstructureHook: TypeAlias = Callable[[StructuredValue], UnstructuredValue]

Hook = TypeVar("Hook", StructureHook, UnstructureHook)
HookFactory: TypeAlias = Callable[[TargetType], Hook]


@define
class _DispatchNotFound:
    """A dummy object to help signify a dispatch not found."""


@define
class FunctionDispatch:
    """
    FunctionDispatch is similar to functools.singledispatch, but
    instead dispatches based on functions that take the type of the
    first argument in the method, and return True or False.

    objects that help determine dispatch should be instantiated objects.
    """

    _handler_pairs: List[
        Tuple[Callable[[Any], bool], Callable[[Any, Any], Any], bool]
    ] = Factory(list)

    def register(
        self,
        can_handle: Callable[[Any], bool],
        func: Callable[..., Any],
        is_generator=False,
    ) -> None:
        self._handler_pairs.insert(0, (can_handle, func, is_generator))

    def dispatch(self, typ: Any) -> Optional[Callable[..., Any]]:
        """
        Return the appropriate handler for the object passed.
        """
        for can_handle, handler, is_generator in self._handler_pairs:
            # can handle could raise an exception here
            # such as issubclass being called on an instance.
            # it's easier to just ignore that case.
            try:
                ch = can_handle(typ)
            except Exception:  # noqa: S112
                continue
            if ch:
                if is_generator:
                    return handler(typ)

                return handler
        return None

    def get_num_fns(self) -> int:
        return len(self._handler_pairs)

    def copy_to(self, other: "FunctionDispatch", skip: int = 0) -> None:
        other._handler_pairs = self._handler_pairs[:-skip] + other._handler_pairs


@define
class MultiStrategyDispatch(Generic[Hook]):
    """
    MultiStrategyDispatch uses a combination of exact-match dispatch,
    singledispatch, and FunctionDispatch.

    :param fallback_factory: A hook factory to be called when a hook cannot be
        produced.

    ..  versionchanged:: 23.2.0
        Fallbacks are now factories.
    """

    _fallback_factory: HookFactory[Hook]
    _direct_dispatch: Dict = field(init=False, factory=dict)
    _function_dispatch: FunctionDispatch = field(init=False, factory=FunctionDispatch)
    _single_dispatch: Any = field(
        init=False, factory=partial(singledispatch, _DispatchNotFound)
    )
    dispatch: Callable[[TargetType], Hook] = field(
        init=False,
        default=Factory(
            lambda self: lru_cache(maxsize=None)(self._dispatch), takes_self=True
        ),
    )

    def _dispatch(self, typ: TargetType) -> Hook:
        try:
            dispatch = self._single_dispatch.dispatch(typ)
            if dispatch is not _DispatchNotFound:
                return dispatch
        except Exception:  # noqa: S110
            pass

        direct_dispatch = self._direct_dispatch.get(typ)
        if direct_dispatch is not None:
            return direct_dispatch

        res = self._function_dispatch.dispatch(typ)
        return res if res is not None else self._fallback_factory(typ)

    def register_cls_list(self, cls_and_handler, direct: bool = False) -> None:
        """Register a class to direct or singledispatch."""
        for cls, handler in cls_and_handler:
            if direct:
                self._direct_dispatch[cls] = handler
            else:
                self._single_dispatch.register(cls, handler)
                self.clear_direct()
        self.dispatch.cache_clear()

    def register_func_list(
        self,
        pred_and_handler: List[
            Union[
                Tuple[Callable[[Any], bool], Any],
                Tuple[Callable[[Any], bool], Any, bool],
            ]
        ],
    ):
        """
        Register a predicate function to determine if the handle
        should be used for the type.
        """
        for tup in pred_and_handler:
            if len(tup) == 2:
                func, handler = tup
                self._function_dispatch.register(func, handler)
            else:
                func, handler, is_gen = tup
                self._function_dispatch.register(func, handler, is_generator=is_gen)
        self.clear_direct()
        self.dispatch.cache_clear()

    def clear_direct(self) -> None:
        """Clear the direct dispatch."""
        self._direct_dispatch.clear()

    def clear_cache(self) -> None:
        """Clear all caches."""
        self._direct_dispatch.clear()
        self.dispatch.cache_clear()

    def get_num_fns(self) -> int:
        return self._function_dispatch.get_num_fns()

    def copy_to(self, other: "MultiStrategyDispatch", skip: int = 0) -> None:
        self._function_dispatch.copy_to(other._function_dispatch, skip=skip)
        for cls, fn in self._single_dispatch.registry.items():
            other._single_dispatch.register(cls, fn)
        other.clear_cache()
