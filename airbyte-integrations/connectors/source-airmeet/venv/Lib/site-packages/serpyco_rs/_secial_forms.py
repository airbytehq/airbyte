import sys
import types
import typing
from contextlib import suppress
from typing import Annotated, Any, ClassVar, Final, ForwardRef, Union, get_origin

from typing_extensions import NotRequired, ReadOnly, Required, get_args

from ._meta import Annotations


if sys.version_info >= (3, 12):
    from typing import TypeAliasType
else:
    TypeAliasType = None


def unwrap_special_forms(annotation: Any) -> tuple[Any, Annotations]:
    metadata: list[Any] = []

    while True:
        annotation, _meta = _unpack_annotated(annotation)
        if _meta:
            metadata = _meta + metadata
            continue

        if is_typealiastype(annotation):
            # unwrap bare PEP 695 type aliases like ``type Foo = int``
            annotation = annotation.__value__
            continue

        if is_newtype(annotation):
            annotation = annotation.__supertype__
            continue

        if isinstance(annotation, str):
            annotation = ForwardRef(
                annotation,
                # we will use globals from resolver_context
                module=None,
                # allow use of special forms because we don't know current context
                is_class=True,
            )
            continue

        origin = get_origin(annotation)
        if origin is not None:
            if (
                is_classvar(origin)
                or is_final(origin)
                or is_required(origin)
                or is_notrequired(origin)
                or is_readonly(origin)
            ):
                annotation = annotation.__args__[0]
            elif is_typealiastype(origin):
                # unwrap PEP 695 type aliases
                args = get_args(annotation)
                annotation = annotation.__value__

                # apply generics args
                with suppress(TypeError):
                    annotation = annotation[args]
            else:
                # origin is not None but not a type qualifier not `Annotated` (e.g. `list[int]`):
                break
        else:
            break

    return annotation, Annotations(*metadata)


def is_annotated(origin: Any) -> bool:
    return origin is Annotated


def is_typealiastype(annotation: Any) -> bool:
    return TypeAliasType is not None and isinstance(annotation, TypeAliasType)


def is_newtype(annotation: Any) -> bool:
    return hasattr(annotation, '__supertype__') and callable(annotation)


def is_classvar(origin: Any) -> bool:
    return origin is ClassVar


def is_final(origin: Any) -> bool:
    return origin is Final


def is_required(origin: Any) -> bool:
    return origin is Required


def is_notrequired(origin: Any) -> bool:
    return origin is NotRequired


def is_readonly(origin: Any) -> bool:
    return origin is ReadOnly


def is_union_type(origin: Any) -> bool:
    if origin is Union:
        return True
    # Python 3.10+ union syntax (X | Y)
    if sys.version_info >= (3, 10) and origin is types.UnionType:
        return True
    return False


def is_literal_type(annotation: Any) -> bool:
    return annotation is typing.Literal


def _unpack_annotated(annotation: Any) -> tuple[Any, list[Any]]:
    origin = get_origin(annotation)
    if is_annotated(origin):
        annotated_type = annotation.__origin__
        metadata = list(annotation.__metadata__)

        # The annotated type might be a PEP 695 type alias, so we need to recursively unpack it
        annotated_type, sub_meta = _unpack_annotated(annotated_type)
        metadata = sub_meta + metadata
        return annotated_type, metadata
    if is_typealiastype(annotation):
        value = annotation.__value__
        typ, metadata = _unpack_annotated(value)
        if metadata:
            # Having metadata means the type alias' `__value__` was an `Annotated` form
            # (or, recursively, a type alias to an `Annotated` form). It is important to check
            # for this, as we don't want to unpack other type aliases (e.g. `type MyInt = int`).
            return typ, metadata
        return annotation, []
    if is_typealiastype(origin):
        # When parameterized, PEP 695 type aliases become generic aliases
        # (e.g. with `type MyList[T] = Annotated[list[T], ...]`, `MyList[int]`
        # is a generic alias).

        value = origin.__value__

        with suppress(TypeError):
            value = value[annotation.__args__]

        typ, metadata = _unpack_annotated(value)
        if metadata:
            return typ, metadata
        return annotation, []

    return annotation, []
