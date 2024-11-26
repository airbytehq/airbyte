#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

# ....................{ TODO                               }....................
#FIXME: "typing.LiteralString". We just had a mildly brilliant revelation in
#the "beartype.claw._clawast" submodule as to how we might go about performing
#static analysis at runtime via the third-party "executing" submodule. \o/

#FIXME: [PEP 484]: Support subscripted bounded type variables. We didn't even
#know this was a thing -- but it makes sense. An example is probably the best
#way to explain this madness. Witness!
#    from beartype import beartype
#    from typing import Iterable
#    
#    T = TypeVar('T', bound=Iterable)
#    
#    @beartype
#    def stringify_iterable_items(arg: T[int]) -> T[str]:
#        return type(arg)(str(item) for item in arg)
#
#Clearly, @beartype should just quietly reduce both the "T[int]" and "T[str]"
#type hints that we can't really do anything with to "Iterable[int]" and
#"Iterable[str]" type hints, which we can. Does @beartype currently do that?
#Probably... not. At the least, we should begin testing this exhaustively.

#FIXME: [PEP 585] It looks like CPython's stdlib quietly extended PEP 585
#support to a variety of undocumented classes, including:
#* "asyncio.Future[T]".
#* "asyncio.Task[T]".
#* "asyncio.Queue[T]".
#* "pathlib.PathLike[T]".
#
#Yes, we can verify that *ALL* of those actually are subscriptable at runtime.
#@beartype will need to add corresponding support for such hints, beginning with
#defining new sign singletons suffixed by the same basenames (e.g.,
#"HintSignFuture", "HintSignTask"). Or... maybe not? Maybe everything just
#behaves as expected as is?
#
#At the least, we'll want to rigorously test *ALL* of the above in our test
#suite to ensure that @beartype does indeed type-check these as expected.
#FIXME: Sadly, we do need to explicitly do *SOMETHING*. @beartype currently
#raises exceptions on callables annotated by any of the above, as the metaclass
#of these hints prohibits isinstance() checks: e.g.,
#    asyncio.Task[~T] uncheckable at runtime (i.e., not passable as second
#    parameter to isinstance(), due to raising "isinstance() argument 2 cannot
#    be a parameterized generic" from metaclass __instancecheck__() method).
#
#Rather than explicitly matching all of the above, we instead want @beartype to
#perform an automated solution implicitly matching all of the above. Notably,
#improve @beartype to:
#
#* Detect parametrized generic hints that are otherwise unrecognized (e.g.,
#  "asyncio.Task[~T]"). 
#* Introspect the origin (i.e., "__origin__" dunder attribute) from these hints.
#* Internally replace each such parametrized generic hint with its origin when
#  generating type-checking code. Voila!

#FIXME: [PEP] Add PEP 613 support (i.e., "typing.TypeAlias"). Thankfully, this
#is trivial. "typing.TypeAlias" is prohibited in callable definitions and
#inside the bodies of callables. Ergo, @beartype should just raise a
#decoration-time exception if any parameter or return is annotated as an
#explicit "TypeAlias". That constitutes full support for PEP 613 from our
#side. Good enough! :p

#FIXME: [SPEED] As a useful MACROoptimization, render the entire @beartype
#toolchain thread-safe upfront rather than doing so piecemeal throughout the
#toolchain. While the latter certainly works as well, the former is
#*SUBSTANTIALLY* more efficient due to the non-trivial expense of each
#threadsafe context manager. To do so:
#* Simply wrap the body of the implementation of the @beartype decorator in a
#  context manager locking on a globally declared lock: e.g.,
#      with lock:
#          ...
#  Note that an "RLock" is neither needed nor desired here, as @beartype
#  *NEVER* invokes itself recursively. A non-reentrant "Lock" suffices.
#* Rip out all now-redundant "with lock:" expressions throughout the codebase.

