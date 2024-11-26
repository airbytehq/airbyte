#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **Python version-agnostic signs** (i.e., instances of the
:class:`beartype._data.hint.pep.sign.datapepsigncls.HintSign` class
uniquely identifying PEP-compliant type hints in a safe, non-deprecated manner
regardless of the Python version targeted by the active Python interpreter).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: Attributes imported here at module scope *MUST* be explicitly
# deleted from this module's namespace below.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype._data.hint.pep.sign.datapepsigncls import HintSign as _HintSign

# ....................{ SIGNS ~ explicit                   }....................
# Signs with explicit analogues in the stdlib "typing" module.
#
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: Signs defined by this module are synchronized with the "__all__"
# list global of the "typing" module bundled with the most recent CPython
# release. For that reason, these signs are:
# * Intentionally declared in the exact same order prefixed by the exact same
#   inline comments as for that list global.
# * Intentionally *NOT* commented with docstrings, both because:
#   * These docstrings would all trivially reduce to a single-line sentence
#     fragment resembling "Alias of typing attribute."
#   * These docstrings would inhibit diffing and synchronization by inspection.
# * Intentionally *NOT* conditionally isolated to the specific range of Python
#   versions whose "typing" module lists these attributes. For example, the
#   "HintSignAsyncContextManager" sign identifying the
#   "typing.AsyncContextManager" attribute that only exists under Python >=
#   3.7 could be conditionally isolated to that range of Python versions.
#   Technically, there exists *NO* impediment to doing so; pragmatically, doing
#   so would be ineffectual. Why? Because attributes *NOT* defined by the
#   "typing" module of the active Python interpreter cannot (by definition) be
#   used to annotate callables decorated by the @beartype decorator.
#
# When bumping beartype to support a new CPython release:
# * Declare one new attribute here for each new "typing" attribute added by
#   that CPython release regardless of whether beartype explicitly supports
#   that attribute yet. The subsequently called die_unless_hint_pep_supported()
#   validator will raise exceptions when passed these attributes.
# * Preserve attributes here that have since been removed from the "typing"
#   module in that CPython release to ensure their continued usability when
#   running beartype against older CPython releases.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# Super-special typing primitives.
HintSignAnnotated = _HintSign(name='Annotated')
HintSignAny = _HintSign(name='Any')
HintSignCallable = _HintSign(name='Callable')
HintSignClassVar = _HintSign(name='ClassVar')
HintSignConcatenate = _HintSign(name='Concatenate')
HintSignFinal = _HintSign(name='Final')
HintSignForwardRef = _HintSign(name='ForwardRef')
HintSignGeneric = _HintSign(name='Generic')
HintSignLiteral = _HintSign(name='Literal')
HintSignOptional = _HintSign(name='Optional')
HintSignParamSpec = _HintSign(name='ParamSpec')
HintSignProtocol = _HintSign(name='Protocol')
HintSignTuple = _HintSign(name='Tuple')
HintSignType = _HintSign(name='Type')
HintSignTypeVar = _HintSign(name='TypeVar')
HintSignTypeVarTuple = _HintSign(name='TypeVarTuple')
HintSignUnion = _HintSign(name='Union')

# ABCs (from collections.abc).
HintSignAbstractSet = _HintSign(name='AbstractSet')
HintSignByteString = _HintSign(name='ByteString')
HintSignContainer = _HintSign(name='Container')
HintSignContextManager = _HintSign(name='ContextManager')
HintSignHashable = _HintSign(name='Hashable')
HintSignItemsView = _HintSign(name='ItemsView')
HintSignIterable = _HintSign(name='Iterable')
HintSignIterator = _HintSign(name='Iterator')
HintSignKeysView = _HintSign(name='KeysView')
HintSignMapping = _HintSign(name='Mapping')
HintSignMappingView = _HintSign(name='MappingView')
HintSignMutableMapping = _HintSign(name='MutableMapping')
HintSignMutableSequence = _HintSign(name='MutableSequence')
HintSignMutableSet = _HintSign(name='MutableSet')
HintSignSequence = _HintSign(name='Sequence')
HintSignSized = _HintSign(name='Sized')
HintSignValuesView = _HintSign(name='ValuesView')
HintSignAwaitable = _HintSign(name='Awaitable')
HintSignAsyncIterator = _HintSign(name='Iterator')
HintSignAsyncIterable = _HintSign(name='Iterable')
HintSignCoroutine = _HintSign(name='Coroutine')
HintSignCollection = _HintSign(name='Collection')
HintSignAsyncGenerator = _HintSign(name='AsyncGenerator')
HintSignAsyncContextManager = _HintSign(name='ContextManager')

# Structural checks, a.k.a. protocols.
HintSignReversible = _HintSign(name='Reversible')
# SupportsAbs   <-- not a useful type hint (already an isinstanceable ABC)
# SupportsBytes   <-- not a useful type hint (already an isinstanceable ABC)
# SupportsComplex   <-- not a useful type hint (already an isinstanceable ABC)
# SupportsFloat   <-- not a useful type hint (already an isinstanceable ABC)
# SupportsIndex   <-- not a useful type hint (already an isinstanceable ABC)
# SupportsInt   <-- not a useful type hint (already an isinstanceable ABC)
# SupportsRound   <-- not a useful type hint (already an isinstanceable ABC)

