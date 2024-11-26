import dataclasses
import inspect
import json
import logging
import types
from abc import ABC, abstractmethod, abstractproperty
from collections.abc import Callable, Mapping
from functools import cached_property
from typing import (
    Any,
    Generic,
    ParamSpec,
    TypeAlias,
    cast,
    get_type_hints,
    overload,
)

import cattrs
from graphql.pyutils import camel_to_snake
from typing_extensions import Self, TypeVar, override

import dagger
from dagger import dag

from ._arguments import Parameter
from ._converter import to_typedef
from ._exceptions import UserError
from ._types import APIName, PythonName
from ._utils import (
    asyncify,
    await_maybe,
    get_alt_constructor,
    get_arg_name,
    get_doc,
    transform_error,
)

logger = logging.getLogger(__name__)

R = TypeVar("R", infer_variance=True)
P = ParamSpec("P")

Func: TypeAlias = Callable[P, R]


@dataclasses.dataclass(kw_only=True, slots=True)
class Resolver(ABC):
    original_name: PythonName
    name: APIName = dataclasses.field(repr=False)
    doc: str | None = dataclasses.field(repr=False)

    # Used for instance methods, to get the parent class for the `self` argument.
    # NB: In a FunctionResolver, if `wrapped_func` is a class, it's only useful
    # to know if the class's constructor is being added to another class.
    origin: type | None

    @abstractproperty
    def return_type(self) -> type:
        ...

    @abstractmethod
    def register(self, typedef: dagger.TypeDef) -> dagger.TypeDef:
        return typedef

    @abstractmethod
    async def get_result(
        self,
        converter: cattrs.Converter,
        root: object | None,
        inputs: Mapping[APIName, Any],
    ) -> Any:
        ...


@dataclasses.dataclass(kw_only=True, slots=True)
class FieldResolver(Resolver):
    type_annotation: type
    is_optional: bool

    @override
    def register(self, typedef: dagger.TypeDef) -> dagger.TypeDef:
        return typedef.with_field(
            self.name,
            to_typedef(self.type_annotation).with_optional(self.is_optional),
            description=self.doc or None,
        )

    @override
    async def get_result(
        self,
        _: cattrs.Converter,
        root: object | None,
        inputs: Mapping[APIName, Any],
    ) -> Any:
        # NB: This is only useful in unit tests because the API server
        # resolves trivial fields automatically, without invoking the
        # module.
        assert not inputs
        return getattr(root, self.original_name)

    @property
    @override
    def return_type(self):
        """Return the field's type."""
        return self.type_annotation

    def __str__(self):
        assert self.origin is not None
        return f"{self.origin.__name__}.{self.original_name}"


