from collections import Counter, deque
from collections.abc import MutableSet as AbcMutableSet
from dataclasses import Field
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import (
    Any,
    Callable,
    Deque,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from attrs import Attribute
from attrs import has as attrs_has
from attrs import resolve_types

from ._compat import (
    FrozenSetSubscriptable,
    Mapping,
    MutableMapping,
    MutableSequence,
    OriginAbstractSet,
    OriginMutableSet,
    Sequence,
    Set,
    fields,
    get_final_base,
    get_newtype_base,
    get_origin,
    has,
    has_with_generic,
    is_annotated,
    is_bare,
    is_counter,
    is_deque,
    is_frozenset,
    is_generic,
    is_generic_attrs,
    is_hetero_tuple,
    is_literal,
    is_mapping,
    is_mutable_set,
    is_protocol,
    is_sequence,
    is_tuple,
    is_typeddict,
    is_union_type,
)
from .disambiguators import create_default_dis_func, is_supported_union
from .dispatch import HookFactory, MultiStrategyDispatch, StructureHook, UnstructureHook
from .errors import (
    IterableValidationError,
    IterableValidationNote,
    StructureHandlerNotFoundError,
)
from .fns import identity, raise_error
from .gen import (
    AttributeOverride,
    DictStructureFn,
    HeteroTupleUnstructureFn,
    IterableUnstructureFn,
    MappingStructureFn,
    MappingUnstructureFn,
    make_dict_structure_fn,
    make_dict_unstructure_fn,
    make_hetero_tuple_unstructure_fn,
    make_iterable_unstructure_fn,
    make_mapping_structure_fn,
    make_mapping_unstructure_fn,
)
from .gen.typeddicts import make_dict_structure_fn as make_typeddict_dict_struct_fn
from .gen.typeddicts import make_dict_unstructure_fn as make_typeddict_dict_unstruct_fn

__all__ = ["UnstructureStrategy", "BaseConverter", "Converter", "GenConverter"]

NoneType = type(None)
T = TypeVar("T")
V = TypeVar("V")


class UnstructureStrategy(Enum):
    """`attrs` classes unstructuring strategies."""

    AS_DICT = "asdict"
    AS_TUPLE = "astuple"


def _subclass(typ: Type) -> Callable[[Type], bool]:
    """a shortcut"""
    return lambda cls: issubclass(cls, typ)


def is_optional(typ: Type) -> bool:
    return is_union_type(typ) and NoneType in typ.__args__ and len(typ.__args__) == 2


def is_literal_containing_enums(typ: Type) -> bool:
    return is_literal(typ) and any(isinstance(val, Enum) for val in typ.__args__)


class BaseConverter:
    """Converts between structured and unstructured data."""

    __slots__ = (
        "_dis_func_cache",
        "_unstructure_func",
        "_unstructure_attrs",
        "_structure_attrs",
        "_dict_factory",
        "_union_struct_registry",
        "_structure_func",
        "_prefer_attrib_converters",
        "detailed_validation",
        "_struct_copy_skip",
        "_unstruct_copy_skip",
    )

    def __init__(
        self,
        dict_factory: Callable[[], Any] = dict,
        unstruct_strat: UnstructureStrategy = UnstructureStrategy.AS_DICT,
        prefer_attrib_converters: bool = False,
        detailed_validation: bool = True,
        unstructure_fallback_factory: HookFactory[UnstructureHook] = lambda _: identity,
        structure_fallback_factory: HookFactory[StructureHook] = lambda _: raise_error,
    ) -> None:
        """
        :param detailed_validation: Whether to use a slightly slower mode for detailed
            validation errors.
        :param unstructure_fallback_factory: A hook factory to be called when no
            registered unstructuring hooks match.
        :param structure_fallback_factory: A hook factory to be called when no
            registered structuring hooks match.

        ..  versionadded:: 23.2.0 *unstructure_fallback_factory*
        ..  versionadded:: 23.2.0 *structure_fallback_factory*
        """
        unstruct_strat = UnstructureStrategy(unstruct_strat)
        self._prefer_attrib_converters = prefer_attrib_converters

        self.detailed_validation = detailed_validation

        # Create a per-instance cache.
        if unstruct_strat is UnstructureStrategy.AS_DICT:
            self._unstructure_attrs = self.unstructure_attrs_asdict
            self._structure_attrs = self.structure_attrs_fromdict
        else:
            self._unstructure_attrs = self.unstructure_attrs_astuple
            self._structure_attrs = self.structure_attrs_fromtuple

        self._dis_func_cache = lru_cache()(self._get_dis_func)

        self._unstructure_func = MultiStrategyDispatch(unstructure_fallback_factory)
        self._unstructure_func.register_cls_list(
            [(bytes, identity), (str, identity), (Path, str)]
        )
        self._unstructure_func.register_func_list(
            [
                (
                    is_protocol,
                    lambda o: self.unstructure(o, unstructure_as=o.__class__),
                ),
                (
                    lambda t: get_final_base(t) is not None,
                    lambda t: self._unstructure_func.dispatch(get_final_base(t)),
                    True,
                ),
                (is_mapping, self._unstructure_mapping),
                (is_sequence, self._unstructure_seq),
                (is_mutable_set, self._unstructure_seq),
                (is_frozenset, self._unstructure_seq),
                (_subclass(Enum), self._unstructure_enum),
                (has, self._unstructure_attrs),
                (is_union_type, self._unstructure_union),
            ]
        )

        # Per-instance register of to-attrs converters.
        # Singledispatch dispatches based on the first argument, so we
        # store the function and switch the arguments in self.loads.
        self._structure_func = MultiStrategyDispatch(structure_fallback_factory)
        self._structure_func.register_func_list(
            [
                (lambda cl: cl is Any or cl is Optional or cl is None, lambda v, _: v),
                (is_generic_attrs, self._gen_structure_generic, True),
                (lambda t: get_newtype_base(t) is not None, self._structure_newtype),
                (
                    lambda t: get_final_base(t) is not None,
                    self._structure_final_factory,
                    True,
                ),
                (is_literal, self._structure_simple_literal),
                (is_literal_containing_enums, self._structure_enum_literal),
                (is_sequence, self._structure_list),
                (is_deque, self._structure_deque),
                (is_mutable_set, self._structure_set),
                (is_frozenset, self._structure_frozenset),
                (is_tuple, self._structure_tuple),
                (is_mapping, self._structure_dict),
                (is_supported_union, self._gen_attrs_union_structure, True),
                (
                    lambda t: is_union_type(t) and t in self._union_struct_registry,
                    self._structure_union,
                ),
                (is_optional, self._structure_optional),
                (has, self._structure_attrs),
            ]
        )
        # Strings are sequences.
        self._structure_func.register_cls_list(
            [
                (str, self._structure_call),
                (bytes, self._structure_call),
                (int, self._structure_call),
                (float, self._structure_call),
                (Enum, self._structure_call),
                (Path, self._structure_call),
            ]
        )

        self._dict_factory = dict_factory

        # Unions are instances now, not classes. We use different registries.
        self._union_struct_registry: Dict[Any, Callable[[Any, Type[T]], T]] = {}

        self._unstruct_copy_skip = self._unstructure_func.get_num_fns()
        self._struct_copy_skip = self._structure_func.get_num_fns()

    def unstructure(self, obj: Any, unstructure_as: Any = None) -> Any:
        return self._unstructure_func.dispatch(
            obj.__class__ if unstructure_as is None else unstructure_as
        )(obj)

    @property
    def unstruct_strat(self) -> UnstructureStrategy:
        """The default way of unstructuring ``attrs`` classes."""
        return (
            UnstructureStrategy.AS_DICT
            if self._unstructure_attrs == self.unstructure_attrs_asdict
            else UnstructureStrategy.AS_TUPLE
        )

    def register_unstructure_hook(self, cls: Any, func: UnstructureHook) -> None:
        """Register a class-to-primitive converter function for a class.

        The converter function should take an instance of the class and return
        its Python equivalent.
        """
        if attrs_has(cls):
            resolve_types(cls)
        if is_union_type(cls):
            self._unstructure_func.register_func_list([(lambda t: t == cls, func)])
        elif get_newtype_base(cls) is not None:
            # This is a newtype, so we handle it specially.
            self._unstructure_func.register_func_list([(lambda t: t is cls, func)])
        else:
            self._unstructure_func.register_cls_list([(cls, func)])

    def register_unstructure_hook_func(
        self, check_func: Callable[[Any], bool], func: UnstructureHook
    ) -> None:
        """Register a class-to-primitive converter function for a class, using
        a function to check if it's a match.
        """
        self._unstructure_func.register_func_list([(check_func, func)])

    def register_unstructure_hook_factory(
        self, predicate: Callable[[Any], bool], factory: HookFactory[UnstructureHook]
    ) -> None:
        """
        Register a hook factory for a given predicate.

        :param predicate: A function that, given a type, returns whether the factory
            can produce a hook for that type.
        :param factory: A callable that, given a type, produces an unstructuring
            hook for that type. This unstructuring hook will be cached.
        """
        self._unstructure_func.register_func_list([(predicate, factory, True)])

    def register_structure_hook(self, cl: Any, func: StructureHook) -> None:
        """Register a primitive-to-class converter function for a type.

        The converter function should take two arguments:
          * a Python object to be converted,
          * the type to convert to

        and return the instance of the class. The type may seem redundant, but
        is sometimes needed (for example, when dealing with generic classes).
        """
        if attrs_has(cl):
            resolve_types(cl)
        if is_union_type(cl):
            self._union_struct_registry[cl] = func
            self._structure_func.clear_cache()
        elif get_newtype_base(cl) is not None:
            # This is a newtype, so we handle it specially.
            self._structure_func.register_func_list([(lambda t: t is cl, func)])
        else:
            self._structure_func.register_cls_list([(cl, func)])

    def register_structure_hook_func(
        self, check_func: Callable[[Type[T]], bool], func: StructureHook
    ) -> None:
        """Register a class-to-primitive converter function for a class, using
        a function to check if it's a match.
        """
        self._structure_func.register_func_list([(check_func, func)])

    def register_structure_hook_factory(
        self, predicate: Callable[[Any], bool], factory: HookFactory[StructureHook]
    ) -> None:
        """
        Register a hook factory for a given predicate.

        :param predicate: A function that, given a type, returns whether the factory
            can produce a hook for that type.
        :param factory: A callable that, given a type, produces a structuring
            hook for that type. This structuring hook will be cached.
        """
        self._structure_func.register_func_list([(predicate, factory, True)])

    def structure(self, obj: Any, cl: Type[T]) -> T:
        """Convert unstructured Python data structures to structured data."""
        return self._structure_func.dispatch(cl)(obj, cl)

    # Classes to Python primitives.
    def unstructure_attrs_asdict(self, obj: Any) -> Dict[str, Any]:
        """Our version of `attrs.asdict`, so we can call back to us."""
        attrs = fields(obj.__class__)
        dispatch = self._unstructure_func.dispatch
        rv = self._dict_factory()
        for a in attrs:
            name = a.name
            v = getattr(obj, name)
            rv[name] = dispatch(a.type or v.__class__)(v)
        return rv

    def unstructure_attrs_astuple(self, obj: Any) -> Tuple[Any, ...]:
        """Our version of `attrs.astuple`, so we can call back to us."""
        attrs = fields(obj.__class__)
        dispatch = self._unstructure_func.dispatch
        res = []
        for a in attrs:
            name = a.name
            v = getattr(obj, name)
            res.append(dispatch(a.type or v.__class__)(v))
        return tuple(res)

    def _unstructure_enum(self, obj: Enum) -> Any:
        """Convert an enum to its value."""
        return obj.value

    def _unstructure_seq(self, seq: Sequence[T]) -> Sequence[T]:
        """Convert a sequence to primitive equivalents."""
        # We can reuse the sequence class, so tuples stay tuples.
        dispatch = self._unstructure_func.dispatch
        return seq.__class__(dispatch(e.__class__)(e) for e in seq)

    def _unstructure_mapping(self, mapping: Mapping[T, V]) -> Mapping[T, V]:
        """Convert a mapping of attr classes to primitive equivalents."""

        # We can reuse the mapping class, so dicts stay dicts and OrderedDicts
        # stay OrderedDicts.
        dispatch = self._unstructure_func.dispatch
        return mapping.__class__(
            (dispatch(k.__class__)(k), dispatch(v.__class__)(v))
            for k, v in mapping.items()
        )

    # note: Use UnionType when 3.11 is released as
    # the behaviour of @final is changed. This would
    # affect how we can support UnionType in ._compat.py
    def _unstructure_union(self, obj: Any) -> Any:
        """
        Unstructure an object as a union.

        By default, just unstructures the instance.
        """
        return self._unstructure_func.dispatch(obj.__class__)(obj)

    # Python primitives to classes.

    def _gen_structure_generic(self, cl: Type[T]) -> DictStructureFn[T]:
        """Create and return a hook for structuring generics."""
        return make_dict_structure_fn(
            cl, self, _cattrs_prefer_attrib_converters=self._prefer_attrib_converters
        )

    def _gen_attrs_union_structure(
        self, cl: Any, use_literals: bool = True
    ) -> Callable[[Any, Type[T]], Optional[Type[T]]]:
        """
        Generate a structuring function for a union of attrs classes (and maybe None).

        :param use_literals: Whether to consider literal fields.
        """
        dis_fn = self._get_dis_func(cl, use_literals=use_literals)
        has_none = NoneType in cl.__args__

        if has_none:

            def structure_attrs_union(obj, _) -> cl:
                if obj is None:
                    return None
                return self.structure(obj, dis_fn(obj))

        else:

            def structure_attrs_union(obj, _):
                return self.structure(obj, dis_fn(obj))

        return structure_attrs_union

    @staticmethod
    def _structure_call(obj: Any, cl: Type[T]) -> Any:
        """Just call ``cl`` with the given ``obj``.

        This is just an optimization on the ``_structure_default`` case, when
        we know we can skip the ``if`` s. Use for ``str``, ``bytes``, ``enum``,
        etc.
        """
        return cl(obj)

    @staticmethod
    def _structure_simple_literal(val, type):
        if val not in type.__args__:
            raise Exception(f"{val} not in literal {type}")
        return val

    @staticmethod
    def _structure_enum_literal(val, type):
        vals = {(x.value if isinstance(x, Enum) else x): x for x in type.__args__}
        try:
            return vals[val]
        except KeyError:
            raise Exception(f"{val} not in literal {type}") from None

    def _structure_newtype(self, val, type):
        base = get_newtype_base(type)
        return self._structure_func.dispatch(base)(val, base)

    def _structure_final_factory(self, type):
        base = get_final_base(type)
        res = self._structure_func.dispatch(base)
        if res == self._structure_call:
            # It's not really `structure_call` for Finals (can't call Final())
            return lambda v, _: self._structure_call(v, base)
        return lambda v, _: res(v, base)

    # Attrs classes.

    def structure_attrs_fromtuple(self, obj: Tuple[Any, ...], cl: Type[T]) -> T:
        """Load an attrs class from a sequence (tuple)."""
        conv_obj = []  # A list of converter parameters.
        for a, value in zip(fields(cl), obj):
            # We detect the type by the metadata.
            converted = self._structure_attribute(a, value)
            conv_obj.append(converted)

        return cl(*conv_obj)

    def _structure_attribute(self, a: Union[Attribute, Field], value: Any) -> Any:
        """Handle an individual attrs attribute."""
        type_ = a.type
        attrib_converter = getattr(a, "converter", None)
        if self._prefer_attrib_converters and attrib_converter:
            # A attrib converter is defined on this attribute, and
            # prefer_attrib_converters is set to give these priority over registered
            # structure hooks. So, pass through the raw value, which attrs will flow
            # into the converter
            return value
        if type_ is None:
            # No type metadata.
            return value

        try:
            return self._structure_func.dispatch(type_)(value, type_)
        except StructureHandlerNotFoundError:
            if attrib_converter:
                # Return the original value and fallback to using an attrib converter.
                return value
            raise

    def structure_attrs_fromdict(self, obj: Mapping[str, Any], cl: Type[T]) -> T:
        """Instantiate an attrs class from a mapping (dict)."""
        # For public use.

        conv_obj = {}  # Start with a fresh dict, to ignore extra keys.
        for a in fields(cl):
            try:
                val = obj[a.name]
            except KeyError:
                continue

            # try .alias and .name because this code also supports dataclasses!
            conv_obj[getattr(a, "alias", a.name)] = self._structure_attribute(a, val)

        return cl(**conv_obj)

    def _structure_list(self, obj: Iterable[T], cl: Any) -> List[T]:
        """Convert an iterable to a potentially generic list."""
        if is_bare(cl) or cl.__args__[0] is Any:
            res = list(obj)
        else:
            elem_type = cl.__args__[0]
            handler = self._structure_func.dispatch(elem_type)
            if self.detailed_validation:
                errors = []
                res = []
                ix = 0  # Avoid `enumerate` for performance.
                for e in obj:
                    try:
                        res.append(handler(e, elem_type))
                    except Exception as e:
                        msg = IterableValidationNote(
                            f"Structuring {cl} @ index {ix}", ix, elem_type
                        )
                        e.__notes__ = [*getattr(e, "__notes__", []), msg]
                        errors.append(e)
                    finally:
                        ix += 1
                if errors:
                    raise IterableValidationError(
                        f"While structuring {cl!r}", errors, cl
                    )
            else:
                res = [handler(e, elem_type) for e in obj]
        return res

    def _structure_deque(self, obj: Iterable[T], cl: Any) -> Deque[T]:
        """Convert an iterable to a potentially generic deque."""
        if is_bare(cl) or cl.__args__[0] is Any:
            res = deque(e for e in obj)
        else:
            elem_type = cl.__args__[0]
            handler = self._structure_func.dispatch(elem_type)
            if self.detailed_validation:
                errors = []
                res = deque()
                ix = 0  # Avoid `enumerate` for performance.
                for e in obj:
                    try:
                        res.append(handler(e, elem_type))
                    except Exception as e:
                        msg = IterableValidationNote(
                            f"Structuring {cl} @ index {ix}", ix, elem_type
                        )
                        e.__notes__ = [*getattr(e, "__notes__", []), msg]
                        errors.append(e)
                    finally:
                        ix += 1
                if errors:
                    raise IterableValidationError(
                        f"While structuring {cl!r}", errors, cl
                    )
            else:
                res = deque(handler(e, elem_type) for e in obj)
        return res

    def _structure_set(
        self, obj: Iterable[T], cl: Any, structure_to: type = set
    ) -> Set[T]:
        """Convert an iterable into a potentially generic set."""
        if is_bare(cl) or cl.__args__[0] is Any:
            return structure_to(obj)
        elem_type = cl.__args__[0]
        handler = self._structure_func.dispatch(elem_type)
        if self.detailed_validation:
            errors = []
            res = set()
            ix = 0
            for e in obj:
                try:
                    res.add(handler(e, elem_type))
                except Exception as exc:
                    msg = IterableValidationNote(
                        f"Structuring {structure_to.__name__} @ element {e!r}",
                        ix,
                        elem_type,
                    )
                    exc.__notes__ = [*getattr(exc, "__notes__", []), msg]
                    errors.append(exc)
                finally:
                    ix += 1
            if errors:
                raise IterableValidationError(f"While structuring {cl!r}", errors, cl)
            return res if structure_to is set else structure_to(res)
        if structure_to is set:
            return {handler(e, elem_type) for e in obj}
        return structure_to([handler(e, elem_type) for e in obj])

    def _structure_frozenset(
        self, obj: Iterable[T], cl: Any
    ) -> FrozenSetSubscriptable[T]:
        """Convert an iterable into a potentially generic frozenset."""
        return self._structure_set(obj, cl, structure_to=frozenset)

    def _structure_dict(self, obj: Mapping[T, V], cl: Any) -> Dict[T, V]:
        """Convert a mapping into a potentially generic dict."""
        if is_bare(cl) or cl.__args__ == (Any, Any):
            return dict(obj)
        key_type, val_type = cl.__args__
        if key_type is Any:
            val_conv = self._structure_func.dispatch(val_type)
            return {k: val_conv(v, val_type) for k, v in obj.items()}
        if val_type is Any:
            key_conv = self._structure_func.dispatch(key_type)
            return {key_conv(k, key_type): v for k, v in obj.items()}
        key_conv = self._structure_func.dispatch(key_type)
        val_conv = self._structure_func.dispatch(val_type)
        return {key_conv(k, key_type): val_conv(v, val_type) for k, v in obj.items()}

    def _structure_optional(self, obj, union):
        if obj is None:
            return None
        union_params = union.__args__
        other = union_params[0] if union_params[1] is NoneType else union_params[1]
        # We can't actually have a Union of a Union, so this is safe.
        return self._structure_func.dispatch(other)(obj, other)

    def _structure_union(self, obj, union):
        """Deal with structuring a union."""
        handler = self._union_struct_registry[union]
        return handler(obj, union)

    def _structure_tuple(self, obj: Any, tup: Type[T]) -> T:
        """Deal with structuring into a tuple."""
        tup_params = None if tup in (Tuple, tuple) else tup.__args__
        has_ellipsis = tup_params and tup_params[-1] is Ellipsis
        if tup_params is None or (has_ellipsis and tup_params[0] is Any):
            # Just a Tuple. (No generic information.)
            return tuple(obj)
        if has_ellipsis:
            # We're dealing with a homogenous tuple, Tuple[int, ...]
            tup_type = tup_params[0]
            conv = self._structure_func.dispatch(tup_type)
            if self.detailed_validation:
                errors = []
                res = []
                ix = 0
                for e in obj:
                    try:
                        res.append(conv(e, tup_type))
                    except Exception as exc:
                        msg = IterableValidationNote(
                            f"Structuring {tup} @ index {ix}", ix, tup_type
                        )
                        exc.__notes__ = [*getattr(exc, "__notes__", []), msg]
                        errors.append(exc)
                    finally:
                        ix += 1
                if errors:
                    raise IterableValidationError(
                        f"While structuring {tup!r}", errors, tup
                    )
                return tuple(res)
            return tuple(conv(e, tup_type) for e in obj)

        # We're dealing with a heterogenous tuple.
        exp_len = len(tup_params)
        try:
            len_obj = len(obj)
        except TypeError:
            pass  # most likely an unsized iterator, eg generator
        else:
            if len_obj > exp_len:
                exp_len = len_obj
        if self.detailed_validation:
            errors = []
            res = []
            for ix, (t, e) in enumerate(zip(tup_params, obj)):
                try:
                    conv = self._structure_func.dispatch(t)
                    res.append(conv(e, t))
                except Exception as exc:
                    msg = IterableValidationNote(
                        f"Structuring {tup} @ index {ix}", ix, t
                    )
                    exc.__notes__ = [*getattr(exc, "__notes__", []), msg]
                    errors.append(exc)
            if len(res) < exp_len:
                problem = "Not enough" if len(res) < len(tup_params) else "Too many"
                exc = ValueError(f"{problem} values in {obj!r} to structure as {tup!r}")
                msg = f"Structuring {tup}"
                exc.__notes__ = [*getattr(exc, "__notes__", []), msg]
                errors.append(exc)
            if errors:
                raise IterableValidationError(f"While structuring {tup!r}", errors, tup)
            return tuple(res)

        res = tuple(
            [self._structure_func.dispatch(t)(e, t) for t, e in zip(tup_params, obj)]
        )
        if len(res) < exp_len:
            problem = "Not enough" if len(res) < len(tup_params) else "Too many"
            raise ValueError(f"{problem} values in {obj!r} to structure as {tup!r}")
        return res

    @staticmethod
    def _get_dis_func(union: Any, use_literals: bool = True) -> Callable[[Any], Type]:
        """Fetch or try creating a disambiguation function for a union."""
        union_types = union.__args__
        if NoneType in union_types:  # type: ignore
            # We support unions of attrs classes and NoneType higher in the
            # logic.
            union_types = tuple(
                e for e in union_types if e is not NoneType  # type: ignore
            )

        # TODO: technically both disambiguators could support TypedDicts and
        # dataclasses...
        if not all(has(get_origin(e) or e) for e in union_types):
            raise StructureHandlerNotFoundError(
                "Only unions of attrs classes supported "
                "currently. Register a loads hook manually.",
                type_=union,
            )

        return create_default_dis_func(*union_types, use_literals=use_literals)

    def __deepcopy__(self, _) -> "BaseConverter":
        return self.copy()

    def copy(
        self,
        dict_factory: Optional[Callable[[], Any]] = None,
        unstruct_strat: Optional[UnstructureStrategy] = None,
        prefer_attrib_converters: Optional[bool] = None,
        detailed_validation: Optional[bool] = None,
    ) -> "BaseConverter":
        """Create a copy of the converter, keeping all existing custom hooks.

        :param detailed_validation: Whether to use a slightly slower mode for detailed
            validation errors.
        """
        res = self.__class__(
            dict_factory if dict_factory is not None else self._dict_factory,
            unstruct_strat
            if unstruct_strat is not None
            else (
                UnstructureStrategy.AS_DICT
                if self._unstructure_attrs == self.unstructure_attrs_asdict
                else UnstructureStrategy.AS_TUPLE
            ),
            prefer_attrib_converters
            if prefer_attrib_converters is not None
            else self._prefer_attrib_converters,
            detailed_validation
            if detailed_validation is not None
            else self.detailed_validation,
        )

        self._unstructure_func.copy_to(res._unstructure_func, self._unstruct_copy_skip)
        self._structure_func.copy_to(res._structure_func, self._struct_copy_skip)

        return res


class Converter(BaseConverter):
    """A converter which generates specialized un/structuring functions."""

    __slots__ = (
        "omit_if_default",
        "forbid_extra_keys",
        "type_overrides",
        "_unstruct_collection_overrides",
    )

    def __init__(
        self,
        dict_factory: Callable[[], Any] = dict,
        unstruct_strat: UnstructureStrategy = UnstructureStrategy.AS_DICT,
        omit_if_default: bool = False,
        forbid_extra_keys: bool = False,
        type_overrides: Mapping[Type, AttributeOverride] = {},
        unstruct_collection_overrides: Mapping[Type, Callable] = {},
        prefer_attrib_converters: bool = False,
        detailed_validation: bool = True,
        unstructure_fallback_factory: HookFactory[UnstructureHook] = lambda _: identity,
        structure_fallback_factory: HookFactory[StructureHook] = lambda _: raise_error,
    ):
        """
        :param detailed_validation: Whether to use a slightly slower mode for detailed
            validation errors.
        :param unstructure_fallback_factory: A hook factory to be called when no
            registered unstructuring hooks match.
        :param structure_fallback_factory: A hook factory to be called when no
            registered structuring hooks match.

        ..  versionadded:: 23.2.0 *unstructure_fallback_factory*
        ..  versionadded:: 23.2.0 *structure_fallback_factory*
        """
        super().__init__(
            dict_factory=dict_factory,
            unstruct_strat=unstruct_strat,
            prefer_attrib_converters=prefer_attrib_converters,
            detailed_validation=detailed_validation,
            unstructure_fallback_factory=unstructure_fallback_factory,
            structure_fallback_factory=structure_fallback_factory,
        )
        self.omit_if_default = omit_if_default
        self.forbid_extra_keys = forbid_extra_keys
        self.type_overrides = dict(type_overrides)

        unstruct_collection_overrides = {
            get_origin(k) or k: v for k, v in unstruct_collection_overrides.items()
        }

        self._unstruct_collection_overrides = unstruct_collection_overrides

        # Do a little post-processing magic to make things easier for users.
        co = unstruct_collection_overrides

        # abc.Set overrides, if defined, apply to abc.MutableSets and sets
        if OriginAbstractSet in co:
            if OriginMutableSet not in co:
                co[OriginMutableSet] = co[OriginAbstractSet]
                co[AbcMutableSet] = co[OriginAbstractSet]  # For 3.8 compatibility.
            if FrozenSetSubscriptable not in co:
                co[FrozenSetSubscriptable] = co[OriginAbstractSet]

        # abc.MutableSet overrrides, if defined, apply to sets
        if OriginMutableSet in co and set not in co:
            co[set] = co[OriginMutableSet]

        if FrozenSetSubscriptable in co:
            co[frozenset] = co[FrozenSetSubscriptable]  # For 3.8 compatibility.

        # abc.Sequence overrides, if defined, can apply to MutableSequences, lists and
        # tuples
        if Sequence in co:
            if MutableSequence not in co:
                co[MutableSequence] = co[Sequence]
            if tuple not in co:
                co[tuple] = co[Sequence]

        # abc.MutableSequence overrides, if defined, can apply to lists
        if MutableSequence in co:
            if list not in co:
                co[list] = co[MutableSequence]
            if deque not in co:
                co[deque] = co[MutableSequence]

        # abc.Mapping overrides, if defined, can apply to MutableMappings
        if Mapping in co and MutableMapping not in co:
            co[MutableMapping] = co[Mapping]

        # abc.MutableMapping overrides, if defined, can apply to dicts
        if MutableMapping in co and dict not in co:
            co[dict] = co[MutableMapping]

        # builtins.dict overrides, if defined, can apply to counters
        if dict in co and Counter not in co:
            co[Counter] = co[dict]

        if unstruct_strat is UnstructureStrategy.AS_DICT:
            # Override the attrs handler.
            self.register_unstructure_hook_factory(
                has_with_generic, self.gen_unstructure_attrs_fromdict
            )
            self.register_structure_hook_factory(
                has_with_generic, self.gen_structure_attrs_fromdict
            )
        self.register_unstructure_hook_factory(
            is_annotated, self.gen_unstructure_annotated
        )
        self.register_unstructure_hook_factory(
            is_hetero_tuple, self.gen_unstructure_hetero_tuple
        )
        self.register_unstructure_hook_factory(
            is_sequence, self.gen_unstructure_iterable
        )
        self.register_unstructure_hook_factory(is_mapping, self.gen_unstructure_mapping)
        self.register_unstructure_hook_factory(
            is_mutable_set,
            lambda cl: self.gen_unstructure_iterable(cl, unstructure_to=set),
        )
        self.register_unstructure_hook_factory(
            is_frozenset,
            lambda cl: self.gen_unstructure_iterable(cl, unstructure_to=frozenset),
        )
        self.register_unstructure_hook_factory(
            is_optional, self.gen_unstructure_optional
        )
        self.register_unstructure_hook_factory(
            is_typeddict, self.gen_unstructure_typeddict
        )
        self.register_unstructure_hook_factory(
            lambda t: get_newtype_base(t) is not None,
            lambda t: self._unstructure_func.dispatch(get_newtype_base(t)),
        )

        self.register_structure_hook_factory(is_annotated, self.gen_structure_annotated)
        self.register_structure_hook_factory(is_mapping, self.gen_structure_mapping)
        self.register_structure_hook_factory(is_counter, self.gen_structure_counter)
        self.register_structure_hook_factory(is_typeddict, self.gen_structure_typeddict)
        self.register_structure_hook_factory(
            lambda t: get_newtype_base(t) is not None, self.get_structure_newtype
        )

        # We keep these so we can more correctly copy the hooks.
        self._struct_copy_skip = self._structure_func.get_num_fns()
        self._unstruct_copy_skip = self._unstructure_func.get_num_fns()

    def get_structure_newtype(self, type: Type[T]) -> Callable[[Any, Any], T]:
        base = get_newtype_base(type)
        handler = self._structure_func.dispatch(base)
        return lambda v, _: handler(v, base)

    def gen_unstructure_annotated(self, type):
        origin = type.__origin__
        return self._unstructure_func.dispatch(origin)

    def gen_structure_annotated(self, type) -> Callable:
        """A hook factory for annotated types."""
        origin = type.__origin__
        hook = self._structure_func.dispatch(origin)
        return lambda v, _: hook(v, origin)

    def gen_unstructure_typeddict(self, cl: Any) -> Callable[[Dict], Dict]:
        """Generate a TypedDict unstructure function.

        Also apply converter-scored modifications.
        """
        return make_typeddict_dict_unstruct_fn(cl, self)

    def gen_unstructure_attrs_fromdict(
        self, cl: Type[T]
    ) -> Callable[[T], Dict[str, Any]]:
        origin = get_origin(cl)
        attribs = fields(origin or cl)
        if attrs_has(cl) and any(isinstance(a.type, str) for a in attribs):
            # PEP 563 annotations - need to be resolved.
            resolve_types(cl)
        attrib_overrides = {
            a.name: self.type_overrides[a.type]
            for a in attribs
            if a.type in self.type_overrides
        }

        return make_dict_unstructure_fn(
            cl, self, _cattrs_omit_if_default=self.omit_if_default, **attrib_overrides
        )

    def gen_unstructure_optional(self, cl: Type[T]) -> Callable[[T], Any]:
        """Generate an unstructuring hook for optional types."""
        union_params = cl.__args__
        other = union_params[0] if union_params[1] is NoneType else union_params[1]

        # TODO: Remove this special case when we make unstructuring Any consistent.
        if other is Any or isinstance(other, TypeVar):
            handler = self.unstructure
        else:
            handler = self._unstructure_func.dispatch(other)

        def unstructure_optional(val, _handler=handler):
            return None if val is None else _handler(val)

        return unstructure_optional

    def gen_structure_typeddict(self, cl: Any) -> Callable[[Dict], Dict]:
        """Generate a TypedDict structure function.

        Also apply converter-scored modifications.
        """
        return make_typeddict_dict_struct_fn(
            cl, self, _cattrs_detailed_validation=self.detailed_validation
        )

    def gen_structure_attrs_fromdict(
        self, cl: Type[T]
    ) -> Callable[[Mapping[str, Any], Any], T]:
        attribs = fields(get_origin(cl) or cl if is_generic(cl) else cl)
        if attrs_has(cl) and any(isinstance(a.type, str) for a in attribs):
            # PEP 563 annotations - need to be resolved.
            resolve_types(cl)
        attrib_overrides = {
            a.name: self.type_overrides[a.type]
            for a in attribs
            if a.type in self.type_overrides
        }
        return make_dict_structure_fn(
            cl,
            self,
            _cattrs_forbid_extra_keys=self.forbid_extra_keys,
            _cattrs_prefer_attrib_converters=self._prefer_attrib_converters,
            _cattrs_detailed_validation=self.detailed_validation,
            **attrib_overrides,
        )

    def gen_unstructure_iterable(
        self, cl: Any, unstructure_to: Any = None
    ) -> IterableUnstructureFn:
        unstructure_to = self._unstruct_collection_overrides.get(
            get_origin(cl) or cl, unstructure_to or list
        )
        h = make_iterable_unstructure_fn(cl, self, unstructure_to=unstructure_to)
        self._unstructure_func.register_cls_list([(cl, h)], direct=True)
        return h

    def gen_unstructure_hetero_tuple(
        self, cl: Any, unstructure_to: Any = None
    ) -> HeteroTupleUnstructureFn:
        unstructure_to = self._unstruct_collection_overrides.get(
            get_origin(cl) or cl, unstructure_to or list
        )
        h = make_hetero_tuple_unstructure_fn(cl, self, unstructure_to=unstructure_to)
        self._unstructure_func.register_cls_list([(cl, h)], direct=True)
        return h

    def gen_unstructure_mapping(
        self,
        cl: Any,
        unstructure_to: Any = None,
        key_handler: Optional[Callable[[Any, Optional[Any]], Any]] = None,
    ) -> MappingUnstructureFn:
        unstructure_to = self._unstruct_collection_overrides.get(
            get_origin(cl) or cl, unstructure_to or dict
        )
        h = make_mapping_unstructure_fn(
            cl, self, unstructure_to=unstructure_to, key_handler=key_handler
        )
        self._unstructure_func.register_cls_list([(cl, h)], direct=True)
        return h

    def gen_structure_counter(self, cl: Any) -> MappingStructureFn[T]:
        h = make_mapping_structure_fn(
            cl,
            self,
            structure_to=Counter,
            val_type=int,
            detailed_validation=self.detailed_validation,
        )
        self._structure_func.register_cls_list([(cl, h)], direct=True)
        return h

    def gen_structure_mapping(self, cl: Any) -> MappingStructureFn[T]:
        h = make_mapping_structure_fn(
            cl, self, detailed_validation=self.detailed_validation
        )
        self._structure_func.register_cls_list([(cl, h)], direct=True)
        return h

    def copy(
        self,
        dict_factory: Optional[Callable[[], Any]] = None,
        unstruct_strat: Optional[UnstructureStrategy] = None,
        omit_if_default: Optional[bool] = None,
        forbid_extra_keys: Optional[bool] = None,
        type_overrides: Optional[Mapping[Type, AttributeOverride]] = None,
        unstruct_collection_overrides: Optional[Mapping[Type, Callable]] = None,
        prefer_attrib_converters: Optional[bool] = None,
        detailed_validation: Optional[bool] = None,
    ) -> "Converter":
        """Create a copy of the converter, keeping all existing custom hooks.

        :param detailed_validation: Whether to use a slightly slower mode for detailed
            validation errors.
        """
        res = self.__class__(
            dict_factory if dict_factory is not None else self._dict_factory,
            unstruct_strat
            if unstruct_strat is not None
            else (
                UnstructureStrategy.AS_DICT
                if self._unstructure_attrs == self.unstructure_attrs_asdict
                else UnstructureStrategy.AS_TUPLE
            ),
            omit_if_default if omit_if_default is not None else self.omit_if_default,
            forbid_extra_keys
            if forbid_extra_keys is not None
            else self.forbid_extra_keys,
            type_overrides if type_overrides is not None else self.type_overrides,
            unstruct_collection_overrides
            if unstruct_collection_overrides is not None
            else self._unstruct_collection_overrides,
            prefer_attrib_converters
            if prefer_attrib_converters is not None
            else self._prefer_attrib_converters,
            detailed_validation
            if detailed_validation is not None
            else self.detailed_validation,
        )

        self._unstructure_func.copy_to(
            res._unstructure_func, skip=self._unstruct_copy_skip
        )
        self._structure_func.copy_to(res._structure_func, skip=self._struct_copy_skip)

        return res


GenConverter = Converter
