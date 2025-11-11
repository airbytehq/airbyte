# Uses code from https://github.com/python/cpython/pull/111515
# type: ignore
import collections.abc
import functools
import operator
import sys
import types
from collections import defaultdict
from types import GenericAlias
from typing import (
    Any,
    ForwardRef,
    Generic,
    TypeVar,
    Union,
    _AnnotatedAlias,
    _eval_type,
    _GenericAlias,
    _type_check,
    get_args,
    get_origin,
)

from typing_extensions import NotRequired, ParamSpec, Required, TypeVarTuple, is_typeddict


_allowed_types = (
    types.FunctionType,
    types.BuiltinFunctionType,
    types.MethodType,
    types.ModuleType,
    types.WrapperDescriptorType,
    types.MethodWrapperType,
    types.MethodDescriptorType,
)


def get_type_hints(
    obj: Any,
    globalns: Union[dict[str, Any], None] = None,
    localns: Union[dict[str, Any], None] = None,
    include_extras: bool = False,
) -> dict[str, Any]:
    """Return type hints for an object.

    This is often the same as obj.__annotations__, but it handles
    forward references encoded as string literals, recursively replaces all
    'Annotated[T, ...]' with 'T' (unless 'include_extras=True'), and resolves
    type variables to their values as needed.

    The argument may be a module, class, generic alias, method, or function.
    The annotations are returned as a dictionary. For classes and generic aliases,
    annotations also include inherited members.

    TypeError is raised if the argument is not of a type that can contain
    annotations, and an empty dictionary is returned if no annotations are
    present.

    BEWARE -- the behavior of globalns and localns is counterintuitive
    (unless you are familiar with how eval() and exec() work).  The
    search order is locals first, then globals.

    - If no dict arguments are passed, an attempt is made to use the
      globals from obj (or the respective module's globals for classes),
      and these are also used as the locals.  If the object does not appear
      to have globals, an empty dictionary is used.  For classes, the search
      order is globals first then locals.

    - If one dict argument is passed, it is used for both globals and
      locals.

    - If two dict arguments are passed, they specify globals and
      locals, respectively.
    """
    if getattr(obj, '__no_type_check__', None):
        return {}

    # for Generic Aliases we need to inspect the origin
    # then apply its args later
    ga_args = None
    if isinstance(obj, (_GenericAlias, GenericAlias)):
        ga_args = get_args(obj)
        obj = get_origin(obj)

    # Classes require a special treatment.
    if isinstance(obj, type):
        # track typevars of each base
        param_tracking = defaultdict(list)
        # track type hints of each base
        hint_tracking = {}
        hints = {}
        # typeddicts cannot redefine pre-existing keys
        can_override = not is_typeddict(obj)
        for base in _get_all_bases(obj):
            # keep track of typevars and the values they are being
            # replaced with
            for cls, args in _track_parameter_changes(base):
                param_tracking[cls].append(args)

                if cls is not base:
                    # if we previously scanned it and it found no type hints
                    # then skip processing it
                    if not hint_tracking[cls]:
                        continue

                    to_sub = _substitute_type_hints(param_tracking[cls], hint_tracking[cls])
                    hints.update(to_sub)

            if globalns is None:
                base_globals = getattr(sys.modules.get(base.__module__, None), '__dict__', {})
            else:
                base_globals = globalns
            ann = base.__dict__.get('__annotations__', {})
            if isinstance(ann, types.GetSetDescriptorType):
                ann = {}
            base_locals = dict(vars(base)) if localns is None else localns
            if localns is None and globalns is None:
                # This is surprising, but required.  Before Python 3.10,
                # get_type_hints only evaluated the globalns of
                # a class.  To maintain backwards compatibility, we reverse
                # the globalns and localns order so that eval() looks into
                # *base_globals* first rather than *base_locals*.
                # This only affects ForwardRefs.
                base_globals, base_locals = base_locals, base_globals

            hint_tracking[base] = {}
            for name, value in ann.items():
                # skip pre-existing keys for typeddict
                if not can_override and name in hints:
                    continue

                if value is None:
                    value = type(None)
                if isinstance(value, str):
                    value = ForwardRef(value, is_argument=False, is_class=True)
                value = _eval_type(value, base_globals, base_locals)
                hint_tracking[base][name] = value
                hints[name] = value

        # sub the original args back in
        if ga_args is not None:
            param_tracking[obj].append(ga_args)
            # Build full mapping for Python 3.12+ TypeVar compatibility
            full_mapping = _build_full_typevar_mapping(param_tracking, ga_args)
            to_sub = _substitute_type_hints(param_tracking[obj], hints, full_mapping)
            hints.update(to_sub)

        return hints if include_extras else {k: _strip_annotations(t) for k, t in hints.items()}

    if globalns is None:
        if isinstance(obj, types.ModuleType):
            globalns = obj.__dict__
        else:
            nsobj = obj
            # Find globalns for the unwrapped object.
            while hasattr(nsobj, '__wrapped__'):
                nsobj = nsobj.__wrapped__
            globalns = getattr(nsobj, '__globals__', {})
        if localns is None:
            localns = globalns
    elif localns is None:
        localns = globalns
    hints = getattr(obj, '__annotations__', None)
    if hints is None:
        # Return empty annotations for something that _could_ have them.
        if isinstance(obj, _allowed_types):
            return {}
        else:  # noqa: RET505
            raise TypeError(f'{obj!r} is not a module, class, method, or function.')
    hints = dict(hints)
    for name, value in hints.items():
        if value is None:
            value = type(None)
        if isinstance(value, str):
            # class-level forward refs were handled above, this must be either
            # a module-level annotation or a function argument annotation
            value = ForwardRef(
                value,
                is_argument=not isinstance(obj, types.ModuleType),
                is_class=False,
            )
        hints[name] = _eval_type(value, globalns, localns)
    return hints if include_extras else {k: _strip_annotations(t) for k, t in hints.items()}