# Can't use slots because of @cached_property.
@dataclasses.dataclass(kw_only=True)
class FunctionResolver(Resolver, Generic[P, R]):
    """Base class for wrapping user-defined functions."""

    wrapped_func: Func[P, R]

    def __str__(self):
        return repr(self.sig_func)

    @override
    def register(self, typedef: dagger.TypeDef) -> dagger.TypeDef:
        """Add a new object to current module."""
        fn = dag.function(self.name, to_typedef(self.return_type))

        if self.doc:
            fn = fn.with_description(self.doc)

        for param in self.parameters.values():
            fn = fn.with_arg(
                param.name,
                to_typedef(param.resolved_type).with_optional(param.is_optional),
                description=param.doc,
                default_value=self._get_default_value(param),
            )

        return typedef.with_function(fn) if self.name else typedef.with_constructor(fn)

    def _get_default_value(self, param: Parameter) -> dagger.JSON | None:
        if not param.is_optional:
            return None

        default_value = param.signature.default

        try:
            return dagger.JSON(json.dumps(default_value))
        except TypeError as e:
            # Rather than failing on a default value that's not JSON
            # serializable and going through hoops to support more and more
            # types, just don't register it. It'll still be registered
            # as optional so the API server will call the function without
            # it and let Python handle it.
            logger.debug(
                "Not registering default value for %s: %s",
                param.signature,
                e,
            )
            return None

    @property
    def return_type(self):
        """Return the resolved return type of the wrapped function."""
        is_class = inspect.isclass(self.wrapped_func)
        try:
            r: type = self.type_hints["return"]
        except KeyError:
            # When no return type is specified, assume None.
            return self.wrapped_func if is_class else type(None)

        if is_class:
            if self.sig_func.__name__ == "__init__":
                if r is not type(None):
                    msg = (
                        "Expected None return type "
                        f"in __init__ constructor, got {r!r}"
                    )
                    raise UserError(msg)
                return self.wrapped_func

            if r not in (Self, self.wrapped_func):
                msg = (
                    f"Expected `{self.wrapped_func.__name__}` return type "
                    f"in {self.sig_func!r}, got {r!r}"
                )
                raise UserError(msg)
            return self.wrapped_func

        if r is Self:
            if self.origin is None:
                msg = "Can't return Self without parent class"
                raise UserError(msg)
            return self.origin

        return r

    @property
    def func(self):
        """Return the callable to invoke."""
        # It should be the same as `wrapped_func` except for the alternative
        # constructor which is different than `wrapped_func`.
        # It's simpler not to execute `__init__` directly since it's unbound.
        return get_alt_constructor(self.wrapped_func) or self.wrapped_func

    @property
    def sig_func(self):
        """Return the callable to inspect."""
        # For more accurate inspection, as it can be different
        # than the callable to invoke.
        if inspect.isclass(cls := self.wrapped_func):
            return get_alt_constructor(cls) or cls.__init__
        return self.wrapped_func

    @cached_property
    def type_hints(self):
        return get_type_hints(self.sig_func)

    @cached_property
    def signature(self):
        return inspect.signature(self.sig_func, follow_wrapped=True)

    @cached_property
    def parameters(self):
        """Return the parameter annotations of the wrapped function.

        Keys are the Python parameter names.
        """
        is_method = (
            inspect.isclass(self.wrapped_func)
            and self.sig_func.__name__ == "__init__"
            or self.origin
        )
        mapping: dict[PythonName, Parameter] = {}

        for param in self.signature.parameters.values():
            # Skip `self` parameter on instance methods.
            # It will be added manually on `get_result`.
            if is_method and param.name == "self":
                continue

            if param.kind is inspect.Parameter.POSITIONAL_ONLY:
                msg = "Positional-only parameters are not supported"
                raise TypeError(msg)

            try:
                # Use type_hints instead of param.annotation to get
                # resolved forward references and stripped Annotated.
                annotation = self.type_hints[param.name]
            except KeyError:
                logger.warning(
                    "Missing type annotation for parameter '%s'",
                    param.name,
                )
                annotation = Any

            if isinstance(annotation, dataclasses.InitVar):
                annotation = annotation.type

            parameter = Parameter(
                name=get_arg_name(param.annotation) or param.name,
                signature=param,
                resolved_type=annotation,
                doc=get_doc(param.annotation),
            )

            mapping[param.name] = parameter

        return mapping

    @override
    async def get_result(
        self,
        converter: cattrs.Converter,
        root: object | None,
        inputs: Mapping[APIName, Any],
    ) -> Any:
        # NB: `root` is only needed on instance methods (with first `self` argument).
        # Use bound instance method to remove `self` from the list of arguments.
        func = getattr(root, self.original_name) if root else self.func

        signature = (
            self.signature
            if func is self.sig_func
            else inspect.signature(func, follow_wrapped=True)
        )

        logger.debug("func => %s", repr(signature))
        logger.debug("input args => %s", repr(inputs))
        kwargs = await self._convert_inputs(converter, inputs)
        logger.debug("structured args => %s", repr(kwargs))

        try:
            bound = signature.bind(**kwargs)
        except TypeError as e:
            msg = f"Unable to bind arguments: {e}"
            raise UserError(msg) from e

        return await await_maybe(func(*bound.args, **bound.kwargs))

    async def _convert_inputs(
        self,
        converter: cattrs.Converter,
        inputs: Mapping[APIName, Any],
    ):
        """Convert arguments to the expected parameter types."""
        kwargs: dict[PythonName, Any] = {}

        # Convert arguments to the expected type.
        for python_name, param in self.parameters.items():
            if param.name not in inputs:
                if not param.is_optional:
                    msg = f"Missing required argument: {python_name}"
                    raise UserError(msg)
                continue

            value = inputs[param.name]
            type_ = param.resolved_type

            try:
                kwargs[python_name] = await asyncify(converter.structure, value, type_)
            except Exception as e:  # noqa: BLE001
                msg = transform_error(
                    e,
                    f"Invalid argument `{param.name}`",
                    self.sig_func,
                    type_,
                )
                raise UserError(msg) from e

        return kwargs


@dataclasses.dataclass(slots=True)
class Function(Generic[P, R]):
    """Descriptor for wrapping user-defined functions."""

    func: Func[P, R]
    name: APIName | None = None
    doc: str | None = None
    resolver: FunctionResolver = dataclasses.field(init=False)

    def __post_init__(self):
        original_name = self.func.__name__
        name = original_name if self.name is None else self.name
        origin = None

        if inspect.isclass(self.func):
            if self.name is None:
                name = camel_to_snake(name)
            elif self.name == "":
                origin = self.func

        self.resolver = FunctionResolver(
            original_name=original_name,
            name=name,
            wrapped_func=self.func,
            doc=self.doc,
            origin=origin,
        )

    def __set_name__(self, owner: type, name: str):
        if self.name is None:
            self.name = name
            self.resolver.name = name
        self.resolver.origin = owner

    @overload
    def __get__(self, instance: None, owner: None = None) -> Self:
        ...

    @overload
    def __get__(self, instance: object, owner: None = None) -> Func[P, R]:
        ...

    def __get__(self, instance: object | None, owner: None = None) -> Func[P, R] | Self:
        if instance is None:
            return self
        if inspect.isclass(self.func):
            return cast(Func[P, R], self.func)
        return cast(Func[P, R], types.MethodType(self.func, instance))

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        # NB: This is only needed for top-level functions because only
        # class attributes can access descriptors via `__get__`. For
        # the top-level functions, you'll get this `Function` instance
        # instead, so we need to proxy the call to the wrapped function.
        return self.func(*args, **kwargs)
