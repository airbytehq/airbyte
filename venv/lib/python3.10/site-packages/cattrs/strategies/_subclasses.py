"""Strategies for customizing subclass behaviors."""
from gc import collect
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union

from ..converters import BaseConverter, Converter
from ..gen import AttributeOverride, make_dict_structure_fn, make_dict_unstructure_fn
from ..gen._consts import already_generating


def _make_subclasses_tree(cl: Type) -> List[Type]:
    return [cl] + [
        sscl for scl in cl.__subclasses__() for sscl in _make_subclasses_tree(scl)
    ]


def _has_subclasses(cl: Type, given_subclasses: Tuple[Type, ...]) -> bool:
    """Whether the given class has subclasses from `given_subclasses`."""
    actual = set(cl.__subclasses__())
    given = set(given_subclasses)
    return bool(actual & given)


def _get_union_type(cl: Type, given_subclasses_tree: Tuple[Type]) -> Optional[Type]:
    actual_subclass_tree = tuple(_make_subclasses_tree(cl))
    class_tree = tuple(set(actual_subclass_tree) & set(given_subclasses_tree))
    return Union[class_tree] if len(class_tree) >= 2 else None


def include_subclasses(
    cl: Type,
    converter: Converter,
    subclasses: Optional[Tuple[Type, ...]] = None,
    union_strategy: Optional[Callable[[Any, BaseConverter], Any]] = None,
    overrides: Optional[Dict[str, AttributeOverride]] = None,
) -> None:
    """
    Configure the converter so that the attrs/dataclass `cl` is un/structured as if it
    was a union of itself and all its subclasses that are defined at the time when this
    strategy is applied.

    :param cl: A base `attrs` or `dataclass` class.
    :param converter: The `Converter` on which this strategy is applied. Do note that
        the strategy does not work for a :class:`cattrs.BaseConverter`.
    :param subclasses: A tuple of sublcasses whose ancestor is `cl`. If left as `None`,
        subclasses are detected using recursively the `__subclasses__` method of `cl`
        and its descendents.
    :param union_strategy: A callable of two arguments passed by position
        (`subclass_union`, `converter`) that defines the union strategy to use to
        disambiguate the subclasses union. If `None` (the default), the automatic unique
        field disambiguation is used which means that every single subclass
        participating in the union must have an attribute name that does not exist in
        any other sibling class.
    :param overrides: a mapping of `cl` attribute names to overrides (instantiated with
        :func:`cattrs.gen.override`) to customize un/structuring.

    .. versionadded:: 23.1.0
    """
    # Due to https://github.com/python-attrs/attrs/issues/1047
    collect()
    if subclasses is not None:
        parent_subclass_tree = (cl, *subclasses)
    else:
        parent_subclass_tree = tuple(_make_subclasses_tree(cl))

    if overrides is None:
        overrides = {}

    if union_strategy is None:
        _include_subclasses_without_union_strategy(
            cl, converter, parent_subclass_tree, overrides
        )
    else:
        _include_subclasses_with_union_strategy(
            converter, parent_subclass_tree, union_strategy, overrides
        )