def _build_full_typevar_mapping(
    param_tracking: 'dict[Any, list[tuple[Any, ...]]]', final_substitution: 'tuple[Any, ...]'
) -> 'dict[Any, Any]':
    """Build a complete mapping of all related TypeVars in the inheritance chain.

    In Python 3.12+, each class creates its own TypeVar instances even with the same name.
    This function traces the TypeVar substitutions through the entire inheritance chain
    to build a complete mapping from all TypeVars to their final values.
    """
    if not final_substitution:
        return {}

    # Build a complete mapping by tracing substitutions through the chain
    full_mapping = {}

    # Process classes in reverse MRO order to build substitution chain
    classes_in_order = list(param_tracking.keys())

    # Start with the final class and work backwards
    if classes_in_order and param_tracking[classes_in_order[0]]:
        # Map final class params to their values
        final_params = param_tracking[classes_in_order[0]][0]  # TypeVars of final class
        for i, param in enumerate(final_params):
            if i < len(final_substitution) and _is_typevar_like(param):
                full_mapping[param] = final_substitution[i]

    # Now process all substitution pairs to build transitive mappings
    for substitution_list in param_tracking.values():
        for i in range(len(substitution_list) - 1):
            from_params = substitution_list[i]  # Source TypeVars
            to_params = substitution_list[i + 1]  # Target values/TypeVars

            # Build mapping from source to target
            for j, from_param in enumerate(from_params):
                if j < len(to_params) and _is_typevar_like(from_param):
                    target = to_params[j]

                    # If target is already mapped to a final value, use that
                    if _is_typevar_like(target) and target in full_mapping:
                        full_mapping[from_param] = full_mapping[target]
                    # If target is not a TypeVar, it's a direct value
                    elif not _is_typevar_like(target):
                        full_mapping[from_param] = target
                    # Otherwise, map TypeVar to TypeVar for later resolution
                    else:
                        full_mapping[from_param] = target

    # Resolve any remaining TypeVar-to-TypeVar mappings
    changed = True
    max_iterations = 10  # Prevent infinite loops
    iterations = 0

    while changed and iterations < max_iterations:
        changed = False
        iterations += 1

        for typevar, value in list(full_mapping.items()):
            if _is_typevar_like(value) and value in full_mapping:
                # Replace TypeVar with its mapped value
                new_value = full_mapping[value]
                if new_value != value:
                    full_mapping[typevar] = new_value
                    changed = True

    return full_mapping


def _substitute_type_hints(
    substitutions: 'list[tuple[Any, ...]]', hints: 'dict[str, Any]', full_mapping: 'dict[Any, Any] | None' = None
):
    # nothing to substitute
    if len(substitutions) < 2:
        return {}

    previous_params = substitutions[-2]
    new_params = substitutions[-1]
    new_substitutions = _repack_args(previous_params, new_params)

    # get a mapping of typevar to value
    mapping = {}
    for i in range(len(previous_params)):
        current = previous_params[i]
        # if the previous parameter is *Ts
        # make it {Ts: new Ts or value}
        if _is_unpacked_typevartuple(current):
            (previous_typevartuple,) = get_args(current)
            new_value = new_substitutions[i]

            if _is_unpacked_typevartuple(new_value):
                (new_value,) = get_args(new_value)

            mapping[previous_typevartuple] = new_value
        else:
            mapping[current] = new_substitutions[i]

    # If we have a full_mapping, extend the current mapping with it
    if full_mapping:
        # Add all mappings from full_mapping that are not already in mapping
        for k, v in full_mapping.items():
            if k not in mapping:
                mapping[k] = v

    hints_to_replace = {}

    for name, value in hints.items():
        origin = get_origin(value)
        # if the typevar is nested, we must substitute the typevar all the way down.
        if origin is not None:
            new_args = tuple(_make_substitution(origin, get_args(value), mapping))
            sub = _copy_with(value, new_args)
        elif _is_typevar_like(value):
            # https://github.com/python/cpython/pull/111515#issuecomment-2018336687
            # sub = mapping[value]  # old
            sub = mapping.get(value, value)
        else:
            continue

        hints_to_replace[name] = sub

    return hints_to_replace