#FIXME: [SPEED] As a useful microoptimization, consider memoizing "repr(hint)"
#calls. We strongly suspect these calls to be a performance bottleneck, because
#we repeat them so frequently for the same hint throughout the codebase. The
#best approach to doing so is to:
#* Define a new memoized "beartype._util.hint.utilhintget" getter: e.g.,
#      @callable_cached
#      def get_hint_repr(hint: object) -> str:
#          return repr(hint)
#* Globally replace all calls to the repr() builtin throughout the codebase
#  passed a hint with calls to get_hint_repr() instead.

#FIXME: [SPEED] As a useful microoptimization, unroll *ALL* calls to the any()
#and all() builtins into equivalent "for" loops in our critical path. Since we
#typically pass these builtins generator comprehensions created and destroyed
#on-the-fly, we've profiled these builtins to incur substantially higher
#runtime costs than equivalent "for" loops. Thanks alot, CPython. *sigh*

#FIXME: [FEATURE] Plugin architecture. The NumPy type hints use case will come
#up again and again. So, let's get out ahead of that use case rather than
#continuing to reinvent the wheel. Let's begin by defining a trivial plugin API
#enabling users to define their own arbitrary type hint *REDUCTIONS.* Because
#it's capitalized, we know the term "REDUCTIONS" is critical here. We are *NOT*
#(at least, *NOT* initially) defining a full-blown plugin API. We're only
#enabling users to reduce arbitrary type hints:
#* From domain-specific objects they implement and annotate their code with...
#* Into PEP-compliant type hints @beartype already supports.
#Due to their versatility, the standard use case is reducing PEP-noncompliant
#type hints to PEP 593-compliant beartype validators. To do so, consider:
#* Defining a new public "beartype.plug" subpackage, defining:
#  * A private "_PLUGIN_NAME_TO_SIGN" dictionary mapping from each "name"
#    parameter passed to each prior call of the plug_beartype() function to the
#    "HintSign" object that function dynamically creates to represent
#    PEP-noncompliant type hints handled by that plugin. This dictionary
#    effectively maps from the thing our users care about but we don't (i.e.,
#    plugin names) to the thing our users don't care about but we do (i.e.,
#    hint signs).
#  * A public plug_beartype() function with signature resembling:
#       def plug_beartype(
#           # Mandatory parameters.
#           name: str,
#           hint_reduce: Callable[[object,], object],
#
#           # Optional parameters.
#           hint_detect_from_repr_prefix_args_1_or_more: Optional[str] = None,
#           hint_detect_from_type_name: Optional[str] = None,
#       ) -> None:
#    ...where:
#    * The "name" parameter is an arbitrary non-empty string (e.g., "Numpy").
#      This function will then synthesize a new hint sign suffixed by this
#      substring (e.g., f'HintSign{name}') and map this name to that sign in
#      the "_PLUGIN_NAME_TO_SIGN" dictionary.
#    * The "hint_detect_from_repr_prefix_args_1_or_more" parameter is an
#      arbitrary non-empty string typically corresponding to the
#      fully-qualified name of a subclass of "types.GenericAlias" serving as a
#      PEP 585-compliant type hint factory(e.g.,
#      "muh_package.MuhTypeHintFactory"), corresponding exactly to the items
#      of the "HINT_REPR_PREFIX_ARGS_1_OR_MORE_TO_SIGN" set.
#    * The "hint_detect_from_type_name" parameter is the fully-qualified name
#      of a caller-defined class (e.g., "muh_package.MuhTypeHintFactoryType"),
#      corresponding exactly to the items of the "HINT_TYPE_NAME_TO_SIGN" set.
#    * The "hint_reduce" parameter is an arbitrary caller-defined callable
#      reducing all type hints identified by one or more of the detection
#      schemes below to another arbitrary (but hopefully PEP-compliant and
#      beartype-supported) type hint. Again, that will typically be a
#      PEP 593-compliant beartype validator.
#  * A public unplug_beartype() function with signature resembling:
#       def unplug_beartype(name: str) -> None:
#    This function simply looks up the passed name in various internal data
#    structures (e.g.,"_PLUGIN_NAME_TO_SIGN") to undo the effects of the prior
#    plug_beartype() call passed that name.
#
#Given that, we should then entirely reimplement our current strategy for
#handling NumPy type hints into a single call to plug_beartype(): e.g.,
#    # Pretty boss, ain't it? Note we intentionally pass
#    # "hint_detect_from_repr_prefix_args_1_or_more" here, despite the fact
#    # that the unsubscripted "numpy.typing.NDArray" factory is a valid type
#    # hint. Yes, this actually works. Why? Because that factory implicitly
#    # subscripts itself when unsubscripted. In other words, there is *NO* such
#    # thing as an unsubscripted typed NumPy array. O_o
#    def plug_beartype(
#        name='NumpyArray',
#        hint_reduce=reduce_hint_numpy_ndarray,
#        hint_detect_from_repr_prefix_args_1_or_more='numpy.ndarray',
#    )
#
#Yes, this would then permit us to break backward compatibility by bundling
#that logic into a new external "beartype_numpy" plugin for @beartype -- but we
#absolutely should *NOT* do that, both because it would severely break backward
#compatibility *AND* because everyone (including us) wants NumPy support
#out-of-the-box. We're all data scientists here. Do the right thing.