# Concrete collection types.
HintSignChainMap = _HintSign(name='ChainMap')
HintSignCounter = _HintSign(name='Counter')
HintSignDeque = _HintSign(name='Deque')
HintSignDict = _HintSign(name='Dict')
HintSignDefaultDict = _HintSign(name='DefaultDict')
HintSignList = _HintSign(name='List')
HintSignOrderedDict = _HintSign(name='OrderedDict')
HintSignSet = _HintSign(name='Set')
HintSignFrozenSet = _HintSign(name='FrozenSet')
HintSignNamedTuple = _HintSign(name='NamedTuple')
HintSignTypedDict = _HintSign(name='TypedDict')
HintSignGenerator = _HintSign(name='Generator')

# Other concrete types.
HintSignMatch = _HintSign(name='Match')
HintSignPattern = _HintSign(name='Pattern')

# Other concrete type aliases.
HintSignIO = HintSignGeneric
HintSignBinaryIO = HintSignGeneric
HintSignTextIO = HintSignGeneric

# One-off things.
# AnyStr   <-- not a unique type hint (just a constrained "TypeVar")
# cast   <-- unusable as a type hint
# final   <-- unusable as a type hint
# get_args   <-- unusable as a type hint
# get_origin   <-- unusable as a type hint
# get_type_hints   <-- unusable as a type hint
# is_typeddict   <-- unusable as a type hint
HintSignLiteralString = _HintSign(name='LiteralString')
HintSignNever = _HintSign(name='Never')
HintSignNewType = _HintSign(name='NewType')
# no_type_check   <-- unusable as a type hint
# no_type_check_decorator   <-- unusable as a type hint

# Note that "NoReturn" is contextually valid *ONLY* as a top-level return hint.
# Since this use case is extremely limited, we explicitly generate code for this
# use case outside of the general-purpose code generation pathway for standard
# type hints. Since "NoReturn" is an unsubscriptable singleton, we explicitly
# detect this type hint with an identity test and thus require *NO* sign to
# uniquely identify this type hint.
#
# Theoretically, explicitly defining a sign uniquely identifying this type hint
# could erroneously encourage us to use that sign elsewhere; we should avoid
# that, as "NoReturn" is invalid in almost all possible contexts. Pragmatically,
# doing so nonetheless improves orthogonality when detecting and validating
# PEP-compliant type hints, which ultimately matters more than our subjective
# feelings about the matter. Wisely, we choose pragmatics.
#
# In short, "NoReturn" is insane.
HintSignNoReturn = _HintSign(name='NoReturn')

HintSignNotRequired = _HintSign(name='NotRequired')
# overload   <-- unusable as a type hint
HintSignParamSpecArgs = _HintSign(name='ParamSpecArgs')
HintSignParamSpecKwargs = _HintSign(name='ParamSpecKwargs')
HintSignRequired = _HintSign(name='Required')
# runtime_checkable   <-- unusable as a type hint
HintSignSelf = _HintSign(name='Self')
# Text   <-- not actually a type hint (literal alias for "str")
# TYPE_CHECKING   <-- unusable as a type hint
HintSignTypeAlias = _HintSign(name='TypeAlias')
HintSignTypeGuard = _HintSign(name='TypeGuard')
HintSignUnpack = _HintSign(name='Unpack')

# Wrapper namespace for re type aliases.
#
# Note that "typing.__all__" intentionally omits the "Match" and "Pattern"
# attributes, which it oddly considers to comprise another namespace. *shrug*

# ....................{ SIGNS ~ implicit                   }....................
# Signs with *NO* explicit analogues in the stdlib "typing" module but
# nonetheless standardized by one or more PEPs.

# PEP 484 explicitly supports the "None" singleton, albeit implicitly:
#     When used in a type hint, the expression None is considered equivalent to
#     type(None).
HintSignNone = _HintSign(name='None')

# PEP 557 defines the "dataclasses.InitVar" type hint factory for annotating
# class-scoped variable annotations of @dataclass.dataclass-decorated classes.
HintSignDataclassInitVar = _HintSign(name='DataclassInitVar')

# ....................{ SIGNS ~ implicit : lib             }....................
# Signs identifying PEP-noncompliant third-party type hints published by...
#
# ....................{ SIGNS ~ implicit : lib : numpy     }....................
# ...the "numpy.typing" subpackage.
HintSignNumpyArray = _HintSign(name='NumpyArray')   # <-- "numpy.typing.NDArray"

# ....................{ SIGNS ~ implicit : lib : pandera   }....................
# ...the "pandera.typing" subpackage. Specifically, define a single sign
# unconditionally matching *ALL* type hints published by the "pandera.typing"
# subpackage. Why? Because Pandera insanely publishes its own Pandera-specific
# PEP-noncompliant runtime type-checking decorator @pandera.check_types() that
# supports *ONLY* Pandera-specific PEP-noncompliant "pandera.typing" type hints.
# Since Pandera users are already accustomed to decorating *ALL* Pandera-based
# callables (i.e., callables accepting one or more parameters and/or returning
# one or more values which are Pandera objects) by @pandera.check_types(),
# attempting to type-check the same objects already type-checked by that
# decorator would only inefficiently and needlessly slow @beartype down. Ergo,
# we ignore *ALL* Pandera type hints by:
# * Defining this catch-all singleton for Pandera type hints here.
# * Denoting this singleton to be unconditionally ignorable elsewhere.
HintSignPanderaAny = _HintSign(name='PanderaAny')   # <-- "pandera.typing.*"

#FIXME: Excise us up, please.
# HintSignPanderaAny = HintSignGeneric

# ....................{ CLEANUP                            }....................
# Prevent all attributes imported above from polluting this namespace. Why?
# Logic elsewhere subsequently assumes a one-to-one mapping between the
# attributes of this namespace and signs.
del _HintSign
