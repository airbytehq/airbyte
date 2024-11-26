#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype cave.**

This submodule collects common types (e.g., :class:`NoneType`, the type of the
``None`` singleton) and tuples of common types (e.g., :data:`CallableTypes`, a
tuple of the types of all callable objects).

PEP 484
----------
This module is intentionally *not* compliant with the :pep:`484` standard
implemented by the stdlib :mod:`typing` module, which formalizes type hinting
annotations with a catalogue of generic classes and metaclasses applicable to
common use cases. :mod:`typing` enables end users to enforce contractual
guarantees over the contents of arbitrarily complex data structures with the
assistance of third-party static type checkers (e.g., :mod:`mypy`,
:mod:`pyre`), runtime type checkers (e.g., :mod:`beartype`, :mod:`typeguard`),
and integrated development environments (e.g., PyCharm).

Genericity comes at a cost, though. Deeply type checking a container containing
``n`` items, for example, requires type checking both that container itself
non-recursively *and* each item in that container recursively. Doing so has
time complexity ``O(N)`` for ``N >= n`` the total number of items transitively
contained in this container (i.e., items directly contained in this container
*and* items directly contained in containers contained in this container).
While the cost of this operation can be paid either statically *or* amortized
at runtime over all calls to annotated callables accepting that container, the
underlying cost itself remains the same.

By compare, this module only contains standard Python classes and tuples of
such classes intended to be passed as is to the C-based :func:`isinstance`
builtin and APIs expressed in terms of that builtin (e.g., :mod:`beartype`).
This module only enables end users to enforce contractual guarantees over the
types but *not* contents of arbitrarily complex data structures. This
intentional tradeoff maximizes runtime performance at a cost of ignoring the
types of items contained in containers.

In summary:

=====================  ====================  ====================================
feature set            :mod:`beartype.cave`  :mod:`typing`
=====================  ====================  ====================================
type checking          **shallow**           **deep**
type check items?      **no**                **yes**
:pep:`484`-compliant?  **no**                **yes**
time complexity        ``O(1)``              ``O(N)``
performance            stupid fast           *much* less stupid fast
implementation         C-based builtin call  pure-Python (meta)class method calls
low-level primitive    :func:`isinstance`    :mod:`typing.TypingMeta`
=====================  ====================  ====================================
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: *NEVER IMPORT FROM THIS SUBPACKAGE FROM WITHIN BEARTYPE ITSELF.*
# This subpackage currently imports from expensive third-party packages on
# importation (e.g., NumPy) despite beartype itself *NEVER* requiring those
# imports. Until resolved, this subpackage is considered tainted.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To prevent "mypy --no-implicit-reexport" from raising literally
# hundreds of errors at static analysis time, *ALL* public attributes *MUST* be
# explicitly reimported under the same names with "{exception_name} as
# {exception_name}" syntax rather than merely "{exception_name}". Yes, this is
# ludicrous. Yes, this is mypy. For posterity, these failures resemble:
#     beartype/_cave/_cavefast.py:47: error: Module "beartype.roar" does not
#     explicitly export attribute "BeartypeCallUnavailableTypeException";
#     implicit reexport disabled  [attr-defined]
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To avoid polluting the public module namespace, external attributes
# should be locally imported at module scope *ONLY* under alternate private
# names (e.g., "from argparse import ArgumentParser as _ArgumentParser" rather
# than merely "from argparse import ArgumentParser").
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

