from functools import wraps
from typing import Any, Callable, Type


class LazyPassDecorator:
    def __init__(self, cls: Type[Any], *args: Any, **kwargs: Any) -> None:
        self.cls = cls
        self.args = args
        self.kwargs = kwargs

    def __call__(self, f: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(f)
        def decorated_function(*args: Any, **kwargs: Any) -> Any:
            # Check if the kwargs already contain the arguments being passed by the decorator
            decorator_kwargs = {k: v for k, v in self.kwargs.items() if k not in kwargs}
            # Create an instance of the class
            instance = self.cls(*self.args, **decorator_kwargs)
            # If function has **kwargs, we can put the instance there
            if 'kwargs' in kwargs:
                kwargs['kwargs'] = instance
            # Otherwise, add it to positional arguments
            else:
                args = (*args, instance)
            return f(*args, **kwargs)
        return decorated_function