def _copy_with(t, new_args):
    if new_args == t.__args__:
        return t
    if isinstance(t, GenericAlias):
        return GenericAlias(t.__origin__, new_args)
    if isinstance(t, _AnnotatedAlias):  # https://github.com/python/cpython/pull/111515#issuecomment-2018132920
        return t.copy_with(new_args[:1])
    if hasattr(types, 'UnionType') and isinstance(t, types.UnionType):
        return functools.reduce(operator.or_, new_args)
    else:  # noqa: RET505
        return t.copy_with(new_args)


def _make_substitution(origin, args, new_arg_by_param):
    """Create a list of new type arguments."""
    new_args = []
    for old_arg in args:
        if isinstance(old_arg, type):
            new_args.append(old_arg)
            continue

        substfunc = getattr(old_arg, '__typing_subst__', None)
        if substfunc:
            new_arg = substfunc(new_arg_by_param[old_arg])
        elif isinstance(old_arg, TypeVar) and sys.version_info[:2] <= (3, 10):
            new_arg = _typevar_subst(new_arg_by_param[old_arg])
        else:
            subparams = getattr(old_arg, '__parameters__', ())
            if not subparams:
                new_arg = old_arg
            else:
                subargs = []
                for x in subparams:
                    if isinstance(x, TypeVarTuple):
                        subargs.extend(new_arg_by_param[x])
                    else:
                        subargs.append(new_arg_by_param[x])
                new_arg = old_arg[tuple(subargs)]

        if origin == collections.abc.Callable and isinstance(new_arg, tuple):
            # Consider the following `Callable`.
            #   C = Callable[[int], str]
            # Here, `C.__args__` should be (int, str) - NOT ([int], str).
            # That means that if we had something like...
            #   P = ParamSpec('P')
            #   T = TypeVar('T')
            #   C = Callable[P, T]
            #   D = C[[int, str], float]
            # ...we need to be careful; `new_args` should end up as
            # `(int, str, float)` rather than `([int, str], float)`.
            new_args.extend(new_arg)
        elif _is_unpacked_typevartuple(old_arg):
            # Consider the following `_GenericAlias`, `B`:
            #   class A(Generic[*Ts]): ...
            #   B = A[T, *Ts]
            # If we then do:
            #   B[float, int, str]
            # The `new_arg` corresponding to `T` will be `float`, and the
            # `new_arg` corresponding to `*Ts` will be `(int, str)`. We
            # should join all these types together in a flat list
            # `(float, int, str)` - so again, we should `extend`.
            new_args.extend(new_arg)
        elif isinstance(old_arg, tuple):
            # Corner case:
            #    P = ParamSpec('P')
            #    T = TypeVar('T')
            #    class Base(Generic[P]): ...
            # Can be substituted like this:
            #    X = Base[[int, T]]
            # In this case, `old_arg` will be a tuple:
            new_args.append(
                tuple(_make_substitution(origin, old_arg, new_arg_by_param)),
            )
        else:
            new_args.append(new_arg)
    return new_args


def _repack_args(reference, params):
    """transforms params to match the requested arguments
    of reference.

    >>> _repack_args((T, U, *Ts), (int, str, float, bool))
    (int, str, (float, bool))
    >>> _repack_args((T, U, *Ts), (int, str, *Ts))
    (int, str, *Ts)
    """

    # find bounds of potential typevar tuple
    tuple_start, tuple_end = 0, None
    found_typvartuple = False
    for i, tv in enumerate(reference):
        if _is_unpacked_typevartuple(tv) or isinstance(tv, TypeVarTuple):
            tuple_start = i
            found_typvartuple = True
        elif found_typvartuple:
            tuple_end = i
            break

    if found_typvartuple:
        # if typevartuple doesnt consume rest
        if tuple_end is not None:
            tuple_end = tuple_end - len(reference)

        # tuple of typevars
        type_var_tuple_params = params[tuple_start:tuple_end]

        # if params might contain typevartuple args
        if len(params) > tuple_start:  # noqa: SIM102
            # if params[tuple_start] is *Ts keep it as-is
            if _is_unpacked_typevartuple(params[tuple_start]):
                type_var_tuple_params = params[tuple_start]

        # if starts with type var tuple
        if tuple_start == 0:
            # if there are type vars after it
            if tuple_end is not None:
                return (type_var_tuple_params, *params[tuple_end:])
            return (type_var_tuple_params,)
        # if it's at the end
        elif tuple_end is None:  # noqa: RET505
            return (*params[:tuple_start], type_var_tuple_params)
        # if it's in the middle
        return (*params[:tuple_start], type_var_tuple_params, *params[tuple_end:])
    return params