from beartype.cave._cavelib import (
    # Types.
    ArgParserType as ArgParserType,
    ArgSubparsersType as ArgSubparsersType,
    WeakRefCType as WeakRefCType,

    # Type tuples.
    WeakRefProxyCTypes as WeakRefProxyCTypes,
)
from beartype._cave._caveabc import (
    BoolType as BoolType,
)
from beartype._cave._cavefast import (
    # Types.
    AnyType as AnyType,
    AsyncCoroutineCType as AsyncCoroutineCType,
    AsyncGeneratorCType as AsyncGeneratorCType,
    CallableCodeObjectType as CallableCodeObjectType,
    ClassDictType as ClassDictType,
    CallableFrameType as CallableFrameType,
    CallablePartialType as CallablePartialType,
    ClassType as ClassType,
    ClosureVarCellType as ClosureVarCellType,
    CollectionType as CollectionType,
    ContainerType as ContainerType,
    EllipsisType as EllipsisType,
    EnumType as EnumType,
    EnumMemberType as EnumMemberType,
    ExceptionTracebackType as ExceptionTracebackType,
    FileType as FileType,
    FunctionType as FunctionType,
    FunctionOrMethodCType as FunctionOrMethodCType,
    GeneratorCType as GeneratorCType,
    GeneratorType as GeneratorType,
    HashableType as HashableType,
    HintGenericSubscriptedType as HintGenericSubscriptedType,
    IntOrFloatType as IntOrFloatType,
    IntType as IntType,
    IterableType as IterableType,
    IteratorType as IteratorType,
    MappingMutableType as MappingMutableType,
    MappingType as MappingType,
    MethodBoundInstanceDunderCType as MethodBoundInstanceDunderCType,
    MethodBoundInstanceOrClassType as MethodBoundInstanceOrClassType,
    MethodDecoratorClassType as MethodDecoratorClassType,
    MethodDecoratorPropertyType as MethodDecoratorPropertyType,
    MethodDecoratorStaticType as MethodDecoratorStaticType,
    MethodUnboundClassCType as MethodUnboundClassCType,
    MethodUnboundInstanceDunderCType as MethodUnboundInstanceDunderCType,
    MethodUnboundInstanceNondunderCType as MethodUnboundInstanceNondunderCType,
    MethodUnboundPropertyNontrivialCExtensionType as
        MethodUnboundPropertyNontrivialCExtensionType,
    MethodUnboundPropertyTrivialCExtensionType as
        MethodUnboundPropertyTrivialCExtensionType,
    ModuleType as ModuleType,
    NoneType as NoneType,
    NotImplementedType as NotImplementedType,
    NumberRealType as NumberRealType,
    NumberType as NumberType,
    SizedType as SizedType,
    QueueType as QueueType,
    RegexCompiledType as RegexCompiledType,
    RegexMatchType as RegexMatchType,
    SetType as SetType,
    SequenceMutableType as SequenceMutableType,
    SequenceType as SequenceType,
    StrType as StrType,
    UnavailableType as UnavailableType,

    # Type tuples.
    AsyncCTypes as AsyncCTypes,
    BoolOrNumberTypes as BoolOrNumberTypes,
    CallableCTypes as CallableCTypes,
    CallableOrClassTypes as CallableOrClassTypes,
    CallableOrStrTypes as CallableOrStrTypes,
    CallableTypes as CallableTypes,
    DecoratorTypes as DecoratorTypes,
    FunctionTypes as FunctionTypes,
    ModuleOrStrTypes as ModuleOrStrTypes,
    MethodBoundTypes as MethodBoundTypes,
    MethodDecoratorBuiltinTypes as MethodDecoratorBuiltinTypes,
    MethodUnboundTypes as MethodUnboundTypes,
    MethodTypes as MethodTypes,
    MappingOrSequenceTypes as MappingOrSequenceTypes,
    ModuleOrSequenceTypes as ModuleOrSequenceTypes,
    NumberOrIterableTypes as NumberOrIterableTypes,
    NumberOrSequenceTypes as NumberOrSequenceTypes,
    RegexTypes as RegexTypes,
    ScalarTypes as ScalarTypes,
    TestableTypes as TestableTypes,
    UnavailableTypes as UnavailableTypes,
)
from beartype._cave._cavemap import (
    NoneTypeOr as NoneTypeOr,
)

# ....................{ DEPRECATIONS                       }....................
def __getattr__(attr_deprecated_name: str) -> object:
    '''
    Dynamically retrieve a deprecated attribute with the passed unqualified
    name from this submodule and emit a non-fatal deprecation warning on each
    such retrieval if this submodule defines this attribute *or* raise an
    exception otherwise.

    The Python interpreter implicitly calls this :pep:`562`-compliant module
    dunder function under Python >= 3.7 *after* failing to directly retrieve an
    explicit attribute with this name from this submodule. Since this dunder
    function is only called in the event of an error, neither space nor time
    efficiency are a concern here.

    Parameters
    ----------
    attr_deprecated_name : str
        Unqualified name of the deprecated attribute to be retrieved.

    Returns
    ----------
    object
        Value of this deprecated attribute.

    Warns
    ----------
    :class:`DeprecationWarning`
        If this attribute is deprecated.

    Raises
    ----------
    :exc:`AttributeError`
        If this attribute is unrecognized and thus erroneous.
    '''

    # Isolate imports to avoid polluting the module namespace.
    from beartype._util.module.utilmoddeprecate import deprecate_module_attr

    # Return the value of this deprecated attribute and emit a warning.
    return deprecate_module_attr(
        attr_deprecated_name=attr_deprecated_name,
        attr_deprecated_name_to_nondeprecated_name={
            'HintPep585Type': 'HintGenericSubscriptedType',
        },
        attr_nondeprecated_name_to_value=globals(),
    )
