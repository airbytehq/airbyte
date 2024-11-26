import dataclasses
import functools
import inspect
import logging
import typing
from collections.abc import Sequence

from beartype.door import TypeHint
from cattrs.preconf.json import make_converter as make_json_converter

from ._types import ObjectDefinition
from ._utils import (
    get_doc,
    is_annotated,
    is_optional,
    is_union,
    non_optional,
    strip_annotations,
    syncify,
)

logger = logging.getLogger(__name__)

if typing.TYPE_CHECKING:
    from dagger import TypeDef


def make_converter():
    from dagger import dag
    from dagger.client._core import Arg
    from dagger.client._guards import is_id_type, is_id_type_subclass

    conv = make_json_converter(
        detailed_validation=True,
    )

    def dagger_type_structure(id_, cls):
        """Get dagger object type from id."""
        cls = strip_annotations(cls)

        if not is_id_type_subclass(cls):
            msg = f"Unsupported type '{cls.__name__}'"
            raise TypeError(msg)

        return cls(
            dag._select(f"load{cls.__name__}FromID", [Arg("id", id_)])  # noqa: SLF001
        )

    def dagger_type_unstructure(obj):
        """Get id from dagger object."""
        if not is_id_type(obj):
            msg = f"Expected dagger Type object, got `{type(obj)}`"
            raise TypeError(msg)
        return syncify(obj.id)

    conv.register_structure_hook_func(
        is_id_type_subclass,
        dagger_type_structure,
    )

    conv.register_unstructure_hook_func(
        is_id_type_subclass,
        dagger_type_unstructure,
    )

    return conv


@functools.cache
def to_typedef(annotation: type) -> "TypeDef":  # noqa: C901
    """Convert Python object to API type."""
    assert not is_annotated(
        annotation
    ), "Annotated types should be handled by the caller."

    import dagger
    from dagger import dag
    from dagger.client._guards import is_id_type_subclass

    td = dag.type_def()

    if isinstance(annotation, dataclasses.InitVar):
        annotation = annotation.type

    typ = TypeHint(annotation)

    if is_optional(typ):
        td = td.with_optional(True)

    typ = non_optional(typ)

    if typ is TypeHint(type(None)):
        return td.with_kind(dagger.TypeDefKind.VoidKind)

    builtins = {
        str: dagger.TypeDefKind.StringKind,
        int: dagger.TypeDefKind.IntegerKind,
        bool: dagger.TypeDefKind.BooleanKind,
    }

    if typ.hint in builtins:
        return td.with_kind(builtins[typ.hint])

    # Can't represent unions in the API.
    if is_union(typ):
        msg = f"Unsupported union type: {typ.hint}"
        raise TypeError(msg)

    if typ.is_subhint(TypeHint(Sequence)):
        if len(typ) != 1:
            msg = (
                "Expected sequence type to be subscripted "
                f"with 1 subtype, got {len(typ)}"
            )
            raise TypeError(msg)

        return td.with_list_of(to_typedef(typ.args[0]))

    if inspect.isclass(cls := typ.hint):
        custom_obj: ObjectDefinition | None = getattr(cls, "__dagger_type__", None)

        if custom_obj is not None:
            return td.with_object(
                custom_obj.name,
                description=custom_obj.doc,
            )

        if is_id_type_subclass(cls):
            return td.with_object(cls.__name__)

        return td.with_object(
            cls.__name__,
            description=get_doc(cls),
        )

    msg = f"Unsupported type: {typ.hint!r}"
    raise TypeError(msg)