def _is_unpacked_typevartuple(x: Any) -> bool:
    return (not isinstance(x, type)) and getattr(x, '__typing_is_unpacked_typevartuple__', False)


def _is_typevar_like(x: Any) -> bool:
    return isinstance(x, (TypeVar, ParamSpec)) or _is_unpacked_typevartuple(x)


def _get_all_bases(cls):
    """Correctly obtains the bases for classes
    and typeddicts alike.
    """
    mro = reversed(cls.__mro__)

    if not is_typeddict(cls):
        yield from mro
        return

    traversing = list(mro)
    visited = []

    while traversing:
        base = traversing.pop(0)

        orig_bases = getattr(base, '__orig_bases__', ())
        mro_changed = False

        for orig_base in orig_bases:
            origin = get_origin(orig_base)

            if origin is not Generic:
                new_base = orig_base if origin is None else origin
                if new_base not in visited:
                    traversing.insert(0, new_base)
                    traversing.insert(1, base)
                    mro_changed = True

        if mro_changed:
            continue

        yield base

        visited.append(base)


def _track_parameter_changes(base):
    """Track how a parameters values are substituted
    or changed while traversing its bases.
    """
    orig_bases = getattr(base, '__orig_bases__', ())
    generic_encountered = False

    for orig_base in orig_bases:
        origin = get_origin(orig_base)
        if origin is None:
            continue

        args = get_args(orig_base)

        if origin is Generic:
            generic_encountered = True
            yield base, args
        else:
            yield origin, args

    # this occurs if obj is
    # class Bar(Foo[str, U]): ...
    # in this case, we need to imagine there's a generic base
    # with the required typevars here.
    if orig_bases and not generic_encountered:
        # we need to collect all the typevars from all bases
        # in the case that they have multiple generic bases
        # class Baz(Foo[str, U], Bar[U, T]): ...
        type_vars_for_generic = _collect_parameters(orig_bases)

        # this may be empty if obj is
        # class Bar(Foo[str]): ...
        # we can skip adding typevars here.
        if type_vars_for_generic:
            yield base, type_vars_for_generic


def _collect_parameters(args):
    """Collect all type variables and parameter specifications in args
    in order of first appearance (lexicographic order).

    For example::

        assert _collect_parameters((T, Callable[P, T])) == (T, P)
    """
    parameters = []
    for t in args:
        if isinstance(t, type):
            # We don't want __parameters__ descriptor of a bare Python class.
            pass
        elif isinstance(t, tuple):
            # `t` might be a tuple, when `ParamSpec` is substituted with
            # `[T, int]`, or `[int, *Ts]`, etc.
            for x in t:
                for collected in _collect_parameters([x]):
                    if collected not in parameters:
                        parameters.append(collected)
        elif hasattr(t, '__typing_subst__'):
            if t not in parameters:
                parameters.append(t)
        else:
            for x in getattr(t, '__parameters__', ()):
                if x not in parameters:
                    parameters.append(x)
    return tuple(parameters)


def _strip_annotations(t):
    """Strip the annotations from a given type."""
    if isinstance(t, _AnnotatedAlias):
        return _strip_annotations(t.__origin__)
    if hasattr(t, '__origin__') and t.__origin__ in (Required, NotRequired):
        return _strip_annotations(t.__args__[0])
    if isinstance(t, _GenericAlias):
        stripped_args = tuple(_strip_annotations(a) for a in t.__args__)
        if stripped_args == t.__args__:
            return t
        return t.copy_with(stripped_args)
    if isinstance(t, GenericAlias):
        stripped_args = tuple(_strip_annotations(a) for a in t.__args__)
        if stripped_args == t.__args__:
            return t
        return GenericAlias(t.__origin__, stripped_args)
    if hasattr(types, 'UnionType') and isinstance(t, types.UnionType):
        stripped_args = tuple(_strip_annotations(a) for a in t.__args__)
        if stripped_args == t.__args__:
            return t
        return functools.reduce(operator.or_, stripped_args)

    return t


# python 3.9 / 3.10 compatibility


def _typevar_subst(arg):
    msg = 'Parameters to generic types must be types.'
    arg = _type_check(arg, msg, is_argument=True)
    return arg