def _include_subclasses_without_union_strategy(
    cl,
    converter: Converter,
    parent_subclass_tree: Tuple[Type],
    overrides: Dict[str, AttributeOverride],
):
    # The iteration approach is required if subclasses are more than one level deep:
    for cl in parent_subclass_tree:
        # We re-create a reduced union type to handle the following case:
        #
        #     converter.structure(d, as=Child)
        #
        # In the above, the `as=Child` argument will be transformed to a union type of
        # itself and its subtypes, that way we guarantee that the returned object will
        # not be the parent.
        subclass_union = _get_union_type(cl, parent_subclass_tree)

        def cls_is_cl(cls, _cl=cl):
            return cls is _cl

        base_struct_hook = make_dict_structure_fn(cl, converter, **overrides)
        base_unstruct_hook = make_dict_unstructure_fn(cl, converter, **overrides)

        if subclass_union is None:

            def struct_hook(val: dict, _, _cl=cl, _base_hook=base_struct_hook) -> cl:
                return _base_hook(val, _cl)

        else:
            dis_fn = converter._get_dis_func(subclass_union)

            def struct_hook(
                val: dict,
                _,
                _c=converter,
                _cl=cl,
                _base_hook=base_struct_hook,
                _dis_fn=dis_fn,
            ) -> cl:
                """
                If val is disambiguated to the class `cl`, use its base hook.

                If val is disambiguated to a subclass, dispatch on its exact runtime
                type.
                """
                dis_cl = _dis_fn(val)
                if dis_cl is _cl:
                    return _base_hook(val, _cl)
                return _c.structure(val, dis_cl)

        def unstruct_hook(
            val: parent_subclass_tree[0],
            _c=converter,
            _cl=cl,
            _base_hook=base_unstruct_hook,
        ) -> Dict:
            """
            If val is an instance of the class `cl`, use the hook.

            If val is an instance of a subclass, dispatch on its exact runtime type.
            """
            if val.__class__ is _cl:
                return _base_hook(val)
            return _c.unstructure(val, unstructure_as=val.__class__)

        # This needs to use function dispatch, using singledispatch will again
        # match A and all subclasses, which is not what we want.
        converter.register_structure_hook_func(cls_is_cl, struct_hook)
        converter.register_unstructure_hook_func(cls_is_cl, unstruct_hook)


def _include_subclasses_with_union_strategy(
    converter: Converter,
    union_classes: Tuple[Type, ...],
    union_strategy: Callable[[Any, BaseConverter], Any],
    overrides: Dict[str, AttributeOverride],
):
    """
    This function is tricky because we're dealing with what is essentially a circular
    reference.

    We need to generate a structure hook for a class that is both:
    * specific for that particular class and its own fields
    * but should handle specific functions for all its descendants too

    Hence the dance with registering below.
    """

    parent_classes = [cl for cl in union_classes if _has_subclasses(cl, union_classes)]
    if not parent_classes:
        return

    original_unstruct_hooks = {}
    original_struct_hooks = {}
    for cl in union_classes:
        # In the first pass, every class gets its own unstructure function according to
        # the overrides.
        # We just generate the hooks, and do not register them. This allows us to
        # manipulate the _already_generating set to force runtime dispatch.
        already_generating.working_set = set(union_classes) - {cl}
        try:
            unstruct_hook = make_dict_unstructure_fn(cl, converter, **overrides)
            struct_hook = make_dict_structure_fn(cl, converter, **overrides)
        finally:
            already_generating.working_set = set()
        original_unstruct_hooks[cl] = unstruct_hook
        original_struct_hooks[cl] = struct_hook

    # Now that's done, we can register all the hooks and generate the
    # union handler. The union handler needs them.
    final_union = Union[union_classes]  # type: ignore

    for cl, hook in original_unstruct_hooks.items():

        def cls_is_cl(cls, _cl=cl):
            return cls is _cl

        converter.register_unstructure_hook_func(cls_is_cl, hook)

    for cl, hook in original_struct_hooks.items():

        def cls_is_cl(cls, _cl=cl):
            return cls is _cl

        converter.register_structure_hook_func(cls_is_cl, hook)

    union_strategy(final_union, converter)
    unstruct_hook = converter._unstructure_func.dispatch(final_union)
    struct_hook = converter._structure_func.dispatch(final_union)

    for cl in union_classes:
        # In the second pass, we overwrite the hooks with the union hook.

        def cls_is_cl(cls, _cl=cl):
            return cls is _cl

        converter.register_unstructure_hook_func(cls_is_cl, unstruct_hook)
        subclasses = tuple([c for c in union_classes if issubclass(c, cl)])
        if len(subclasses) > 1:
            u = Union[subclasses]  # type: ignore
            union_strategy(u, converter)
            struct_hook = converter._structure_func.dispatch(u)

            def sh(payload: dict, _, _u=u, _s=struct_hook) -> cl:
                return _s(payload, _u)

            converter.register_structure_hook_func(cls_is_cl, sh)
