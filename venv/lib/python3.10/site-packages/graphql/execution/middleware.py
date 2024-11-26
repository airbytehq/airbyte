from functools import partial, reduce
from inspect import isfunction

from typing import Callable, Iterator, Dict, List, Tuple, Any, Optional

__all__ = ["MiddlewareManager"]

GraphQLFieldResolver = Callable[..., Any]


class MiddlewareManager:
    """Manager for the middleware chain.

    This class helps to wrap resolver functions with the provided middleware functions
    and/or objects. The functions take the next middleware function as first argument.
    If middleware is provided as an object, it must provide a method ``resolve`` that is
    used as the middleware function.

    Note that since resolvers return "AwaitableOrValue"s, all middleware functions
    must be aware of this and check whether values are awaitable before awaiting them.
    """

    # allow custom attributes (not used internally)
    __slots__ = "__dict__", "middlewares", "_middleware_resolvers", "_cached_resolvers"

    _cached_resolvers: Dict[GraphQLFieldResolver, GraphQLFieldResolver]
    _middleware_resolvers: Optional[List[Callable]]

    def __init__(self, *middlewares: Any):
        self.middlewares = middlewares
        self._middleware_resolvers = (
            list(get_middleware_resolvers(middlewares)) if middlewares else None
        )
        self._cached_resolvers = {}

    def get_field_resolver(
        self, field_resolver: GraphQLFieldResolver
    ) -> GraphQLFieldResolver:
        """Wrap the provided resolver with the middleware.

        Returns a function that chains the middleware functions with the provided
        resolver function.
        """
        if self._middleware_resolvers is None:
            return field_resolver
        if field_resolver not in self._cached_resolvers:
            self._cached_resolvers[field_resolver] = reduce(
                lambda chained_fns, next_fn: partial(next_fn, chained_fns),
                self._middleware_resolvers,
                field_resolver,
            )
        return self._cached_resolvers[field_resolver]


def get_middleware_resolvers(middlewares: Tuple[Any, ...]) -> Iterator[Callable]:
    """Get a list of resolver functions from a list of classes or functions."""
    for middleware in middlewares:
        if isfunction(middleware):
            yield middleware
        else:  # middleware provided as object with 'resolve' method
            resolver_func = getattr(middleware, "resolve", None)
            if resolver_func is not None:
                yield resolver_func