#FIXME: [FEATURE] Define the following supplementary decorators:
#* @beartype.beartype_O1(), identical to the current @beartype.beartype()
#  decorator but provided for disambiguity. This decorator only type-checks
#  exactly one item from each container for each call rather than all items.
#* @beartype.beartype_Ologn(), type-checking log(n) random items from each
#  container of "n" items for each call.
#* @beartype.beartype_On(), type-checking all items from each container for
#  each call. We have various ideas littered about GitHub on how to optimize
#  this for various conditions, but this is never going to be ideal and should
#  thus never be the default.
#
#To differentiate between these three strategies, consider:
#* Declare an enumeration in "beartype._check.checkcall" resembling:
#    from enum import Enum
#    BeartypeStrategyKind = Enum('BeartypeStrategyKind ('O1', 'Ologn', 'On',))
#* Define a new "BeartypeCall.strategy_kind" instance variable.
#* Set this variable to the corresponding "BeartypeStrategyKind" enumeration
#  member based on which of the three decorators listed above was called.
#* Explicitly pass the value of the "BeartypeCall.strategy_kind" instance
#  variable to the beartype._check.code.codemake.make_func_wrapper_code()
#  function as a new memoized "strategy_kind" parameter.
#* Conditionally generate type-checking code throughout that function depending
#  on the value of that parameter.

#FIXME: Emit one non-fatal warning for each annotated type that is either:
#
#* "beartype.cave.UnavailableType".
#* "beartype.cave.UnavailableTypes".
#
#Both cases imply user-side misconfiguration, but not sufficiently awful enough
#to warrant fatal exceptions. Moreover, emitting warnings rather than
#exceptions enables end users to unconditionally disable all unwanted warnings,
#whereas no such facilities exist for unwanted exceptions.
#FIXME: Validate all tuple annotations to be non-empty *EXCLUDING*
#"beartype.cave.UnavailableTypes", which is intentionally empty.
#FIXME: Unit test the above edge case.

#FIXME: Add support for all possible kinds of parameters. @beartype currently
#supports most but *NOT* all types. Specifically:
#
#* Type-check variadic keyword arguments. Currently, only variadic positional
#  arguments are type-checked. When doing so, remove the
#  "Parameter.VAR_KEYWORD" type from the "_PARAM_KIND_IGNORABLE" set.
#* Type-check positional-only arguments under Python >= 3.8. Note that, since
#  C-based callables have *ALWAYS* supported positional-only arguments, the
#  "Parameter.POSITIONAL_ONLY" type is defined for *ALL* Python versions
#  despite only being usable in actual Python from Python >= 3.8. In other
#  words, support for type-checking positional-only arguments should be added
#  unconditionally without reference to Python version -- we suspect, anyway.
#  When doing so, remove the "Parameter.POSITIONAL_ONLY" type from the
#  "_PARAM_KIND_IGNORABLE" set.
#* Remove the "_PARAM_KIND_IGNORABLE" set entirely.
